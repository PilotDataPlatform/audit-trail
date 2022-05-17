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
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.api_registry import api_registry
from app.config import SRV_NAMESPACE
from app.config import ConfigClass


def create_app():
    """Initialize and configure the application."""

    app = FastAPI(
        title='Audit Trail Service',
        description='Service for managing audit logs.',
        docs_url='/v1/api-doc',
        version=ConfigClass.version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # API registry
    # v1
    api_registry(app)
    if ConfigClass.OPEN_TELEMETRY_ENABLED:
        instrument_app(app)

    return app


def instrument_app(app) -> None:
    """Instrument the application with OpenTelemetry tracing."""

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: SRV_NAMESPACE}))
    trace.set_tracer_provider(tracer_provider)

    jaeger_exporter = JaegerExporter(agent_host_name='127.0.0.1', agent_port=6831)

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    FastAPIInstrumentor.instrument_app(app)
    ElasticsearchInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
