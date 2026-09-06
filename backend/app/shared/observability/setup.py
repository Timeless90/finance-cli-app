import json
import logging
from collections.abc import Callable
from contextvars import ContextVar
from datetime import UTC, datetime

from fastapi import FastAPI
from opentelemetry import trace

from app.shared.config import ApiSettings

request_id: ContextVar[str] = ContextVar("request_id", default="")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        context = trace.get_current_span().get_span_context()
        return json.dumps(
            {
                "time": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
                "logger": record.name,
                "request_id": request_id.get(),
                "trace_id": format(context.trace_id, "032x"),
            }
        )


def configure(app: FastAPI, settings: ApiSettings) -> Callable[[], None]:
    logger = logging.getLogger("app")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    shutdowns: list[Callable[[], None]] = []
    if settings.telemetry_enabled:
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter,
        )
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.service_name})
        endpoint = settings.otlp_endpoint.rstrip("/")
        traces = TracerProvider(resource=resource)
        traces.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint + "/v1/traces"))
        )
        metrics = MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=endpoint + "/v1/metrics"),
                    export_interval_millis=5000,
                )
            ],
        )
        logs = LoggerProvider(resource=resource)
        logs.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint + "/v1/logs"))
        )
        otel_handler = LoggingHandler(logger_provider=logs)
        otel_handler.setFormatter(JsonFormatter())
        logger.addHandler(otel_handler)
        FastAPIInstrumentor.instrument_app(
            app, tracer_provider=traces, meter_provider=metrics
        )
        shutdowns = [
            traces.shutdown,
            metrics.shutdown,
            logs.shutdown,
            lambda: logger.removeHandler(otel_handler),
        ]

    def close() -> None:
        for shutdown in shutdowns:
            shutdown()
        logger.removeHandler(handler)
        handler.close()

    return close
