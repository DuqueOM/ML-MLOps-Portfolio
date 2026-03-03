# ADR-004: OpenTelemetry with Graceful No-Op Fallback

**Status**: Accepted  
**Date**: 2026-03-03  
**Decision Makers**: DuqueOM

## Context

Need distributed tracing across 3 FastAPI ML services for production observability. OpenTelemetry is the CNCF standard but adds heavy dependencies (~50MB). Not all environments (dev, test, CI) need tracing.

## Decision

Implement OpenTelemetry via `common_utils/telemetry.py` with environment-controlled activation (`OTEL_ENABLED=true`) and graceful no-op fallback when OTel packages are not installed.

## Rationale

- **Zero overhead** in dev/test: functions return immediately if OTel is disabled or missing
- **No import errors**: try/except guards around all OTel imports
- **ML-specific spans**: `@trace_prediction()`, `@trace_data_validation()` decorators
- **Shared module**: same telemetry code across all 3 services via `common_utils/`

## Consequences

- **Positive**: Tracing available in production without impacting dev workflow
- **Positive**: No additional Docker image size in environments without OTel
- **Negative**: OTel packages must be installed separately for tracing to work
