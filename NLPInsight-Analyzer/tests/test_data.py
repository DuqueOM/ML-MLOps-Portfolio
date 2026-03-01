"""Tests for NLPInsight data loading and processing."""

import pandas as pd
import pytest

from src.nlpinsight.data import TextDataset, encode_labels, load_dataset, split_dataset


class TestLoadDataset:
    def test_load_valid_csv(self, tmp_path):
        df = pd.DataFrame({"text": ["hello", "world"], "label": [0, 1]})
        path = tmp_path / "test.csv"
        df.to_csv(path, index=False)

        result = load_dataset(path)
        assert len(result) == 2
        assert "text" in result.columns

    def test_missing_column_raises(self, tmp_path):
        df = pd.DataFrame({"content": ["hello"], "label": [0]})
        path = tmp_path / "test.csv"
        df.to_csv(path, index=False)

        with pytest.raises(ValueError, match="Missing required column"):
            load_dataset(path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_dataset("nonexistent.csv")

    def test_drops_nan_text(self, tmp_path):
        df = pd.DataFrame({"text": ["hello", None, "world"], "label": [0, 1, 0]})
        path = tmp_path / "test.csv"
        df.to_csv(path, index=False)

        result = load_dataset(path)
        assert len(result) == 2


class TestEncodeLabels:
    def test_encode_string_labels(self):
        df = pd.DataFrame({"text": ["a", "b", "c"], "label": ["pos", "neg", "pos"]})
        result, l2id, id2l = encode_labels(df, label_names=["neg", "pos"])
        assert l2id == {"neg": 0, "pos": 1}
        assert id2l == {0: "neg", 1: "pos"}
        assert result["label"].tolist() == [1, 0, 1]

    def test_auto_detect_labels(self):
        df = pd.DataFrame({"text": ["a", "b"], "label": ["negative", "positive"]})
        result, l2id, _ = encode_labels(df)
        assert "negative" in l2id
        assert "positive" in l2id

    def test_handles_unknown_labels(self):
        df = pd.DataFrame({"text": ["a", "b"], "label": ["pos", "unknown"]})
        result, _, _ = encode_labels(df, label_names=["neg", "pos"])
        assert len(result) == 1  # unknown label dropped


class TestSplitDataset:
    def test_split_sizes(self):
        df = pd.DataFrame({"text": [f"t{i}" for i in range(100)], "label": [0] * 50 + [1] * 50})
        train, val = split_dataset(df, val_size=0.2, seed=42)
        assert len(train) == 80
        assert len(val) == 20

    def test_stratified_split(self):
        df = pd.DataFrame({"text": [f"t{i}" for i in range(100)], "label": [0] * 80 + [1] * 20})
        train, val = split_dataset(df, val_size=0.2, seed=42)
        # Roughly proportional (±1 due to rounding)
        train_ratio = train["label"].mean()
        assert 0.15 <= train_ratio <= 0.25


class TestTextDataset:
    def test_dataset_length(self, sample_texts, sample_labels):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not installed")

        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        ds = TextDataset(sample_texts, sample_labels, tokenizer, max_length=64)
        assert len(ds) == len(sample_texts)

    def test_dataset_item_keys(self, sample_texts, sample_labels):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not installed")

        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        ds = TextDataset(sample_texts, sample_labels, tokenizer, max_length=64)
        item = ds[0]
        assert "input_ids" in item
        assert "attention_mask" in item
        assert "labels" in item

    def test_dataset_item_shapes(self, sample_texts, sample_labels):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            pytest.skip("transformers not installed")

        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        ds = TextDataset(sample_texts, sample_labels, tokenizer, max_length=64)
        item = ds[0]
        assert item["input_ids"].shape[0] == 64
        assert item["attention_mask"].shape[0] == 64
