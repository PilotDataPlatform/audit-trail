import time
from datetime import datetime, timedelta
import requests
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi_utils import cbv
from ...resources.error_handler import catch_internal
from ...resources.es_helper import exact_search, insert_one
from ...resources.entity_helper import create_geid
from ...models.models_audit_log import AuditLogCreation, AuditLogQuery
from ...models.base_models import APIResponse, EAPIResponseCode
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...config import ConfigClass

router = APIRouter()

_API_TAG = 'Audit-logs'
_API_NAMESPACE = "api_audit_log"

ES_TYPE = 'operation_logs'

@cbv.cbv(router)
class APIAuditLog:
    def __init__(self):
        self.__logger = SrvLoggerFactory('api_audit_log').get_logger()

    @router.post("/audit-logs", tags=[_API_TAG],
                 summary="Create an audit log for file operation")
    @catch_internal(_API_NAMESPACE)
    async def audit_log_creation(self, request_payload: AuditLogCreation):
        response = APIResponse()

        action = request_payload.action
        operator = request_payload.operator
        target = request_payload.target
        outcome = request_payload.outcome
        project_code = request_payload.project_code
        display_name = request_payload.display_name
        resource = request_payload.resource
        extra_info = request_payload.extra

        self.__logger.debug('Project of Audit log Creation: {}'.format(project_code))
        self.__logger.debug('Params of Audit log Creation: {}, {}, {}, {}, {}'.format(action, operator, target, outcome, resource))

        geid = create_geid('audit-logs')

        self.__logger.debug('Geid of Audit log Creation: ' + geid)

        if not geid: 
            response.code = EAPIResponseCode.internal_error
            response.error_msg = "Failed to create global id"
            return response

        # insert an new audit log into elastic search
        data = {
            "target": target,
            "outcome": outcome,
            "displayName": display_name,
            "operator": operator,
            "action": action,
            "projectCode": project_code,
            "createdTime": time.time(),
            "geid": geid,
            "resource": resource
        }

        for key in extra_info:
            data[key] = extra_info[key]

        res = insert_one(ES_TYPE, resource, data)

        if res['result'] == 'created':
            self.__logger.debug('Result of Audit log Creation: Success')
            response.code = EAPIResponseCode.success
            response.result = res
        else:
            self.__logger.debug('Result of Audit log Creation: Failed')
            response.code = EAPIResponseCode.internal_error
            response.result = 'faied to insert audit log into elastic search'

        return response


    @router.get("/audit-logs", tags=[_API_TAG],
                 summary="Get audit logs")
    @catch_internal(_API_NAMESPACE)
    async def audit_log_query(
        self, 
        query: dict = Depends(AuditLogQuery),
        page: Optional[int] = 0, 
        page_size: Optional[int] = 10, 
        sort_by: Optional[str] = 'createdTime', 
        sort_type: Optional[str] = 'desc'
    ):
        today_date = datetime.now().date()
        today_datetime = datetime.combine(today_date, datetime.min.time())

        queries = dict()
        
        for item in query:
            queries[item[0]] = item[1]

        start_date = queries['start_date']
        end_date = queries['end_date']
        project_code = queries['project_code']
        action = queries['action']
        operator = queries['operator']
        resource = queries['resource']
       
        if not start_date:
            start_date = int(today_datetime.timestamp())
        if not end_date:
            end_datetime = datetime.combine(today_date + timedelta(days=1), datetime.min.time())
            end_date = int(end_datetime.timestamp())

        # get audit logs from elastic search
        params = {
            "createdTime": [start_date, end_date],
            "projectCode" : project_code,
        }

        try:
            # for actions, we might have the `all` keyword to fetch all 4 actions.
            if action == "all":
                params['action'] = ["data_upload", "data_download", 
                    "data_transfer", "data_delete"]
            elif action:
                params['action'] = [action]

            if operator:
                params['operator'] = operator


            res = exact_search(ES_TYPE, resource, page, page_size, params, sort_by, sort_type)
        
        except Exception as e:
            self.__logger.info(e)

        response = APIResponse()
        response.code = EAPIResponseCode.success
        response.result = res['hits']['hits']
        response.total = res['hits']['total']['value']

        return response

