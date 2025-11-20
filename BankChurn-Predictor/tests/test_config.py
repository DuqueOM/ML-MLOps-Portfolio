"""Tests for configuration management."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.bankchurn.config import BankChurnConfig, DataConfig, MLflowConfig, ModelConfig


class TestModelConfig:
    """Test ModelConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ModelConfig()
        assert config.test_size == 0.2
        assert config.random_state == 42
        assert config.cv_folds == 5
        assert config.ensemble_voting == "soft"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ModelConfig(
            test_size=0.3,
            random_state=123,
            cv_folds=10,
            ensemble_voting="hard",
        )
        assert config.test_size == 0.3
        assert config.random_state == 123
        assert config.cv_folds == 10
        assert config.ensemble_voting == "hard"

    def test_test_size_validation(self):
        """Test test_size bounds validation."""
        with pytest.raises(ValidationError):
            ModelConfig(test_size=1.5)  # > 1.0

        with pytest.raises(ValidationError):
            ModelConfig(test_size=-0.1)  # < 0.0

    def test_cv_folds_validation(self):
        """Test cv_folds minimum validation."""
        with pytest.raises(ValidationError):
            ModelConfig(cv_folds=1)  # < 2

    def test_ensemble_voting_validation(self):
        """Test ensemble_voting pattern validation."""
        with pytest.raises(ValidationError):
            ModelConfig(ensemble_voting="invalid")


class TestDataConfig:
    """Test DataConfig class."""

    def test_default_values(self):
        """Test default data configuration."""
        config = DataConfig()
        assert config.target_column == "Exited"
        assert config.categorical_features == []
        assert config.numerical_features == []
        assert config.drop_columns == []

    def test_custom_features(self):
        """Test custom feature lists."""
        config = DataConfig(
            categorical_features=["Gender", "Geography"],
            numerical_features=["Age", "Balance"],
            drop_columns=["CustomerId"],
        )
        assert len(config.categorical_features) == 2
        assert len(config.numerical_features) == 2
        assert len(config.drop_columns) == 1


class TestMLflowConfig:
    """Test MLflowConfig class."""

    def test_default_values(self):
        """Test default MLflow configuration."""
        config = MLflowConfig()
        assert config.tracking_uri == "file:./mlruns"
        assert config.experiment_name == "bankchurn"
        assert config.enabled is True

    def test_custom_mlflow_config(self):
        """Test custom MLflow settings."""
        config = MLflowConfig(
            tracking_uri="http://localhost:5000",
            experiment_name="production",
            enabled=False,
        )
        assert config.tracking_uri == "http://localhost:5000"
        assert config.experiment_name == "production"
        assert config.enabled is False


class TestBankChurnConfig:
    """Test complete BankChurnConfig class."""

    @pytest.fixture
    def sample_config_dict(self):
        """Sample configuration dictionary."""
        return {
            "model": {
                "test_size": 0.25,
                "random_state": 42,
                "cv_folds": 5,
                "ensemble_voting": "soft",
            },
            "data": {
                "target_column": "Exited",
                "categorical_features": ["Gender", "Geography"],
                "numerical_features": ["Age", "Balance", "CreditScore"],
                "drop_columns": ["CustomerId", "Surname"],
            },
            "mlflow": {
                "tracking_uri": "file:./mlruns",
                "experiment_name": "bankchurn",
                "enabled": True,
            },
        }

    def test_from_dict(self, sample_config_dict):
        """Test creating config from dictionary."""
        config = BankChurnConfig(**sample_config_dict)
        assert config.model.test_size == 0.25
        assert len(config.data.categorical_features) == 2
        assert config.mlflow.enabled is True

    def test_from_yaml(self, sample_config_dict):
        """Test loading config from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(sample_config_dict, f)
            temp_path = f.name

        try:
            config = BankChurnConfig.from_yaml(temp_path)
            assert config.model.test_size == 0.25
            assert len(config.data.categorical_features) == 2
        finally:
            Path(temp_path).unlink()

    def test_from_yaml_file_not_found(self):
        """Test that from_yaml raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            BankChurnConfig.from_yaml("nonexistent.yaml")

    def test_to_dict(self, sample_config_dict):
        """Test converting config to dictionary."""
        config = BankChurnConfig(**sample_config_dict)
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "model" in config_dict
        assert "data" in config_dict
        assert "mlflow" in config_dict
        assert config_dict["model"]["test_size"] == 0.25

    def test_nested_access(self, sample_config_dict):
        """Test accessing nested configuration values."""
        config = BankChurnConfig(**sample_config_dict)
        assert config.model.random_state == 42
        assert config.data.target_column == "Exited"
        assert config.mlflow.experiment_name == "bankchurn"

    def test_invalid_config_raises_validation_error(self):
        """Test that invalid config raises ValidationError."""
        invalid_config = {
            "model": {"test_size": 2.0},  # Invalid: > 1.0
            "data": {"target_column": "Exited"},
            "mlflow": {"tracking_uri": "file:./mlruns", "experiment_name": "test", "enabled": True},
        }

        with pytest.raises(ValidationError):
            BankChurnConfig(**invalid_config)
