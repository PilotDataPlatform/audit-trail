import time
from datetime import datetime, timedelta
import requests
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi_utils import cbv
import json
from ...resources.error_handler import catch_internal
from ...resources.es_helper import exact_search, insert_one_by_id, get_mappings, file_search, update_one_by_id
from ...models.models_file_meta import FileMetaCreation, FileMetaUpdate
from ...models.base_models import APIResponse, EAPIResponseCode
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...config import ConfigClass

router = APIRouter()

_API_TAG = 'File Entity'
_API_NAMESPACE = "api_file_entity"

ES_INDEX = 'files'


@cbv.cbv(router)
class APIAuditLog:
    def __init__(self):
        self.__logger = SrvLoggerFactory('api_file_entity').get_logger()

    @router.post("/entity/file", tags=[_API_TAG],
                 summary="Create a file entity in elastic search")
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

        self.__logger.info(
            'Project of File Meta Creation: {}'.format(project_code))

        data = {
            "zone": zone,
            "data_type": data_type,
            "operator": operator,
            "tags": tags,
            "archived": archived,
            "location": location,
            "time_lastmodified": time_lastmodified,
            "time_created": time_created,
            "process_pipeline": process_pipeline,
            "uploader": uploader,
            "file_name": file_name,
            "file_size": file_size,
            "atlas_guid": atlas_guid,
            "display_path": display_path,
            "dcm_id": dcm_id,
            "attributes": attributes,
            "project_code": project_code,
            "priority": priority,
            "version": version
        }

        res = insert_one_by_id('_doc', ES_INDEX, data, global_entity_id)

        if res['result'] == 'created':
            self.__logger.info('Result of Filemeta Creation: Success')
            response.code = EAPIResponseCode.success
            response.result = res
        else:
            self.__logger.error('Result of Filemeta Creation: Failed')
            response.code = EAPIResponseCode.internal_error
            response.result = 'faied to insert Filemeta into elastic search, {}'.format(
                res)

        return response

    @router.get("/entity/file", tags=[_API_TAG],
                summary="Search file entities in elastic search")
    @catch_internal(_API_NAMESPACE)
    async def file_meta_query(
        self,
        query: str,
        page: Optional[int] = 0,
        page_size: Optional[int] = 10,
        sort_by: Optional[str] = 'time_created',
        sort_type: Optional[str] = 'desc'
    ):
        response = APIResponse()
        queries = json.loads(query)

        search_params = []

        for key in queries:
            if key == 'attributes':
                filed_params = {
                    "nested": True,
                    "field": "attributes",
                    "range": False,
                    "name": queries['attributes']['name'],
                    "multi_values": False
                }

                search_params.append(filed_params)

                if 'attributes' in queries['attributes']:
                    for record in queries['attributes']['attributes']:
                        filed_params = {
                            "nested": True,
                            "field": "attributes",
                            "range": False,
                            "name": queries['attributes']['name'],
                            "multi_values": False
                        }

                        filed_params["attribute_name"] = record['attribute_name']

                        if record['type'] == 'text':
                            if record['condition'] == 'contain':
                                filed_params['value'] = '*{}*'.format(
                                    record['value'])
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
                    "nested": False,
                    "field": key,
                    "range": queries[key]['value'],
                    "multi_values": False,
                    "search_type": queries[key]['condition']
                }
                search_params.append(filed_params)
            elif key == 'tags':
                filed_params = {
                    "nested": False,
                    "field": key,
                    "range": False,
                    "multi_values": True
                }
                if queries['tags']['condition'] == 'contain':
                    filed_params['search_type'] = 'should'
                else:
                    filed_params['search_type'] = 'must'
                filed_params['value'] = queries['tags']['value']
                search_params.append(filed_params)
            else:
                filed_params = {
                    "nested": False,
                    "field": key,
                    "range": False,
                    "multi_values": False,
                    "value": queries[key]['value'],
                    "search_type": queries[key]['condition']
                }
                search_params.append(filed_params)
        res = file_search(ES_INDEX, page, page_size,
                          search_params, sort_by, sort_type)

        response.code = EAPIResponseCode.success
        response.result = res['hits']['hits']
        response.total = res['hits']['total']['value']
        return response

    @router.put("/entity/file", tags=[_API_TAG],
                summary="Update a file entity in elastic search")
    @catch_internal(_API_NAMESPACE)
    async def file_meta_update(self, request_payload: FileMetaUpdate):
        response = APIResponse()

        global_entity_id = request_payload.global_entity_id
        updated_fields = request_payload.updated_fields

        if not global_entity_id:
            response.code = EAPIResponseCode.bad_request
            response.result = 'global_entity_id is required'

            return response

        if 'time_lastmodified' in updated_fields:
            updated_fields['time_lastmodified'] = int(
                updated_fields['time_lastmodified'])

        res = update_one_by_id(ES_INDEX, global_entity_id, updated_fields)

        if res.get('result') == 'updated' or res.get('result') == 'noop':
            res.update({'result':'updated'})
            self.__logger.debug('Result of Filemeta Update: Success')
            response.code = EAPIResponseCode.success
            response.result = res
        else:
            self.__logger.debug('Result of Filemeta Update: Failed')
            response.code = EAPIResponseCode.internal_error
            response.result = 'Faied to Update Filemeta in elastic search'

        return response

    @router.get("/entity/file/search-rules", tags=[_API_TAG],
                summary="Return searchable fileds")
    @catch_internal(_API_NAMESPACE)
    async def search_rules(self):
        response = APIResponse()

        res = get_mappings(ES_INDEX)

        searchable_fileds = ['file_name', 'uploader',
                             'tags', 'manifest', 'time_created']

        mappings = res['files']['mappings']['properties']

        result = []

        for key in mappings:
            if key == 'file_name':
                result.append({"filed": "fileName", "conditions": [
                              "contain", "equal"], "type": "string"})
            if key == 'uploader':
                result.append({"filed": "uploader", "conditions": [
                              "contain", "equal"], "type": "string"})
            if key == 'tags':
                result.append({"filed": "tags", "conditions": [
                              "contain", "equal"], "type": "array"})
            if key == 'time_created':
                result.append({"filed": "timeCreated", "conditions": [
                              "equal"], "type": "date"})
            if key == 'attributes':
                result.append({"filed": "attributes", "conditions": [
                              "equal"], "type": "array"})

        response.code = EAPIResponseCode.success
        response.result = result

        return response
