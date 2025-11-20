"""Common utilities for ML/MLOps portfolio.

This package provides shared functionality across all projects including:
- Seed management for reproducibility
- Configuration helpers
- Logging utilities
"""

from __future__ import annotations

from .seed import DEFAULT_SEED, set_seed

__version__ = "1.0.0"
__all__ = ["set_seed", "DEFAULT_SEED"]
