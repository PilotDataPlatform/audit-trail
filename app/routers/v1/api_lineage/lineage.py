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

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv

from app.commons.atlas.lineage_manager import SrvLineageMgr
from app.models.base_models import EAPIResponseCode
from app.models.models_lineage import GETLineage
from app.models.models_lineage import GETLineageResponse
from app.models.models_lineage import POSTLineage
from app.models.models_lineage import POSTLineageResponse
from app.models.models_lineage import creation_form_factory
from app.resources.error_handler import catch_internal
from app.resources.neo4j_helper import http_query_node

router = APIRouter()
_API_NAMESPACE = 'api_lineage'


@cbv(router)
class Lineage:
    lineage_mgr = SrvLineageMgr()
    _logger = LoggerFactory('api_lineage_action').get_logger()

    @router.get('/', response_model=GETLineageResponse, summary='Get Lineage')
    @catch_internal(_API_NAMESPACE)
    async def get(self, params: GETLineage = Depends(GETLineage)):
        """get lineage, query params: geid, direction defult(INPUT)"""
        api_response = GETLineageResponse()
        geid = params.geid
        type_name = 'file_data'

        response = await self.lineage_mgr.get(geid, type_name, params.direction)
        self._logger.debug(f'Response of get is {response.text}')
        if response.status_code == 200:
            response_json = response.json()
            self._logger.info(f'The Response from atlas is: {str(response_json)}')
            if response_json['guidEntityMap']:
                await self.add_display_path(response_json['guidEntityMap'])
                pass
            else:
                res_default_entity = await self.lineage_mgr.search_entity(geid, type_name=type_name)
                self._logger.info(f'The default_entity from atlas is: {str(res_default_entity.json())}')
                if res_default_entity.status_code == 200 and len(res_default_entity.json()['entities']) > 0:
                    default_entity = res_default_entity.json()['entities'][0]
                    response_json['guidEntityMap'] = {'{}'.format(default_entity['guid']): default_entity}
                    self._logger.info(f'The current response json is: {str(response_json)}')
                    await self.add_display_path(response_json['guidEntityMap'])
                else:
                    self._logger.debug(f'LINE50: {res_default_entity.status_code}')
                    api_response.error_msg = 'Invalid Entity'
                    api_response.code = EAPIResponseCode.bad_request
                    return api_response.json()
            api_response.result = response_json
            return api_response.json_response()
        else:
            self._logger.error('LINE 56 Error: %s', response.text)
            api_response.error_msg = response.text
            if 'ATLAS-404' in response.json().get('errorCode'):
                api_response.code = EAPIResponseCode.not_found
                return api_response.json_response()
            raise

    @router.post('/', response_model=POSTLineageResponse, summary='POST Lineage')
    @catch_internal(_API_NAMESPACE)
    async def post(self, data: POSTLineage):
        """
        add new lineage to the metadata service by payload
            {
                'input_geid': '',
                'output_geid': '',
                'project_code': '',
                'pipeline_name': '',
                'description': '',
            }
        """
        api_response = POSTLineageResponse()
        creation_form = {}

        if data.input_geid == data.output_geid:
            api_response.error_msg = 'Input and Output geid are the same'
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        try:
            creation_form = creation_form_factory(data)
        except Exception as e:
            self._logger.exception('Error in create lineage.')
            api_response.error_msg = str(e)
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        try:
            # create atlas lineage
            res = await self.lineage_mgr.create(creation_form, version='v2')
            # log it if not 200 level response
            if res.status_code >= 300:
                self._logger.error('Error in response: %s', res.text)
                api_response.error_msg = res.text
                api_response.code = EAPIResponseCode.internal_error
                return api_response.json_response()
        except Exception as e:
            self._logger.exception('Error in create lineage.')
            api_response.error_msg = str(e)
            if 'Not Found Entity' in str(e):
                api_response.code = EAPIResponseCode.not_found
            else:
                api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        api_response.result = res.json()
        return api_response.json_response()

    async def add_display_path(self, guidEntityMap):
        for _, value in guidEntityMap.items():
            if value['typeName'] == 'Process':
                continue

            geid = value['attributes']['global_entity_id']
            node_res = await http_query_node(geid)
            if node_res.status_code != 200:
                raise Exception('Neo4j error')
            node_data = node_res.json()
            self._logger.info(f'Node in Neo4j is: {str(node_data)}')
            if len(node_data) == 0:
                continue

            labels = node_data[0]['labels']
            value['attributes']['zone'] = labels

            if 'display_path' in node_data[0]:
                value['attributes']['display_path'] = node_data[0]['display_path']
            else:
                value['attributes']['display_path'] = value['attributes']['full_path']
