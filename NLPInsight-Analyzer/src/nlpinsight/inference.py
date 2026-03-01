"""Inference engine for sentiment analysis.

Provides a unified interface for loading fine-tuned models and running
predictions. Supports both HuggingFace pipeline and manual torch inference.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Load a fine-tuned transformer and predict sentiment.

    Supports two backends:
    - HuggingFace ``pipeline`` (default, simple)
    - Manual ``torch`` inference (for custom post-processing)

    Parameters
    ----------
    model_path : str or Path
        Directory containing saved model and tokenizer.
    device : str, optional
        ``"cpu"`` or ``"cuda"``. Auto-detected if None.
    """

    def __init__(self, model_path: str | Path, device: Optional[str] = None):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.model_path = Path(model_path)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Loading model from {self.model_path} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(self.model_path))
        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label
        self.label2id = self.model.config.label2id
        logger.info(f"Model loaded: {len(self.id2label)} labels — {list(self.id2label.values())}")

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
        logger.debug(f"Batch inference: {len(texts)} texts in {elapsed_ms:.1f}ms")

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
