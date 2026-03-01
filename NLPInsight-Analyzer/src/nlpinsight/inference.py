"""Inference engine for sentiment analysis.

Provides a unified interface for loading fine-tuned models and running
predictions. Supports both HuggingFace transformers and sklearn/joblib models.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}


class SentimentPredictor:
    """Load a sentiment model and predict.

    Supports two backends:
    - HuggingFace transformers (directory with tokenizer + model)
    - sklearn/joblib pipeline (single .joblib file with TF-IDF + classifier)

    Parameters
    ----------
    model_path : str or Path
        Directory with transformer model, or path to .joblib file.
    device : str, optional
        ``"cpu"`` or ``"cuda"``. Only used for transformer backend.
    """

    def __init__(self, model_path: str | Path, device: Optional[str] = None):
        self.model_path = Path(model_path)
        self.backend = None

        # Try joblib first (fast, no GPU needed)
        joblib_path = self._find_joblib()
        if joblib_path:
            self._load_joblib(joblib_path)
        else:
            self._load_transformer(device)

    def _find_joblib(self) -> Optional[Path]:
        """Find a joblib model file."""
        if self.model_path.suffix == ".joblib" and self.model_path.is_file():
            return self.model_path
        if self.model_path.is_dir():
            for candidate in ["model.joblib", "pipeline.joblib"]:
                p = self.model_path / candidate
                if p.is_file():
                    return p
        return None

    def _load_joblib(self, path: Path) -> None:
        """Load a sklearn pipeline from joblib."""
        import joblib

        logger.info(f"Loading sklearn model from {path}")
        self.model = joblib.load(path)
        self.backend = "sklearn"
        self.id2label = LABEL_MAP
        self.label2id = {v: k for k, v in LABEL_MAP.items()}
        logger.info(f"sklearn model loaded: {list(self.id2label.values())}")

    def _load_transformer(self, device: Optional[str] = None) -> None:
        """Load a HuggingFace transformer model."""
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading transformer from {self.model_path} on {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(self.model_path))
        self.model.to(self.device)
        self.model.eval()
        self.backend = "transformer"

        self.id2label = self.model.config.id2label
        self.label2id = self.model.config.label2id
        logger.info(f"Transformer loaded: {len(self.id2label)} labels — {list(self.id2label.values())}")

    def predict(self, text: str, return_all_scores: bool = False) -> Dict[str, Any]:
        """Predict sentiment for a single text.

        Parameters
        ----------
        text : str
            Input text.
        return_all_scores : bool
            If True, return probabilities for all labels.

        Returns
        -------
        dict with label, confidence, and optionally all_scores.
        """
        return self.predict_batch([text], return_all_scores=return_all_scores)[0]

    def predict_batch(self, texts: List[str], return_all_scores: bool = False) -> List[Dict[str, Any]]:
        """Predict sentiment for a batch of texts.

        Parameters
        ----------
        texts : list of str
        return_all_scores : bool

        Returns
        -------
        list of dicts with label, confidence, and optionally all_scores.
        """
        if self.backend == "sklearn":
            return self._predict_sklearn(texts, return_all_scores)
        return self._predict_transformer(texts, return_all_scores)

    def _predict_sklearn(self, texts: List[str], return_all_scores: bool = False) -> List[Dict[str, Any]]:
        """Predict using sklearn pipeline."""
        start = time.perf_counter()
        pred_ids = self.model.predict(texts)
        probs = self.model.predict_proba(texts) if hasattr(self.model, "predict_proba") else None

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug(f"sklearn batch: {len(texts)} texts in {elapsed_ms:.1f}ms")

        results = []
        for i, pred_id in enumerate(pred_ids):
            conf = float(probs[i][int(pred_id)]) if probs is not None else 1.0
            result: Dict[str, Any] = {
                "label": self.id2label.get(int(pred_id), str(pred_id)),
                "confidence": conf,
            }
            if return_all_scores and probs is not None:
                result["all_scores"] = {self.id2label.get(j, str(j)): float(p) for j, p in enumerate(probs[i])}
            results.append(result)
        return results

    def _predict_transformer(self, texts: List[str], return_all_scores: bool = False) -> List[Dict[str, Any]]:
        """Predict using HuggingFace transformer."""
        import torch

        start = time.perf_counter()

        encodings = self.tokenizer(
            texts,
            max_length=256,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        encodings = {k: v.to(self.device) for k, v in encodings.items()}

        with torch.no_grad():
            outputs = self.model(**encodings)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug(f"Transformer batch: {len(texts)} texts in {elapsed_ms:.1f}ms")

        results = []
        for i, prob in enumerate(probs):
            pred_idx = int(np.argmax(prob))
            result: Dict[str, Any] = {
                "label": self.id2label[pred_idx],
                "confidence": float(prob[pred_idx]),
            }
            if return_all_scores:
                result["all_scores"] = {self.id2label[j]: float(p) for j, p in enumerate(prob)}
            results.append(result)

        return results
