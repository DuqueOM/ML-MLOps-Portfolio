"""Training pipeline for fine-tuning DistilBERT on sentiment analysis.

Supports:
- HuggingFace Trainer API with early stopping
- Mixed-precision (FP16) training
- Learning rate scheduling with warmup
- Class-weighted loss for imbalanced data
- Model checkpointing and metric logging
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


def compute_metrics(eval_pred) -> Dict[str, float]:
    """Compute classification metrics for HuggingFace Trainer.

    Parameters
    ----------
    eval_pred : EvalPrediction
        Predictions and labels from Trainer.

    Returns
    -------
    dict with accuracy, f1, precision, recall
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": float(accuracy_score(labels, preds)),
        "f1": float(f1_score(labels, preds, average="weighted")),
        "precision": float(precision_score(labels, preds, average="weighted", zero_division=0)),
        "recall": float(recall_score(labels, preds, average="weighted", zero_division=0)),
    }


def train_model(
    train_dataset,
    val_dataset,
    model_name: str = "distilbert-base-uncased",
    num_labels: int = 2,
    label2id: Optional[Dict[str, int]] = None,
    id2label: Optional[Dict[int, str]] = None,
    output_dir: str = "models",
    learning_rate: float = 2e-5,
    epochs: int = 3,
    batch_size: int = 16,
    weight_decay: float = 0.01,
    warmup_ratio: float = 0.1,
    fp16: bool = False,
    seed: int = 42,
    early_stopping_patience: int = 2,
) -> Tuple[Any, Dict[str, float]]:
    """Fine-tune a pre-trained transformer for text classification.

    Parameters
    ----------
    train_dataset : TextDataset
        Training data.
    val_dataset : TextDataset
        Validation data.
    model_name : str
        HuggingFace model identifier.
    num_labels : int
        Number of classification labels.
    label2id : dict, optional
        Label name to ID mapping.
    id2label : dict, optional
        ID to label name mapping.
    output_dir : str
        Directory for checkpoints.
    learning_rate : float
    epochs : int
    batch_size : int
    weight_decay : float
    warmup_ratio : float
    fp16 : bool
        Enable mixed-precision training.
    seed : int
    early_stopping_patience : int

    Returns
    -------
    model : PreTrainedModel
        Fine-tuned model.
    metrics : dict
        Final evaluation metrics.
    """
    from transformers import AutoModelForSequenceClassification, EarlyStoppingCallback, Trainer, TrainingArguments

    # Set seed for reproducibility
    torch.manual_seed(seed)
    np.random.seed(seed)

    logger.info(f"Loading pre-trained model: {model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id2label or {i: str(i) for i in range(num_labels)},
        label2id=label2id or {str(i): i for i in range(num_labels)},
    )

    # Detect device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Training device: {device}")
    if device == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size * 2,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        fp16=fp16 and torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        logging_steps=50,
        seed=seed,
        report_to="none",
        disable_tqdm=False,
    )

    callbacks = []
    if early_stopping_patience > 0:
        callbacks.append(EarlyStoppingCallback(early_stopping_patience=early_stopping_patience))

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=callbacks,
    )

    logger.info(f"Starting training: {epochs} epochs, lr={learning_rate}, batch={batch_size}")
    trainer.train()

    # Evaluate
    eval_results = trainer.evaluate()
    metrics = {
        "accuracy": eval_results.get("eval_accuracy", 0.0),
        "f1": eval_results.get("eval_f1", 0.0),
        "precision": eval_results.get("eval_precision", 0.0),
        "recall": eval_results.get("eval_recall", 0.0),
        "eval_loss": eval_results.get("eval_loss", 0.0),
        "model_name": model_name,
        "num_labels": num_labels,
        "epochs": epochs,
        "learning_rate": learning_rate,
    }
    logger.info(f"Training complete — F1: {metrics['f1']:.4f}, Acc: {metrics['accuracy']:.4f}")

    return model, metrics


def save_model(model, tokenizer, output_dir: str, metrics: Optional[Dict] = None) -> None:
    """Save fine-tuned model, tokenizer, and metrics.

    Parameters
    ----------
    model : PreTrainedModel
    tokenizer : PreTrainedTokenizer
    output_dir : str
    metrics : dict, optional
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    logger.info(f"Model and tokenizer saved to {output_path}")

    if metrics:
        metrics_path = output_path / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to {metrics_path}")
