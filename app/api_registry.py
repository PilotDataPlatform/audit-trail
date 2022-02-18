from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_audit_log
from .routers.v1.api_lineage import lineage 
from .routers.v1 import api_file_meta

def api_registry(app: FastAPI):
    app.include_router(api_root.router)
    app.include_router(api_audit_log.router, prefix="/v1")
    app.include_router(lineage.router, prefix="/v1/lineage", tags=["lineage"])
    app.include_router(api_file_meta.router, prefix="/v1")
