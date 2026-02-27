"""Common utilities for ML/MLOps portfolio.

This package provides shared functionality across all projects including:
- Seed management for reproducibility
- Model persistence with compression and integrity validation
"""

from __future__ import annotations

from .model_persistence import load_model, save_model
from .seed import DEFAULT_SEED, set_seed

__version__ = "1.0.0"
__all__ = ["set_seed", "DEFAULT_SEED", "save_model", "load_model"]
