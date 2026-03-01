"""Configuration management for NLPInsight Analyzer.

Pydantic-validated configuration loaded from YAML.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DataConfig(BaseModel):
    """Data paths and processing settings."""

    train_path: str = "data/raw/train.csv"
    test_path: str = "data/raw/test.csv"
    text_column: str = "text"
    label_column: str = "label"
    max_length: int = Field(256, ge=32, le=512)
    labels: List[str] = ["negative", "neutral", "positive"]


class ModelConfig(BaseModel):
    """Model architecture and training hyperparameters."""

    pretrained_name: str = "distilbert-base-uncased"
    num_labels: int = 3
    learning_rate: float = Field(2e-5, gt=0)
    weight_decay: float = 0.01
    epochs: int = Field(3, ge=1)
    batch_size: int = Field(16, ge=1)
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    fp16: bool = False
    seed: int = 42
    early_stopping_patience: int = 2


class PathsConfig(BaseModel):
    """Output paths."""

    model_dir: str = "models"
    artifacts_dir: str = "artifacts"
    metrics_path: str = "artifacts/metrics.json"
    model_export_path: Optional[str] = "models/model.joblib"


class MLflowConfig(BaseModel):
    """MLflow tracking."""

    enabled: bool = False
    tracking_uri: str = "file:./mlruns"
    experiment_name: str = "nlpinsight"


class NLPInsightConfig(BaseModel):
    """Complete NLPInsight configuration."""

    data: DataConfig = DataConfig()
    model: ModelConfig = ModelConfig()
    paths: PathsConfig = PathsConfig()
    mlflow: MLflowConfig = MLflowConfig()

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "NLPInsightConfig":
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}

        logger.info(f"Loaded config from {config_path}")
        return cls(**config_dict)
