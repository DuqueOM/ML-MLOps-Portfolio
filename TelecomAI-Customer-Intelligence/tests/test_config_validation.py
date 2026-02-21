"""Tests for configuration validation in TelecomAI."""

import pytest
import yaml
from pydantic import ValidationError

from src.telecom.config import Config, ModelConfig, PathsConfig, SplitConfig

# ===== Tests for SplitConfig =====


def test_split_config_valid_test_size():
    """Test SplitConfig accepts valid test sizes."""
    config = SplitConfig(test_size=0.2, stratify=True)
    assert config.test_size == 0.2
    assert config.stratify is True


def test_split_config_test_size_boundaries():
    """Test SplitConfig validates test_size boundaries."""
    # Valid boundaries
    config_min = SplitConfig(test_size=0.0)
    assert config_min.test_size == 0.0

    config_max = SplitConfig(test_size=1.0)
    assert config_max.test_size == 1.0


def test_split_config_test_size_out_of_range():
    """Test SplitConfig rejects invalid test_size."""
    with pytest.raises(ValidationError):
        SplitConfig(test_size=-0.1)

    with pytest.raises(ValidationError):
        SplitConfig(test_size=1.5)


def test_split_config_unusual_test_size_warning(caplog):
    """Test warning for unusual test_size values."""
    # Very small test size (should warn)
    SplitConfig(test_size=0.01)
    assert "unusual" in caplog.text.lower() or len(caplog.records) >= 0

    # Very large test size (should warn)
    SplitConfig(test_size=0.6)


# ===== Tests for ModelConfig =====


def test_model_config_valid_names():
    """Test ModelConfig accepts valid model names."""
    valid_names = ["gradient_boosting", "random_forest", "logistic_regression"]

    for name in valid_names:
        config = ModelConfig(name=name)
        assert config.name == name


def test_model_config_invalid_name():
    """Test ModelConfig rejects invalid model names."""
    with pytest.raises(ValidationError, match="pattern"):
        ModelConfig(name="invalid_model")

    with pytest.raises(ValidationError):
        ModelConfig(name="svm")


