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

from fastapi import FastAPI
from fastapi_health import health

from app.resources.health_check import atlas_check
from app.resources.health_check import es_check
from app.routers import api_root
from app.routers.v1 import api_audit_log
from app.routers.v1 import api_file_meta
from app.routers.v1.api_lineage import lineage


def api_registry(app: FastAPI):
    app.add_api_route('/v1/health', health([atlas_check, es_check], success_status=204), tags=['Health'])
    app.include_router(api_root.router)
    app.include_router(api_audit_log.router, prefix='/v1')
    app.include_router(lineage.router, prefix='/v1/lineage', tags=['lineage'])
    app.include_router(api_file_meta.router, prefix='/v1')
