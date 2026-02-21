"""Configuration management for CarVision Market Intelligence.

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

    data_path: str = Field(..., description="Path to raw data CSV file")
    artifacts_dir: str = Field(default="artifacts", description="Directory for artifacts")
    model_path: str = Field(default="models/model.joblib", description="Model file path")
    metrics_path: str = Field(default="artifacts/metrics.json", description="Metrics JSON path")
    baseline_metrics_path: str = Field(default="artifacts/metrics_baseline.json", description="Baseline metrics path")
    split_indices_path: str = Field(default="artifacts/split_indices.json", description="Split indices path")


class RandomForestParams(BaseModel):
    """Random Forest hyperparameters."""

    n_estimators: int = Field(default=300, ge=10, le=1000, description="Number of trees")
    max_depth: Optional[int] = Field(default=12, ge=1, le=50, description="Maximum tree depth")
    min_samples_leaf: int = Field(default=2, ge=1, le=20, description="Minimum samples per leaf")
    n_jobs: int = Field(default=-1, description="Number of parallel jobs (-1 = all cores)")

    @field_validator("n_jobs")
    @classmethod
    def validate_n_jobs(cls, v: int) -> int:
        """Validate n_jobs is -1 or positive."""
        if v != -1 and v < 1:
            raise ValueError("n_jobs must be -1 (all cores) or a positive integer")
        return v


class TrainingConfig(BaseModel):
    """Training configuration."""

    target: str = Field(default="price", description="Target column name")
    test_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Test set proportion")
    val_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Validation set proportion")
    shuffle: bool = Field(default=True, description="Shuffle data before split")
    model: str = Field(default="random_forest", pattern="^(random_forest|linear|ridge)$")
    random_forest_params: RandomForestParams = Field(default_factory=RandomForestParams)
    baseline: str = Field(default="dummy_median", description="Baseline model type")

    @field_validator("test_size", "val_size")
    @classmethod
    def validate_split_sizes(cls, v: float) -> float:
        """Validate split sizes are reasonable."""
        if v < 0.05 or v > 0.5:
            logger.warning(f"Split size {v} is unusual (recommended: 0.1-0.3)")
        return v


class FiltersConfig(BaseModel):
    """Data filtering configuration."""

    min_price: float = Field(default=1000, ge=0, description="Minimum valid price")
    max_price: float = Field(default=500000, ge=1000, description="Maximum valid price")
    min_year: int = Field(default=1990, ge=1900, le=2030, description="Minimum model year")
    max_odometer: float = Field(default=500000, ge=0, description="Maximum odometer reading")

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, v: float, info) -> float:
        """Ensure max_price > min_price."""
        if "min_price" in info.data and v <= info.data["min_price"]:
            raise ValueError(f"max_price ({v}) must be greater than min_price ({info.data['min_price']})")
        return v


class PreprocessingConfig(BaseModel):
    """Preprocessing configuration."""

    filters: FiltersConfig = Field(default_factory=FiltersConfig)
    numeric_imputer: str = Field(default="median", pattern="^(mean|median|most_frequent)$")
    scale_numeric: bool = Field(default=True, description="Apply StandardScaler to numeric features")
    categorical_imputer: str = Field(default="most_frequent", pattern="^(most_frequent|constant)$")
    handle_unknown_category: str = Field(default="ignore", pattern="^(ignore|error)$")
    drop_columns: List[str] = Field(
        default_factory=lambda: ["price_per_mile", "price_category"],
        description="Columns to drop (prevent data leakage)",
    )
    numeric_features: List[str] = Field(default_factory=list, description="Numeric features (empty = auto-detect)")
    categorical_features: List[str] = Field(
        default_factory=list, description="Categorical features (empty = auto-detect)"
    )


class BootstrapConfig(BaseModel):
    """Bootstrap evaluation configuration."""

    enabled: bool = Field(default=True, description="Enable bootstrap confidence intervals")
    n_resamples: int = Field(default=200, ge=50, le=10000, description="Number of bootstrap samples")
    random_state: int = Field(default=42, description="Random seed for reproducibility")


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""

    metrics: List[str] = Field(default_factory=lambda: ["rmse", "mae", "mape", "r2"], description="Metrics to compute")
    bootstrap: BootstrapConfig = Field(default_factory=BootstrapConfig)

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: List[str]) -> List[str]:
        """Validate metric names."""
        valid_metrics = {"rmse", "mae", "mape", "r2", "mse"}
        invalid = set(v) - valid_metrics
        if invalid:
            raise ValueError(f"Invalid metrics: {invalid}. Valid: {valid_metrics}")
        return v


class CarVisionConfig(BaseModel):
    """Complete CarVision configuration."""

    project_name: str = Field(default="CarVision-Market-Intelligence")
    seed: int = Field(default=42, ge=0, description="Global random seed")
    dataset_year: int = Field(default=2024, ge=2000, le=2030, description="Dataset year")
    paths: PathsConfig
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> CarVisionConfig:
        """Load configuration from YAML file.

        Parameters
        ----------
        config_path : str or Path
            Path to YAML configuration file.

        Returns
        -------
        config : CarVisionConfig
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
        config_path = Path(config_path)

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
