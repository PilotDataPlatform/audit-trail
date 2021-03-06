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

import pytest
from async_asgi_testclient import TestClient as TestAsyncClient

from app.config import ConfigClass
from run import app


@pytest.fixture
def test_async_client():
    return TestAsyncClient(app)


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(ConfigClass, 'ELASTIC_SEARCH_HOST', 'elastic_search')
    monkeypatch.setattr(ConfigClass, 'ELASTIC_SEARCH_PORT', 123)
    monkeypatch.setattr(ConfigClass, 'ATLAS_HOST', 'altas')
    monkeypatch.setattr(ConfigClass, 'ATLAS_PORT', 123)
    monkeypatch.setattr(ConfigClass, 'METADATA_SERVICE', 'http://metadata_service/v1/')
