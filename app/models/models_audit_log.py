from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from .base_models import APIResponse

class AuditLogCreation(BaseModel):
    '''
    Create an Audit Log
    '''
    action: str
    operator: str
    target: str
    outcome: str
    resource: str
    display_name: str
    project_code: str
    extra: dict

class AuditLogQuery(BaseModel):
    '''
    Query Audit Logs
    '''
    project_code: str
    action: Optional[str] = None
    resource: str
    operator: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None