from pydantic import BaseModel, Field
from .base_models import APIResponse
from app.commons.logger_services.logger_factory_service import SrvLoggerFactory

_logger = SrvLoggerFactory('api_lineage_action').get_logger()


class GETLineage(BaseModel):
    geid: str
    direction: str = "INPUT"


class GETLineageResponse(APIResponse):
    result: dict = Field({}, example={
         "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": [
        ]
    })


class POSTLineage(BaseModel):
    input_geid: str
    output_geid: str
    project_code: str
    pipeline_name: str
    description: str


class POSTLineageResponse(APIResponse):
    result: dict = Field({}, example={
         "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": [
        ]
    })


class CreationForm:
    def __init__(self, event=None):
        if event:
            self._attribute_map = event
        else:
            self._attribute_map = {
                'input_path': '',
                'output_path': '',
                'project_code': '',
                'pipeline_name': '',
                'description': '',
                'process_timestamp': '',
            }

    @property
    def to_dict(self):
        return self._attribute_map

    @property
    def input_path(self):
        return self._attribute_map['input_path']

    @input_path.setter
    def input_path(self, input_path):
        self._attribute_map['input_path'] = input_path

    @property
    def output_path(self):
        return self._attribute_map['output_path']

    @output_path.setter
    def output_path(self, output_path):
        self._attribute_map['output_path'] = output_path

    @property
    def project_code(self):
        return self._attribute_map['project_code']

    @project_code.setter
    def project_code(self, project_code):
        self._attribute_map['project_code'] = project_code

    @property
    def pipeline_name(self):
        return self._attribute_map['pipeline_name']

    @pipeline_name.setter
    def pipeline_name(self, pipeline_name):
        self._attribute_map['pipeline_name'] = pipeline_name

    @property
    def description(self):
        return self._attribute_map['description']

    @description.setter
    def description(self, description):
        self._attribute_map['description'] = description

    @property
    def process_timestamp(self):
        return self._attribute_map['process_timestamp']

    @process_timestamp.setter
    def process_timestamp(self, process_timestamp):
        self._attribute_map['process_timestamp'] = process_timestamp

def creation_form_factory(post_form):
    try:
        my_form = CreationForm()
        my_form.input_geid = post_form.input_geid
        my_form.output_geid = post_form.output_geid
        my_form.project_code = post_form.project_code
        my_form.pipeline_name = post_form.pipeline_name
        my_form.description = getattr(post_form, "description", '')
        my_form.process_timestamp = getattr(post_form, "process_timestamp", None)
        return my_form
    except Exception as e:
        _logger.error(str(e))
        raise(Exception('Invalid post form: ' + str(post_form)))
    
