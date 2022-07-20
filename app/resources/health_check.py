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
from common import LoggerFactory

from app.config import ConfigClass

logger = LoggerFactory('audit_trail_health_check').get_logger()


async def atlas_check():
    try:
        admin_metrics_url = f'http://{ConfigClass.ATLAS_HOST}:{ConfigClass.ATLAS_PORT}/' + 'api/atlas/admin/metrics'
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(admin_metrics_url, auth=(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD))
            if response.status_code != 200:
                raise Exception
            logger.info('Atlas database connected successfully')
            return True
    except Exception as e:
        logger.error(f'Can not connect to the Atlas database {e}')
        return False


async def es_check():
    try:
        ELASTIC_SEARCH_URL = f'http://{ConfigClass.ELASTIC_SEARCH_HOST}:{ConfigClass.ELASTIC_SEARCH_PORT}/'
        elastic_health_url = ELASTIC_SEARCH_URL + '_cluster/health'
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(elastic_health_url)
            if response.status_code != 200:
                raise Exception
            logger.info('Elastic Search database connected successfully')
            return True
    except Exception as e:
        logger.error(f'Can not connect to the Elastic Search database {e}')
        return False
