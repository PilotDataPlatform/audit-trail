import os
from common import VaultClient
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from dotenv import load_dotenv

#load env var from local env file for local test
load_dotenv()
SRV_NAMESPACE = os.environ.get("APP_NAME", "service_provenance")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):

    port: int = 5078
    host: str = "127.0.0.1"
    env: str = "test"
    version = "0.1.0"
    opentelemetry_enabled: bool = False
    
    # disk mounts
    NFS_ROOT_PATH: str = "./"

    ATLAS_ADMIN: str
    ATLAS_PASSWD: str

    METADATA_API: str
    UTILITY_SERVICE: str

    ELASTIC_SEARCH_SERVICE: str
    ATLAS_API: str
    NEO4J_SERVICE: str

    OPEN_TELEMETRY_HOST: str = "127.0.0.1"
    OPEN_TELEMETRY_PORT: int = 6831


    def __init__(self):
        super().__init__()
        
        self.opentelemetry_enabled = True if self.OPEN_TELEMETRY_ENABLED == "TRUE" else False
        self.UTILITY_SERVICE += "/v1/"
        self.ELASTIC_SEARCH_SERVICE += "/"
        self.ATLAS_API += "/"
        self.NEO4J_SERVICE += "/v1/neo4j/"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                load_vault_settings,
                env_settings,
                file_secret_settings,
            )

ConfigClass = Settings()
