"""Soluciones del Módulo 01 — Python Moderno."""

from .config import DataConfig, ModelConfig, TrainingConfig
from .mathops import add, mean, multiply, normalize, std

__all__ = [
    "ModelConfig",
    "DataConfig",
    "TrainingConfig",
    "add",
    "multiply",
    "mean",
    "std",
    "normalize",
]
