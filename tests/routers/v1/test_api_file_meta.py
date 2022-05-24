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

test_file_entity_api = '/v1/entity/file'


async def test_create_file_metadata(test_async_client, httpx_mock):
    payload = {
        'global_entity_id': 'fake_id',
        'operator': 'test_user',
        'zone': 'gr',
        'file_size': 1234,
        'tags': ['teattag'],
        'archived': False,
        'location': 'http://minio',
        'time_lastmodified': 1646715600,
        'time_created': 1646629200,
        'process_pipeline': 'fake_pipeline',
        'uploader': 'test_user',
        'file_name': 'fake_file',
        'atlas_guid': 'fake_guid',
        'display_path': 'test_user/fake_file',
        'project_code': 'testproject',
    }
    httpx_mock.add_response(
        method='PUT',
        url='http://elastic_search/files/_doc/fake_id',
        json={
            '_index': 'unittest',
            '_type': 'operation_logs',
            '_id': 'fake_id',
            '_version': 1,
            'result': 'created',
            '_shards': {'total': 2, 'successful': 2, 'failed': 0},
            '_seq_no': 122,
            '_primary_term': 2,
        },
        status_code=200,
    )
    res = await test_async_client.post(test_file_entity_api, json=payload)
    assert res.status_code == 200


async def test_query_file_meta_should_return_200(test_async_client, httpx_mock):
    query = {'project_code': {'value': 'test_project', 'condition': 'equal'}}
    query = json.dumps(query)
    httpx_mock.add_response(
        method='GET',
        url='http://elastic_search/files/_search',
        json={
            'took': 6,
            'timed_out': False,
            '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
            'hits': {'total': {'value': 3, 'relation': 'gte'}, 'max_score': 1.0, 'hits': []},
        },
        status_code=200,
    )
    res = await test_async_client.get(test_file_entity_api, query_string={'query': query})
    response = res.json()
    assert res.status_code == 200
    assert response['total'] == 3


async def test_query_file_meta_with_manifest_should_return_200(test_async_client, httpx_mock):
    query = {
        'project_code': {'value': 'test_project', 'condition': 'equal'},
        'attributes': {'name': 'Manifest', 'attributes': []},
        'zone': {'value': 'greenroom', 'condition': 'equal'},
        'archived': {'value': False, 'condition': 'equal'},
    }
    query = json.dumps(query)
    httpx_mock.add_response(
        method='GET',
        url='http://elastic_search/files/_search',
        json={
            'took': 6,
            'timed_out': False,
            '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
            'hits': {'total': {'value': 3, 'relation': 'gte'}, 'max_score': 1.0, 'hits': []},
        },
        status_code=200,
    )
    res = await test_async_client.get(test_file_entity_api, query_string={'query': query})
    response = res.json()
    assert res.status_code == 200
    assert response['total'] == 3


async def test_update_file_meta_should_return_200(test_async_client, httpx_mock):
    query = {
        'global_entity_id': 'fake_id',
        'updated_fields': {
            'archived': True,
        },
    }

    httpx_mock.add_response(
        method='POST',
        url='http://elastic_search/files/_update/fake_id',
        json={
            '_index': 'files',
            '_type': '_doc',
            '_id': 'fake_id',
            '_version': 3,
            'result': 'updated',
            '_shards': {'total': 2, 'successful': 2, 'failed': 0},
            '_seq_no': 266727,
            '_primary_term': 1,
        },
        status_code=200,
    )
    res = await test_async_client.put(test_file_entity_api, json=query)
    response = res.json()
    assert res.status_code == 200
    assert response['result']['result'] == 'updated'


async def test_update_file_meta_with_es_failed_should_return_500(test_async_client, httpx_mock):
    query = {
        'global_entity_id': 'fake_id',
        'updated_fields': {
            'archived': True,
        },
    }

    httpx_mock.add_response(
        method='POST', url='http://elastic_search/files/_update/fake_id', json={'result': 'failed'}, status_code=500
    )
    res = await test_async_client.put(test_file_entity_api, json=query)
    response = res.json()
    assert res.status_code == 500
    assert response['result'] == 'Faied to Update Filemeta in elastic search'
