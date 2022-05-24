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

test_lineage_api = '/v1/lineage/'


async def test_get_lineage_should_return_200(test_async_client, httpx_mock):
    payload = {'item_id': 'fake_item_id', 'direction': 'INPUT'}
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/lineage/uniqueAttribute/type/file_data'
            '?attr:global_entity_id=fake_item_id&depth=50&direction=INPUT'
        ),
        json={
            'baseEntityGuid': 'fake_guid',
            'lineageDirection': 'INPUT',
            'lineageDepth': 50,
            'guidEntityMap': {},
            'relations': [],
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_item_id'
        ),
        json={
            'entities': [
                {
                    'typeName': 'file_data',
                    'attributes': {
                        'global_entity_id': 'fake_item_id',
                        'owner': 'admin',
                        'createTime': 1637072372,
                        'qualifiedName': 'fake_id',
                        'name': 'fake_id',
                        'description': 'Raw file in greenroom',
                        'full_path': 'fake_id',
                    },
                    'guid': 'c1f919ea-63bc-4232-ad32-7a5c20386df1',
                    'status': 'ACTIVE',
                    'displayText': 'fake_id',
                    'classificationNames': [],
                    'meaningNames': [],
                    'meanings': [],
                    'isIncomplete': False,
                    'labels': [],
                }
            ],
            'approximateCount': 30405,
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/item/fake_item_id',
        json={
            'result': {
                'id': 'e09f1614-9301-417a-868b-7ce421dc3g6b',
                'parent': 'c0889128-82a7-44cb-1012-415192a57bb1',
                'parent_path': 'admin',
                'restore_path': None,
                'archived': True,
                'type': 'file',
                'zone': 0,
                'name': 'file.py',
                'size': 739,
                'owner': 'admin',
                'container_code': 'testproject',
                'container_type': 'project',
                'created_time': '2022-04-19 15:06:41.544406',
                'last_updated_time': '2022-04-19 15:09:20.398756',
                'storage': {
                    'id': '81bb3b51-2d5d-222f-8183-6fe802fa7d22',
                    'location_uri': 'location',
                    'version': '1234',
                },
                'extended': {
                    'id': '66a8a999-c569-3af1-2d22-0a4dbbaafad5',
                    'extra': {'tags': [], 'system_tags': [], 'attributes': {}},
                },
            }
        },
        status_code=200,
    )
    res = await test_async_client.get(test_lineage_api, query_string=payload)
    response = res.json()
    assert res.status_code == 200
    assert response['result']['baseEntityGuid'] == 'fake_guid'


async def test_get_lineage_with_atlas_error_should_return_404(test_async_client, httpx_mock):
    payload = {'item_id': 'fake_item_id', 'direction': 'INPUT'}
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/lineage/uniqueAttribute/type/file_data'
            '?attr:global_entity_id=fake_item_id&depth=50&direction=INPUT'
        ),
        json={'errorCode': 'ATLAS-404'},
        status_code=500,
    )
    res = await test_async_client.get(test_lineage_api, query_string=payload)
    assert res.status_code == 404


async def test_create_lineage_should_return_200(test_async_client, httpx_mock):
    payload = {
        'input_id': 'fake_input_id',
        'output_id': 'fake_output_id',
        'input_name': 'fake_input_name',
        'output_name': 'fake_output_name',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }

    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_input_id'
        ),
        json={
            'entities': [
                {
                    'guid': 'input_guid',
                    'attributes': {'global_entity_id': 'fake_input_id'},
                }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_output_id'
        ),
        json={
            'entities': [
                {
                    'guid': 'output_guid',
                    'attributes': {'global_entity_id': 'fake_output_id'},
                }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='POST',
        url='http://atlas_url/api/atlas/v2/entity/bulk',
        json={'mutatedEntities': {'CREATE': []}},
        status_code=200,
    )
    res = await test_async_client.post(test_lineage_api, json=payload)
    assert res.status_code == 200


async def test_create_lineage_with_duplicate_id_should_return_400(test_async_client, httpx_mock):
    payload = {
        'input_id': 'fake_input_id',
        'output_id': 'fake_input_id',
        'input_name': 'fake_input_name',
        'output_name': 'fake_output_name',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }
    res = await test_async_client.post(test_lineage_api, json=payload)
    assert res.status_code == 400


async def test_create_lineage_with_not_found_entity_should_return_403(test_async_client, httpx_mock):
    payload = {
        'input_id': 'fake_input_id',
        'output_id': 'fake_output_id',
        'input_name': 'fake_input_name',
        'output_name': 'fake_output_name',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }

    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_input_id'
        ),
        json={
            'entities': [
                {
                    'guid': 'input_guid',
                    'attributes': {'global_entity_id': 'fake_input_id'},
                }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_output_id'
        ),
        json={'entities': []},
        status_code=200,
    )
    res = await test_async_client.post(test_lineage_api, json=payload)
    assert res.status_code == 404
