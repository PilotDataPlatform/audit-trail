# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
from typing import Optional

from common import LoggerFactory
from fastapi import APIRouter
from fastapi_utils import cbv

from app.models.base_models import APIResponse
from app.models.base_models import EAPIResponseCode
from app.models.models_file_meta import FileMetaCreation
from app.models.models_file_meta import FileMetaUpdate
from app.resources.error_handler import catch_internal
from app.resources.es_helper import file_search
from app.resources.es_helper import insert_one_by_id
from app.resources.es_helper import update_one_by_id

router = APIRouter()

_API_TAG = 'File Entity'
_API_NAMESPACE = 'api_file_entity'

ES_INDEX = 'files'


@cbv.cbv(router)
class APIAuditLog:
    def __init__(self):
        self.__logger = LoggerFactory('api_file_entity').get_logger()

    @router.post('/entity/file', tags=[_API_TAG], summary='Create a file entity in elastic search')
    @catch_internal(_API_NAMESPACE)
    async def file_meta_creation(self, request_payload: FileMetaCreation):
        response = APIResponse()

        self.__logger.info(f'file creation payload: {str(request_payload)}')

        global_entity_id = request_payload.global_entity_id
        zone = request_payload.zone
        data_type = request_payload.data_type
        operator = request_payload.operator
        tags = request_payload.tags
        archived = request_payload.archived
        location = request_payload.location
        time_lastmodified = request_payload.time_lastmodified
        time_created = request_payload.time_created
        process_pipeline = request_payload.process_pipeline
        uploader = request_payload.uploader
        file_name = request_payload.file_name
        file_size = request_payload.file_size
        atlas_guid = request_payload.atlas_guid
        display_path = request_payload.display_path
        dcm_id = request_payload.dcm_id
        attributes = request_payload.attributes
        project_code = request_payload.project_code
        priority = request_payload.priority
        version = request_payload.version

        self.__logger.info(f'Project of File Meta Creation: {project_code}')

        data = {
            'zone': zone,
            'data_type': data_type,
            'operator': operator,
            'tags': tags,
            'archived': archived,
            'location': location,
            'time_lastmodified': time_lastmodified,
            'time_created': time_created,
            'process_pipeline': process_pipeline,
            'uploader': uploader,
            'file_name': file_name,
            'file_size': file_size,
            'atlas_guid': atlas_guid,
            'display_path': display_path,
            'dcm_id': dcm_id,
            'attributes': attributes,
            'project_code': project_code,
            'priority': priority,
            'version': version,
        }

        res = await insert_one_by_id('_doc', ES_INDEX, data, global_entity_id)

        if res['result'] == 'created':
            self.__logger.info('Result of Filemeta Creation: Success')
            response.code = EAPIResponseCode.success
            response.result = res
        else:
            self.__logger.error('Result of Filemeta Creation: Failed')
            response.code = EAPIResponseCode.internal_error
            response.result = 'faied to insert Filemeta into elastic search, {}'.format(res)

        return response

    @router.get('/entity/file', tags=[_API_TAG], summary='Search file entities in elastic search')
    @catch_internal(_API_NAMESPACE)
    async def file_meta_query(  # noqa: C901
        self,
        query: str,
        page: Optional[int] = 0,
        page_size: Optional[int] = 10,
        sort_by: Optional[str] = 'time_created',
        sort_type: Optional[str] = 'desc',
    ):
        response = APIResponse()
        queries = json.loads(query)

        search_params = []

        for key in queries:
            if key == 'attributes':
                filed_params = {
                    'nested': True,
                    'field': 'attributes',
                    'range': False,
                    'name': queries['attributes']['name'],
                    'multi_values': False,
                }

                search_params.append(filed_params)

                if 'attributes' in queries['attributes']:
                    for record in queries['attributes']['attributes']:
                        filed_params = {
                            'nested': True,
                            'field': 'attributes',
                            'range': False,
                            'name': queries['attributes']['name'],
                            'multi_values': False,
                        }

                        filed_params['attribute_name'] = record['attribute_name']

                        if record['type'] == 'text':
                            if record['condition'] == 'contain':
                                filed_params['value'] = '*{}*'.format(record['value'])
                                filed_params['search_type'] = 'wildcard'
                            else:
                                filed_params['value'] = record['value']
                                filed_params['search_type'] = 'match'
                        else:
                            if record['condition'] == 'contain':
                                filed_params['search_type'] = 'should'
                            else:
                                filed_params['search_type'] = 'must'

                            filed_params['value'] = record['value']
                            filed_params['multi_values'] = True

                        search_params.append(filed_params)

            elif key == 'time_created' or key == 'file_size':
                filed_params = {
                    'nested': False,
                    'field': key,
                    'range': queries[key]['value'],
                    'multi_values': False,
                    'search_type': queries[key]['condition'],
                }
                search_params.append(filed_params)
            elif key == 'tags':
                filed_params = {'nested': False, 'field': key, 'range': False, 'multi_values': True}
                if queries['tags']['condition'] == 'contain':
                    filed_params['search_type'] = 'should'
                else:
                    filed_params['search_type'] = 'must'
                filed_params['value'] = queries['tags']['value']
                search_params.append(filed_params)
            else:
                filed_params = {
                    'nested': False,
                    'field': key,
                    'range': False,
                    'multi_values': False,
                    'value': queries[key]['value'],
                    'search_type': queries[key]['condition'],
                }
                search_params.append(filed_params)
        res = await file_search(ES_INDEX, page, page_size, search_params, sort_by, sort_type)
        self.__logger.info(f'Response is: {res}')
        response.code = EAPIResponseCode.success
        response.result = res['hits']['hits']
        response.total = res['hits']['total']['value']
        return response

    @router.put('/entity/file', tags=[_API_TAG], summary='Update a file entity in elastic search')
    @catch_internal(_API_NAMESPACE)
    async def file_meta_update(self, request_payload: FileMetaUpdate):
        response = APIResponse()

        global_entity_id = request_payload.global_entity_id
        updated_fields = request_payload.updated_fields

        if 'time_lastmodified' in updated_fields:
            updated_fields['time_lastmodified'] = int(updated_fields['time_lastmodified'])

        res = await update_one_by_id(ES_INDEX, global_entity_id, updated_fields)
        self.__logger.debug(f'UPdate response is:{res}')

        if res.get('result') == 'updated' or res.get('result') == 'noop':
            res.update({'result': 'updated'})
            self.__logger.debug('Result of Filemeta Update: Success')
            response.code = EAPIResponseCode.success
            response.result = res
        else:
            self.__logger.debug('Result of Filemeta Update: Failed')
            response.code = EAPIResponseCode.internal_error
            response.result = 'Faied to Update Filemeta in elastic search'

        return response.json_response()
