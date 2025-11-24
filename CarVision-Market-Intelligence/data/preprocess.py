"""
Deprecated: Use src.carvision.data instead.
"""

from src.carvision.data import (
    build_preprocessor,
    clean_data,
    infer_feature_types,
    load_data,
    load_split_indices,
    save_split_indices,
    split_data,
)

__all__ = [
    "load_data",
    "clean_data",
    "infer_feature_types",
    "build_preprocessor",
    "split_data",
    "save_split_indices",
    "load_split_indices",
]
