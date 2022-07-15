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

audit_log_api = '/v1/audit-logs'


async def test_create_audit_log_should_return_200_successed(test_async_client, httpx_mock):
    payload = {
        'operator': 'test_user',
        'action': 'testaction',
        'target': 'string1',
        'outcome': 'string2',
        'resource': 'unittest',
        'display_name': 'string2',
        'project_code': 'testproject',
        'extra': {},
    }

    httpx_mock.add_response(
        method='POST',
        url='http://elastic_search:123/unittest/operation_logs',
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
    res = await test_async_client.post(audit_log_api, json=payload)
    response = res.json()
    assert res.status_code == 200
    assert response['result']['result'] == 'created'


async def test_create_audit_log_failed_should_return_500_internal(test_async_client, httpx_mock):
    payload = {
        'operator': 'test_user',
        'action': 'testaction',
        'target': 'string1',
        'outcome': 'string2',
        'resource': 'unittest',
        'display_name': 'string2',
        'project_code': 'testproject',
        'extra': {},
    }

    httpx_mock.add_response(
        method='POST',
        url='http://elastic_search:123/unittest/operation_logs',
        json={'code': 500, 'error_msg': 'mock error', 'result': ''},
        status_code=500,
    )
    res = await test_async_client.post(audit_log_api, json=payload)
    response = res.json()
    assert res.status_code == 500
    assert response['result'] == 'failed to insert audit log into elastic search'


async def test_query_audit_log_should_return_200(test_async_client, httpx_mock):
    params = {
        'project_code': 'testproject',
        'resource': 'unittest',
        'start_date': 1646629200,
        'action': 'all',
        'operator': 'testuser',
        'end_date': 1646715600,
    }
    httpx_mock.add_response(
        method='GET',
        url='http://elastic_search:123/unittest/operation_logs/_search',
        json={'hits': {'hits': 'mock_hits', 'total': {'value': 1}}},
        status_code=200,
    )
    res = await test_async_client.get(audit_log_api, query_string=params)
    assert res.status_code == 200
