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

import httpx

from app.config import ConfigClass


async def http_query_node(geid):
    """Get file node by geid."""

    node_query_url = ConfigClass.NEO4J_SERVICE + 'nodes/geid/{}'.format(geid)
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(node_query_url)
    return response
