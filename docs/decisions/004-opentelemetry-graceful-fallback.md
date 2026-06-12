<div class="portfolio-page" markdown="1">

# ADR-004: OpenTelemetry with Graceful No-Op Fallback

- **Status**: Accepted
- **Date**: 2026-03-03
- **Authors**: Duque Ortega Mutis

> **TL;DR**: Implemented OpenTelemetry distributed tracing with a no-op fallback — when OTel packages are absent or disabled, all tracing calls become zero-cost no-ops. This lets production pods emit traces to a collector while dev/test/CI environments pay zero overhead, without conditional imports scattered across application code.

---

## Context

The portfolio runs 3 FastAPI ML services (BankChurn, NLPInsight, ChicagoTaxi) on Kubernetes. Production observability requires distributed tracing to diagnose cross-service latency, but:

1. **Not all environments need tracing** — dev, test, and CI should not require OTel packages
2. **OTel SDK is heavy** — `opentelemetry-sdk` + exporters add ~50MB to Docker images
3. **Conditional imports are fragile** — scattering `try/except` across every file is unmaintainable

### The Design Pattern Problem

The naive approach:
```python
# ❌ Scattered in every file — unmaintainable
try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
except ImportError:
    tracer = None

def predict():
    if tracer:
        with tracer.start_as_current_span("predict"):
            ...
    else:
        ...
```

This duplicates fallback logic in every file and every function.

---

## Decision

Centralize all OTel logic in **`common_utils/telemetry.py`** with:
1. **Environment-controlled activation**: `OTEL_ENABLED=true` enables tracing; anything else = no-op
2. **Graceful import fallback**: `try/except` only in `telemetry.py` — application code never sees it
3. **ML-specific decorators**: `@trace_prediction()`, `@trace_data_validation()` add semantic spans
4. **Shared module**: identical telemetry code across all 3 services via the `common_utils` package

### Usage in Application Code

```python
from common_utils.telemetry import instrument_fastapi, trace_prediction

app = FastAPI()
instrument_fastapi(app)  # No-op if OTel disabled

@app.post("/predict")
@trace_prediction(service="bankchurn")  # No-op decorator if OTel disabled
async def predict(data: CustomerData):
    ...
```

**The application code is identical** regardless of whether OTel is installed. No `if/else`, no `try/except`.

### Activation

```yaml
# K8s deployment — enable tracing in production
env:
  - name: OTEL_ENABLED
    value: "true"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
```

---

## Alternatives Considered

| Option | Verdict | Rationale |
|--------|---------|-----------|
| Jaeger client SDK | Rejected | Vendor-specific; OTel is the CNCF standard and supports any backend |
| OTel as hard dependency | Rejected | Forces 50MB overhead on dev/test/CI; breaks `pip install` without extras |
| **No-op fallback pattern** ✅ | **Selected** | Zero overhead when disabled; clean application code; CNCF-standard when enabled |
| Middleware-only tracing (no decorators) | Rejected | Loses ML-specific span semantics (`predict`, `validate`, `explain`) |

---

## Implementation

**`common_utils/telemetry.py`** exports:
- `init_telemetry(service_name)` — initializes OTel SDK or returns silently
- `get_tracer(name)` — returns real tracer or no-op proxy
- `instrument_fastapi(app)` — auto-instruments FastAPI routes or no-ops
- `@trace_prediction()` — decorator that creates a span with model name, latency, and prediction metadata
- `@trace_data_validation()` — decorator for data validation spans

**`common_utils/__init__.py`** (v1.2.0) exports `get_logger` and telemetry utilities.

---

## Consequences

- **Positive**: Production tracing with zero dev/test overhead — same code, different behavior per environment
- **Positive**: No Docker image bloat in environments that don't need OTel (~50MB saved)
- **Positive**: ML-specific spans provide richer observability than generic HTTP middleware
- **Positive**: Pattern is reusable — any new service gets tracing by importing `common_utils`
- **Negative**: OTel packages must be explicitly installed for tracing to work (not auto-included)
- **Negative**: No-op proxy means traces are silently dropped if misconfigured — requires health check

## Revisit When

- Full OTel Collector is deployed to the cluster — enable tracing in K8s deployments
- Adopting a service mesh (Istio/Linkerd) that provides automatic tracing — evaluate overlap
- Need distributed trace correlation across async tasks (Celery) — extend decorators

---

## References

- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [CNCF Observability Landscape](https://landscape.cncf.io/card-mode?category=observability-and-analysis)
- `common_utils/telemetry.py` — implementation
- `common_utils/__init__.py` — v1.2.0 with telemetry exports

</div>
