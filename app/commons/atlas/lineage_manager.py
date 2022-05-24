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

from time import time

import httpx
from common import LoggerFactory

from app.config import ConfigClass
from app.models.data_models import EDataType
from app.models.data_models import EPipeline
from app.models.meta_class import MetaService
from app.models.models_lineage import CreationForm


class SrvLineageMgr(metaclass=MetaService):
    _logger = LoggerFactory('api_lineage_action').get_logger()

    def __init__(self):
        self.lineage_endpoint = 'api/atlas/v2/lineage/uniqueAttribute/type'
        self.entity_bulk_endpoint = 'api/atlas/v2/entity/bulk'
        self.search_endpoint = 'api/atlas/v2/search/attribute'

    def lineage_to_typename(self, pipeline_name):
        """return (parent_type, child_type)"""
        return {
            EPipeline.dicom_edit.name: (EDataType.nfs_file.name, EDataType.nfs_file_processed.name),
            EPipeline.data_transfer.name: (EDataType.nfs_file.name, EDataType.nfs_file_processed.name),
        }.get(pipeline_name, (EDataType.nfs_file.name, EDataType.nfs_file_processed.name))

    async def create(self, creation_form: CreationForm, version='v1'):
        """create lineage in Atlas."""
        # v2 uses new entity type, v1 uses old one
        typenames = (
            self.lineage_to_typename(creation_form.pipeline_name) if version == 'v1' else ['file_data', 'file_data']
        )
        self._logger.info(f'_________typenames is: {typenames}')
        # to atlas post form
        input_file_name = creation_form.input_name
        output_file_name = creation_form.output_name

        self._logger.debug(f'[SrvLineageMgr]input_file_path: {creation_form.input_id}')
        self._logger.debug(f'[SrvLineageMgr]output_file_path: {creation_form.output_id}')
        current_timestamp = time() if not creation_form.process_timestamp else creation_form.process_timestamp
        qualifiedName = '{}:{}:{}:{}:to:{}'.format(
            creation_form.project_code,
            creation_form.pipeline_name,
            current_timestamp,
            input_file_name,
            output_file_name,
        )
        input_guid = await self.get_guid_by_id(creation_form.input_id, typenames[0])
        output_guid = await self.get_guid_by_id(creation_form.output_id, typenames[1])
        atlas_post_form_json = {
            'entities': [
                {
                    'typeName': 'Process',
                    'attributes': {
                        'createTime': current_timestamp,
                        'updateTime': current_timestamp,
                        'qualifiedName': qualifiedName if version == 'v1' else qualifiedName + ':v2',
                        'name': qualifiedName if version == 'v1' else qualifiedName + ':v2',
                        'description': creation_form.description,
                        'inputs': [{'guid': input_guid, 'typeName': typenames[0]}],
                        'outputs': [{'guid': output_guid, 'typeName': typenames[1]}],
                    },
                }
            ]
        }
        self._logger.debug(f'[SrvLineageMgr]atlas_post_form_json: {atlas_post_form_json}')
        # create atlas lineage
        headers = {'content-type': 'application/json'}
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.post(
                ConfigClass.ATLAS_API + self.entity_bulk_endpoint,
                json=atlas_post_form_json,
                auth=(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
                headers=headers,
            )
        return res

    async def get(self, _id, type_name, direction, depth=50):
        url = ConfigClass.ATLAS_API + self.lineage_endpoint + '/{}'.format(type_name)
        self._logger.debug(f'Url is: {url}')
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                url, params={'attr:global_entity_id': _id, 'depth': depth, 'direction': direction},
                auth=(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
            )
        return response

    async def search_entity(self, _id, type_name=None):
        url = ConfigClass.ATLAS_API + self.search_endpoint
        self._logger.debug(f'LIne 97 Url is: {url}')
        typeName = type_name if type_name else 'nfs_file_processed'
        params = {'attrName': 'global_entity_id', 'typeName': typeName, 'attrValuePrefix': _id}
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                url, timeout=100, params=params, auth=(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )
        if response.status_code == 200 and response.json().get('entities'):
            return response
        else:
            raise Exception(f'Not Found Entity: {_id}')

    async def get_guid_by_id(self, _id, type_name=None):
        search_res = await self.search_entity(_id, type_name)
        if search_res.status_code == 200:
            my_json = search_res.json()
            self._logger.debug(f'[SrvLineageMgr]search_res: {my_json}')
            entities = my_json['entities']
            found = [entity for entity in entities if entity['attributes']['global_entity_id'] == _id]
            return found[0]['guid'] if found else None
        else:
            self._logger.error(f'Error when get_guid_by_id: {search_res.text}')
            return None
