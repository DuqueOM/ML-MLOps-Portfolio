"""Configuration management for TelecomAI Customer Intelligence.

Handles loading and validation of YAML configuration files with Pydantic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class PathsConfig(BaseModel):
    """File paths configuration."""

    data_csv: str = Field(..., description="Path to raw data CSV file")
    artifacts_dir: str = Field(default="artifacts", description="Directory for artifacts")
    model_path: str = Field(default="artifacts/model.joblib", description="Model file path")
    preprocessor_path: str = Field(default="artifacts/preprocessor.joblib", description="Preprocessor file path")
    metrics_path: str = Field(default="artifacts/metrics.json", description="Metrics JSON path")
    confusion_matrix_path: str = Field(
        default="artifacts/confusion_matrix.png", description="Confusion matrix plot path"
    )
    roc_curve_path: str = Field(default="artifacts/roc_curve.png", description="ROC curve plot path")
    model_export_path: str = Field(default="models/model_v1.0.0.pkl", description="Model export path for production")


class SplitConfig(BaseModel):
    """Train/test split configuration."""

    test_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Test set proportion")
    stratify: bool = Field(default=True, description="Use stratified split")

    @field_validator("test_size")
    @classmethod
    def validate_test_size(cls, v: float) -> float:
        """Validate test size is reasonable."""
        if v < 0.05 or v > 0.5:
            logger.warning(f"Test size {v} is unusual (recommended: 0.1-0.3)")
        return v


class ModelConfig(BaseModel):
    """Model configuration."""

    name: str = Field(
        default="gradient_boosting",
        pattern="^(gradient_boosting|random_forest|logistic_regression)$",
        description="Model type",
    )
    params: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")

    @field_validator("params")
    @classmethod
    def validate_params(cls, v: Dict[str, Any], info) -> Dict[str, Any]:
        """Validate model-specific parameters."""
        model_name = info.data.get("name", "")

        if model_name == "gradient_boosting":
            if "n_estimators" in v and (v["n_estimators"] < 10 or v["n_estimators"] > 1000):
                raise ValueError(f"n_estimators must be between 10 and 1000, got {v['n_estimators']}")
            if "max_depth" in v and (v["max_depth"] < 1 or v["max_depth"] > 20):
                raise ValueError(f"max_depth must be between 1 and 20, got {v['max_depth']}")
            if "learning_rate" in v and (v["learning_rate"] <= 0 or v["learning_rate"] > 1):
                raise ValueError(f"learning_rate must be between 0 and 1, got {v['learning_rate']}")

        return v


class MLflowConfig(BaseModel):
    """MLflow tracking configuration."""

    enable: bool = Field(default=True, description="Enable MLflow tracking")
    experiment: str = Field(default="TelecomAI", description="Experiment name")
    tracking_uri: str = Field(default="file:./mlruns", description="MLflow tracking URI")


class Config(BaseModel):
    """Complete TelecomAI configuration."""

    project_name: str = Field(default="TelecomAI-Customer-Intelligence")
    random_seed: int = Field(default=42, ge=0, description="Global random seed")
    paths: PathsConfig
    features: List[str] = Field(
        default_factory=lambda: ["calls", "minutes", "messages", "mb_used"],
        min_length=1,
        description="Feature column names",
    )
    target: str = Field(default="is_ultra", description="Target column name")
    split: SplitConfig = Field(default_factory=SplitConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification threshold")
    mlflow: Optional[MLflowConfig] = Field(default_factory=MLflowConfig)

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: List[str]) -> List[str]:
        """Validate feature list is not empty and has no duplicates."""
        if not v:
            raise ValueError("Features list cannot be empty")
        if len(v) != len(set(v)):
            raise ValueError(f"Duplicate features found: {v}")
        return v

    @classmethod
    def from_yaml(cls, path: str | Path) -> Config:
        """Load configuration from YAML file.

        Parameters
        ----------
        path : str or Path
            Path to YAML configuration file.

        Returns
        -------
        config : Config
            Validated configuration object.

        Raises
        ------
        FileNotFoundError
            If config file doesn't exist.
        yaml.YAMLError
            If YAML parsing fails.
        ValidationError
            If config validation fails.
        """
        config_path = Path(path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            raise

        if config_dict is None:
            raise ValueError(f"Config file is empty: {config_path}")

        logger.info(f"Loaded configuration from {config_path}")
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns
        -------
        dict
            Configuration as nested dictionary.
        """
        return self.model_dump()

    def save_yaml(self, output_path: str | Path) -> None:
        """Save configuration to YAML file.

        Parameters
        ----------
        output_path : str or Path
            Path to save YAML file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved configuration to {output_path}")
