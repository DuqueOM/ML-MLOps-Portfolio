"""Tests for NLPInsight inference engine (dual backend)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import joblib
import pytest
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.nlpinsight.inference import LABEL_MAP, SentimentPredictor


@pytest.fixture
def sklearn_model_dir(tmp_path):
    """Create a temporary directory with a sklearn joblib model."""
    texts = [
        "revenue increased significantly",
        "profits were strong this quarter",
        "stock price dropped sharply",
        "losses exceeded expectations",
        "results were in line with forecasts",
        "no significant change in revenue",
    ]
    labels = [
        2,
        2,
        0,
        0,
        1,
        1,
    ]  # positive, positive, negative, negative, neutral, neutral

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=100)),
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(texts, labels)

    model_path = tmp_path / "model.joblib"
    joblib.dump(pipe, model_path)
    return tmp_path


@pytest.fixture
def sklearn_model_file(tmp_path):
    """Create a temporary .joblib file directly."""
    texts = ["good", "bad", "ok"]
    labels = [2, 0, 1]

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=50)),
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )
    pipe.fit(texts, labels)

    model_path = tmp_path / "sentiment.joblib"
    joblib.dump(pipe, model_path)
    return model_path


class TestLabelMap:
    def test_label_map_keys(self):
        assert set(LABEL_MAP.keys()) == {0, 1, 2}

    def test_label_map_values(self):
        assert set(LABEL_MAP.values()) == {"negative", "neutral", "positive"}


class TestSentimentPredictorSklearn:
    def test_load_from_directory(self, sklearn_model_dir):
        predictor = SentimentPredictor(model_path=sklearn_model_dir)
        assert predictor.backend == "sklearn"
        assert predictor.id2label == LABEL_MAP

    def test_load_from_file(self, sklearn_model_file):
        predictor = SentimentPredictor(model_path=sklearn_model_file)
        assert predictor.backend == "sklearn"

    def test_predict_single(self, sklearn_model_dir):
        predictor = SentimentPredictor(model_path=sklearn_model_dir)
        result = predictor.predict("revenue growth was excellent")
        assert "label" in result
        assert "confidence" in result
        assert result["label"] in {"negative", "neutral", "positive"}
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_with_all_scores(self, sklearn_model_dir):
        predictor = SentimentPredictor(model_path=sklearn_model_dir)
        result = predictor.predict("stock crashed", return_all_scores=True)
        assert "all_scores" in result
        assert len(result["all_scores"]) == 3

    def test_predict_batch(self, sklearn_model_dir):
        predictor = SentimentPredictor(model_path=sklearn_model_dir)
        results = predictor.predict_batch(
            ["good earnings", "bad quarter", "steady results"],
            return_all_scores=True,
        )
        assert len(results) == 3
        for r in results:
            assert "label" in r
            assert "confidence" in r
            assert "all_scores" in r

    def test_label2id_inverse(self, sklearn_model_dir):
        predictor = SentimentPredictor(model_path=sklearn_model_dir)
        for label, idx in predictor.label2id.items():
            assert predictor.id2label[idx] == label


class TestSentimentPredictorTransformerFallback:
    def test_falls_back_to_transformer_when_no_joblib(self, tmp_path):
        """When no joblib file exists, it should try to load transformer."""
        # Create an empty directory (no joblib, no transformer)
        with pytest.raises(Exception):
            SentimentPredictor(model_path=tmp_path)

    def test_find_joblib_nonexistent(self, tmp_path):
        """_find_joblib returns None for empty directory."""
        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = tmp_path
        assert predictor._find_joblib() is None

    def test_find_joblib_in_dir(self, sklearn_model_dir):
        """_find_joblib finds model.joblib in directory."""
        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = sklearn_model_dir
        result = predictor._find_joblib()
        assert result is not None
        assert result.name == "model.joblib"

    def test_find_joblib_direct_file(self, sklearn_model_file):
        """_find_joblib returns the file path for .joblib files."""
        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = sklearn_model_file
        result = predictor._find_joblib()
        assert result == sklearn_model_file


class TestSentimentPredictorTransformer:
    @patch("transformers.AutoModelForSequenceClassification")
    @patch("transformers.AutoTokenizer")
    def test_load_transformer(self, mock_tok_cls, mock_model_cls, tmp_path):
        """Test transformer loading path."""
        mock_model = MagicMock()
        mock_model.config.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        mock_model.config.label2id = {"negative": 0, "neutral": 1, "positive": 2}
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_tok_cls.from_pretrained.return_value = MagicMock()

        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = tmp_path
        predictor._load_transformer(device="cpu")

        assert predictor.backend == "transformer"
        assert predictor.device == "cpu"
        mock_model.to.assert_called_once_with("cpu")
        mock_model.eval.assert_called_once()

    @patch("transformers.AutoModelForSequenceClassification")
    @patch("transformers.AutoTokenizer")
    def test_predict_transformer_single(self, mock_tok_cls, mock_model_cls, tmp_path):
        """Test transformer prediction path."""
        # Setup mock model
        mock_model = MagicMock()
        mock_model.config.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        mock_model.config.label2id = {"negative": 0, "neutral": 1, "positive": 2}
        # Return logits that predict "positive" (index 2)
        logits = torch.tensor([[0.1, 0.2, 0.9]])
        mock_model.return_value = MagicMock(logits=logits)
        mock_model_cls.from_pretrained.return_value = mock_model

        # Setup mock tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": torch.tensor([[101, 2023, 102]]),
            "attention_mask": torch.tensor([[1, 1, 1]]),
        }
        mock_tok_cls.from_pretrained.return_value = mock_tokenizer

        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = tmp_path
        predictor._load_transformer(device="cpu")

        result = predictor.predict("good earnings")
        assert result["label"] == "positive"
        assert 0.0 <= result["confidence"] <= 1.0

    @patch("transformers.AutoModelForSequenceClassification")
    @patch("transformers.AutoTokenizer")
    def test_predict_transformer_batch_all_scores(self, mock_tok_cls, mock_model_cls, tmp_path):
        """Test transformer batch prediction with all_scores."""
        mock_model = MagicMock()
        mock_model.config.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        mock_model.config.label2id = {"negative": 0, "neutral": 1, "positive": 2}
        logits = torch.tensor([[0.1, 0.2, 0.9], [0.8, 0.1, 0.1]])
        mock_model.return_value = MagicMock(logits=logits)
        mock_model_cls.from_pretrained.return_value = mock_model

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": torch.tensor([[101, 102], [101, 102]]),
            "attention_mask": torch.tensor([[1, 1], [1, 1]]),
        }
        mock_tok_cls.from_pretrained.return_value = mock_tokenizer

        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = tmp_path
        predictor._load_transformer(device="cpu")

        results = predictor.predict_batch(["good", "bad"], return_all_scores=True)
        assert len(results) == 2
        assert results[0]["label"] == "positive"
        assert results[1]["label"] == "negative"
        assert "all_scores" in results[0]
        assert len(results[0]["all_scores"]) == 3

    @patch("transformers.AutoModelForSequenceClassification")
    @patch("transformers.AutoTokenizer")
    def test_predict_batch_routes_to_transformer(self, mock_tok_cls, mock_model_cls, tmp_path):
        """predict_batch routes to _predict_transformer when backend is transformer."""
        mock_model = MagicMock()
        mock_model.config.id2label = {0: "neg", 1: "pos"}
        mock_model.config.label2id = {"neg": 0, "pos": 1}
        logits = torch.tensor([[0.9, 0.1]])
        mock_model.return_value = MagicMock(logits=logits)
        mock_model_cls.from_pretrained.return_value = mock_model

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": torch.tensor([[101, 102]]),
            "attention_mask": torch.tensor([[1, 1]]),
        }
        mock_tok_cls.from_pretrained.return_value = mock_tokenizer

        predictor = SentimentPredictor.__new__(SentimentPredictor)
        predictor.model_path = tmp_path
        predictor._load_transformer(device="cpu")

        results = predictor.predict_batch(["test"])
        assert len(results) == 1
        assert results[0]["label"] == "neg"
