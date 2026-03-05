"""OpenTelemetry instrumentation for ML portfolio services.

Provides distributed tracing across all ML APIs (BankChurn, NLPInsight, ChicagoTaxi).
Traces propagate through HTTP headers enabling end-to-end visibility of:
- API request lifecycle (receive → validate → predict → respond)
- Model inference latency
- Data validation steps
- Error attribution across services

Usage in FastAPI apps:
    from common_utils.telemetry import init_telemetry, get_tracer

    # At app startup
    init_telemetry(service_name="bankchurn-predictor")

    # In route handlers
    tracer = get_tracer()
    with tracer.start_as_current_span("predict") as span:
        span.set_attribute("model.type", "stacking_classifier")
        result = model.predict(X)
        span.set_attribute("prediction.churn_probability", float(prob))

Environment variables:
    OTEL_ENABLED=true              Enable/disable telemetry (default: false)
    OTEL_EXPORTER_OTLP_ENDPOINT   OTLP collector endpoint (default: http://localhost:4317)
    OTEL_SERVICE_NAME              Override service name
    OTEL_TRACES_SAMPLER            Sampler type (default: parentbased_traceid_ratio)
    OTEL_TRACES_SAMPLER_ARG        Sampling rate 0.0-1.0 (default: 1.0)
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

logger = logging.getLogger(__name__)

# Lazy imports — OpenTelemetry is optional; services work without it
_tracer = None
_initialized = False


def _is_otel_enabled() -> bool:
    """Check if OpenTelemetry is enabled via environment variable."""
    return os.getenv("OTEL_ENABLED", "false").lower() in ("true", "1", "yes")


def init_telemetry(
    service_name: str,
    service_version: str = "3.0.0",
    environment: str = "production",
) -> bool:
    """Initialize OpenTelemetry tracing with OTLP exporter.

    Parameters
    ----------
    service_name : str
        Name of the service (e.g., "bankchurn-predictor").
    service_version : str
        Semantic version of the service.
    environment : str
        Deployment environment (dev, staging, production).

    Returns
    -------
    bool
        True if telemetry was initialized, False if skipped or failed.
    """
    global _tracer, _initialized

    if _initialized:
        return True

    if not _is_otel_enabled():
        logger.info("OpenTelemetry disabled (set OTEL_ENABLED=true to enable)")
        _initialized = True
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {
                "service.name": os.getenv("OTEL_SERVICE_NAME", service_name),
                "service.version": service_version,
                "deployment.environment": environment,
                "service.namespace": "ml-portfolio",
            }
        )

        provider = TracerProvider(resource=resource)

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name, service_version)
        _initialized = True

        logger.info(f"OpenTelemetry initialized: service={service_name}, " f"endpoint={endpoint}")
        return True

    except ImportError:
        logger.warning(
            "OpenTelemetry packages not installed. "
            "Install with: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-grpc"
        )
        _initialized = True
        return False
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
        _initialized = True
        return False


def get_tracer(name: Optional[str] = None):
    """Get the configured tracer instance.

    Returns a no-op tracer if OpenTelemetry is not initialized.

    Parameters
    ----------
    name : str, optional
        Tracer name override.

    Returns
    -------
    opentelemetry.trace.Tracer or NoOpTracer
    """
    global _tracer

    if _tracer is not None:
        return _tracer

    # Return a no-op tracer if OTel is not available
    return _NoOpTracer()


def instrument_fastapi(app: Any) -> None:
    """Instrument a FastAPI application with OpenTelemetry.

    Adds automatic tracing for all HTTP endpoints.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    """
    if not _is_otel_enabled():
        return

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except ImportError:
        logger.debug("opentelemetry-instrumentation-fastapi not installed, skipping")
    except Exception as e:
        logger.warning(f"Failed to instrument FastAPI: {e}")


# ---------------------------------------------------------------------------
# No-op implementations for when OTel is not available
# ---------------------------------------------------------------------------


class _NoOpSpan:
    """No-op span that silently ignores all operations."""

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_status(self, status: Any) -> None:
        pass

    def record_exception(self, exception: BaseException) -> None:
        pass

    def add_event(self, name: str, attributes: Optional[Dict] = None) -> None:
        pass

    def end(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class _NoOpTracer:
    """No-op tracer that returns no-op spans."""

    def start_as_current_span(self, name: str, **kwargs: Any) -> _NoOpSpan:
        return _NoOpSpan()

    @contextmanager
    def start_span(self, name: str, **kwargs: Any) -> Generator[_NoOpSpan, None, None]:
        yield _NoOpSpan()


# ---------------------------------------------------------------------------
# Convenience decorators for ML-specific tracing
# ---------------------------------------------------------------------------


def trace_prediction(model_name: str):
    """Decorator to trace model prediction calls.

    Usage:
        @trace_prediction("bankchurn")
        def predict(self, X):
            return self.model.predict(X)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                f"{model_name}.predict",
            ) as span:
                span.set_attribute("ml.model.name", model_name)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("ml.prediction.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("ml.prediction.success", False)
                    span.record_exception(e)
                    raise

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def trace_data_validation(schema_name: str):
    """Decorator to trace data validation steps.

    Usage:
        @trace_data_validation("bankchurn_raw")
        def validate(df):
            return BankChurnRawSchema.validate(df)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(
                f"validate.{schema_name}",
            ) as span:
                span.set_attribute("validation.schema", schema_name)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("validation.passed", True)
                    if hasattr(result, "__len__"):
                        span.set_attribute("validation.rows", len(result))
                    return result
                except Exception as e:
                    span.set_attribute("validation.passed", False)
                    span.record_exception(e)
                    raise

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
