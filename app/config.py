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

import os
from typing import Any
from typing import Dict

from common import VaultClient
from dotenv import load_dotenv
from pydantic import BaseSettings
from pydantic import Extra

# load env var from local env file for local test
load_dotenv()
SRV_NAMESPACE = os.environ.get('APP_NAME', 'audit_trail')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(os.getenv('VAULT_URL'), os.getenv('VAULT_CRT'), os.getenv('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    port: int = 5078
    host: str = '127.0.0.1'
    env: str = 'test'
    version = '0.1.0'

    # disk mounts
    NFS_ROOT_PATH: str = './'

    ATLAS_ADMIN: str
    ATLAS_PASSWD: str

    ELASTIC_SEARCH_SERVICE: str
    ATLAS_API: str
    METADATA_SERVICE: str

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def __init__(self):
        super().__init__()

        self.ELASTIC_SEARCH_SERVICE += '/'
        self.ATLAS_API += '/'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


ConfigClass = Settings()
