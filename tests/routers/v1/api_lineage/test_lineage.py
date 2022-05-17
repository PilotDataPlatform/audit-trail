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
    payload = {'geid': 'fake_geid', 'direction': 'INPUT'}
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/lineage/uniqueAttribute/type/file_data'
            '?attr:global_entity_id=fake_geid&depth=50&direction=INPUT'
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
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_geid'
        ),
        json={
            'entities': [
                {
                    'typeName': 'file_data',
                    'attributes': {
                        'global_entity_id': 'fake_geid',
                        'owner': 'admin',
                        'createTime': 1637072372,
                        'qualifiedName': 'fake_geid',
                        'name': 'fake_geid',
                        'description': 'Raw file in greenroom',
                        'full_path': 'fake_geid',
                    },
                    'guid': 'c1f919ea-63bc-4232-ad32-7a5c20386df1',
                    'status': 'ACTIVE',
                    'displayText': 'fake_geid',
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
        url='http://neo4j_service/nodes/geid/fake_geid',
        json=[
            {
                'labels': ['Greenroom', 'File'],
                'display_path': 'test_user/test_file.zip',
                'full_path': '/test_user/test_file.zip',
            }
        ],
        status_code=200,
    )
    res = await test_async_client.get(test_lineage_api, query_string=payload)
    response = res.json()
    assert res.status_code == 200
    assert response['result']['baseEntityGuid'] == 'fake_guid'


async def test_get_lineage_with_atlas_error_should_return_404(test_async_client, httpx_mock):
    payload = {'geid': 'fake_geid', 'direction': 'INPUT'}
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/lineage/uniqueAttribute/type/file_data'
            '?attr:global_entity_id=fake_geid&depth=50&direction=INPUT'
        ),
        json={'errorCode': 'ATLAS-404'},
        status_code=500,
    )
    res = await test_async_client.get(test_lineage_api, query_string=payload)
    assert res.status_code == 404


async def test_create_lineage_should_return_200(test_async_client, httpx_mock):
    payload = {
        'input_geid': 'fake_input_geid',
        'output_geid': 'fake_output_geid',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/nodes/geid/fake_input_geid',
        json=[{'name': 'fake_gr_file'}],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/nodes/geid/fake_output_geid',
        json=[{'name': 'fake_cr_file'}],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_input_geid'
        ),
        json={
            'entities': [
                {
                    'guid': 'input_guid',
                    'attributes': {'global_entity_id': 'fake_input_geid'},
                }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_output_geid'
        ),
        json={
            'entities': [
                {
                    'guid': 'output_guid',
                    'attributes': {'global_entity_id': 'fake_output_geid'},
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


async def test_create_lineage_with_duplicate_geid_should_return_400(test_async_client, httpx_mock):
    payload = {
        'input_geid': 'fake_input_geid',
        'output_geid': 'fake_input_geid',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }
    res = await test_async_client.post(test_lineage_api, json=payload)
    assert res.status_code == 400


async def test_create_lineage_with_not_found_entity_should_return_403(test_async_client, httpx_mock):
    payload = {
        'input_geid': 'fake_input_geid',
        'output_geid': 'fake_output_geid',
        'project_code': 'test_project',
        'pipeline_name': 'test pipeline',
        'description': 'unit test',
    }
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/nodes/geid/fake_input_geid',
        json=[{'name': 'fake_gr_file'}],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/nodes/geid/fake_output_geid',
        json=[{'name': 'fake_cr_file'}],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_input_geid'
        ),
        json={
            'entities': [
                {
                    'guid': 'input_guid',
                    'attributes': {'global_entity_id': 'fake_input_geid'},
                }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://atlas_url/api/atlas/v2/search/attribute'
            '?attrName=global_entity_id&typeName=file_data&attrValuePrefix=fake_output_geid'
        ),
        json={'entities': []},
        status_code=200,
    )
    res = await test_async_client.post(test_lineage_api, json=payload)
    assert res.status_code == 404