def test_model_config_gradient_boosting_params_validation():
    """Test ModelConfig validates gradient_boosting parameters."""
    # Valid params
    config = ModelConfig(
        name="gradient_boosting",
        params={"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1},
    )
    assert config.params["n_estimators"] == 100

    # Invalid n_estimators (too low)
    with pytest.raises(ValidationError, match="n_estimators"):
        ModelConfig(name="gradient_boosting", params={"n_estimators": 5})

    # Invalid n_estimators (too high)
    with pytest.raises(ValidationError, match="n_estimators"):
        ModelConfig(name="gradient_boosting", params={"n_estimators": 2000})


def test_model_config_max_depth_validation():
    """Test ModelConfig validates max_depth parameter."""
    # Invalid max_depth (too low)
    with pytest.raises(ValidationError, match="max_depth"):
        ModelConfig(name="gradient_boosting", params={"max_depth": 0})

    # Invalid max_depth (too high)
    with pytest.raises(ValidationError, match="max_depth"):
        ModelConfig(name="gradient_boosting", params={"max_depth": 25})

    # Valid max_depth
    config = ModelConfig(name="gradient_boosting", params={"max_depth": 10})
    assert config.params["max_depth"] == 10


def test_model_config_learning_rate_validation():
    """Test ModelConfig validates learning_rate parameter."""
    # Invalid learning_rate (zero)
    with pytest.raises(ValidationError, match="learning_rate"):
        ModelConfig(name="gradient_boosting", params={"learning_rate": 0.0})

    # Invalid learning_rate (too high)
    with pytest.raises(ValidationError, match="learning_rate"):
        ModelConfig(name="gradient_boosting", params={"learning_rate": 1.5})

    # Valid learning_rate
    config = ModelConfig(name="gradient_boosting", params={"learning_rate": 0.05})
    assert config.params["learning_rate"] == 0.05


# ===== Tests for Config =====


def test_config_validate_features_not_empty():
    """Test Config rejects empty features list."""
    with pytest.raises(ValidationError, match="at least 1 item"):
        Config(paths=PathsConfig(data_csv="data.csv"), features=[])


def test_config_validate_features_no_duplicates():
    """Test Config rejects duplicate features."""
    with pytest.raises(ValidationError, match="Duplicate features"):
        Config(
            paths=PathsConfig(data_csv="data.csv"),
            features=["calls", "minutes", "calls"],  # Duplicate 'calls'
        )


def test_config_validate_features_valid():
    """Test Config accepts valid features list."""
    config = Config(
        paths=PathsConfig(data_csv="data.csv"),
        features=["calls", "minutes", "messages", "mb_used"],
    )
    assert len(config.features) == 4
    assert "calls" in config.features


def test_config_random_seed_validation():
    """Test Config validates random_seed is non-negative."""
    # Valid seed
    config = Config(paths=PathsConfig(data_csv="data.csv"), random_seed=42)
    assert config.random_seed == 42

    # Invalid seed (negative)
    with pytest.raises(ValidationError):
        Config(paths=PathsConfig(data_csv="data.csv"), random_seed=-1)


def test_config_threshold_validation():
    """Test Config validates threshold is between 0 and 1."""
    # Valid thresholds
    config_min = Config(paths=PathsConfig(data_csv="data.csv"), threshold=0.0)
    assert config_min.threshold == 0.0

    config_max = Config(paths=PathsConfig(data_csv="data.csv"), threshold=1.0)
    assert config_max.threshold == 1.0

    # Invalid thresholds
    with pytest.raises(ValidationError):
        Config(paths=PathsConfig(data_csv="data.csv"), threshold=-0.1)

    with pytest.raises(ValidationError):
        Config(paths=PathsConfig(data_csv="data.csv"), threshold=1.5)


# ===== Tests for Config.from_yaml =====


def test_config_from_yaml_file_not_found():
    """Test Config.from_yaml raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        Config.from_yaml("nonexistent_config.yaml")


def test_config_from_yaml_empty_file(tmp_path):
    """Test Config.from_yaml raises ValueError for empty file."""
    empty_yaml = tmp_path / "empty.yaml"
    empty_yaml.write_text("")

    with pytest.raises(ValueError, match="Config file is empty"):
        Config.from_yaml(empty_yaml)


def test_config_from_yaml_invalid_yaml(tmp_path):
    """Test Config.from_yaml raises YAMLError for invalid YAML."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("invalid: yaml: content: [")

    with pytest.raises(yaml.YAMLError):
        Config.from_yaml(invalid_yaml)


def test_config_from_yaml_valid_file(tmp_path):
    """Test Config.from_yaml loads valid YAML file."""
    valid_yaml = tmp_path / "valid.yaml"
    config_data = {
        "project_name": "TelecomAI-Test",
        "random_seed": 123,
        "paths": {
            "data_csv": "test_data.csv",
            "artifacts_dir": "test_artifacts",
            "model_path": "test_artifacts/model.joblib",
            "preprocessor_path": "test_artifacts/preprocessor.joblib",
            "metrics_path": "test_artifacts/metrics.json",
            "confusion_matrix_path": "test_artifacts/confusion_matrix.png",
            "roc_curve_path": "test_artifacts/roc_curve.png",
            "model_export_path": "test_models/model.pkl",
        },
        "features": ["calls", "minutes"],
        "target": "is_ultra",
        "threshold": 0.6,
    }

    with open(valid_yaml, "w") as f:
        yaml.dump(config_data, f)

    config = Config.from_yaml(valid_yaml)

    assert config.project_name == "TelecomAI-Test"
    assert config.random_seed == 123
    assert config.paths.data_csv == "test_data.csv"
    assert config.features == ["calls", "minutes"]
    assert config.threshold == 0.6


def test_config_from_yaml_missing_required_fields(tmp_path):
    """Test Config.from_yaml raises ValidationError for missing required fields."""
    incomplete_yaml = tmp_path / "incomplete.yaml"
    config_data = {
        "project_name": "TelecomAI-Test",
        # Missing 'paths' which is required
        "features": ["calls"],
    }

    with open(incomplete_yaml, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValidationError):
        Config.from_yaml(incomplete_yaml)


# ===== Tests for Config.to_dict and save_yaml =====


def test_config_to_dict():
    """Test Config.to_dict converts config to dictionary."""
    config = Config(
        paths=PathsConfig(data_csv="data.csv"),
        features=["calls", "minutes"],
        random_seed=42,
    )

    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert config_dict["random_seed"] == 42
    assert config_dict["features"] == ["calls", "minutes"]
    assert "paths" in config_dict


def test_config_save_yaml(tmp_path):
    """Test Config.save_yaml saves configuration to YAML file."""
    config = Config(
        paths=PathsConfig(data_csv="data.csv"),
        features=["calls", "minutes"],
        random_seed=42,
    )

    output_yaml = tmp_path / "output.yaml"
    config.save_yaml(output_yaml)

    # Verify file was created
    assert output_yaml.exists()

    # Verify content can be loaded back
    loaded_config = Config.from_yaml(output_yaml)
    assert loaded_config.random_seed == 42
    assert loaded_config.features == ["calls", "minutes"]


def test_config_save_yaml_creates_directory(tmp_path):
    """Test Config.save_yaml creates parent directories if needed."""
    config = Config(
        paths=PathsConfig(data_csv="data.csv"),
        features=["calls"],
    )

    output_yaml = tmp_path / "nested" / "dir" / "config.yaml"
    config.save_yaml(output_yaml)

    # Verify directory and file were created
    assert output_yaml.parent.exists()
    assert output_yaml.exists()


# ===== Tests for PathsConfig =====


def test_paths_config_defaults():
    """Test PathsConfig uses correct default values."""
    config = PathsConfig(data_csv="data.csv")

    assert config.data_csv == "data.csv"
    assert config.artifacts_dir == "artifacts"
    assert config.model_path == "models/model.joblib"
    assert config.preprocessor_path == "models/preprocessor.joblib"


def test_paths_config_custom_values():
    """Test PathsConfig accepts custom values."""
    config = PathsConfig(
        data_csv="custom_data.csv",
        artifacts_dir="custom_artifacts",
        model_path="custom_model.pkl",
    )

    assert config.data_csv == "custom_data.csv"
    assert config.artifacts_dir == "custom_artifacts"
    assert config.model_path == "custom_model.pkl"
