"""Common utilities for ML/MLOps portfolio.

This package provides shared functionality across all projects including:
- Seed management for reproducibility
- Model persistence with compression and integrity validation
- OpenTelemetry distributed tracing
"""

from __future__ import annotations

from .logging import get_logger
from .model_persistence import load_model, save_model
from .seed import DEFAULT_SEED, set_seed
from .telemetry import get_tracer, init_telemetry, instrument_fastapi

__version__ = "1.2.0"
__all__ = [
    "set_seed",
    "DEFAULT_SEED",
    "save_model",
    "load_model",
    "init_telemetry",
    "get_tracer",
    "instrument_fastapi",
    "get_logger",
]
