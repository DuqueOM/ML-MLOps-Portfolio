"""Tests for NLPInsight configuration."""

import pytest

from src.nlpinsight.config import DataConfig, ModelConfig, NLPInsightConfig, PathsConfig


class TestDataConfig:
    def test_defaults(self):
        cfg = DataConfig()
        assert cfg.text_column == "text"
        assert cfg.label_column == "label"
        assert cfg.max_length == 256

    def test_max_length_validation(self):
        with pytest.raises(Exception):
            DataConfig(max_length=10)  # below 32


class TestModelConfig:
    def test_defaults(self):
        cfg = ModelConfig()
        assert cfg.pretrained_name == "distilbert-base-uncased"
        assert cfg.num_labels == 3
        assert cfg.learning_rate == 2e-5

    def test_learning_rate_positive(self):
        with pytest.raises(Exception):
            ModelConfig(learning_rate=-1)


class TestNLPInsightConfig:
    def test_from_yaml(self, config_path):
        cfg = NLPInsightConfig.from_yaml(config_path)
        assert cfg.model.pretrained_name == "distilbert-base-uncased"
        assert cfg.data.labels == ["negative", "neutral", "positive"]

    def test_from_yaml_missing_file(self):
        with pytest.raises(FileNotFoundError):
            NLPInsightConfig.from_yaml("nonexistent.yaml")

    def test_defaults(self):
        cfg = NLPInsightConfig()
        assert isinstance(cfg.data, DataConfig)
        assert isinstance(cfg.model, ModelConfig)
        assert isinstance(cfg.paths, PathsConfig)
