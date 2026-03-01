"""Data loading and tokenization for NLP sentiment analysis.

Handles dataset loading, train/val splitting, and HuggingFace tokenization
with proper padding, truncation, and batching.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def load_dataset(path: str | Path, text_col: str = "text", label_col: str = "label") -> pd.DataFrame:
    """Load and validate a text classification dataset.

    Parameters
    ----------
    path : str or Path
        Path to CSV file with text and label columns.
    text_col : str
        Name of the text column.
    label_col : str
        Name of the label column.

    Returns
    -------
    DataFrame with validated text and label columns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    for col in [text_col, label_col]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'. Found: {list(df.columns)}")

    # Drop rows with missing text
    n_before = len(df)
    df = df.dropna(subset=[text_col]).reset_index(drop=True)
    n_dropped = n_before - len(df)
    if n_dropped:
        logger.warning(f"Dropped {n_dropped} rows with missing text")

    logger.info(f"Loaded {len(df)} samples from {path}")
    return df


def encode_labels(
    df: pd.DataFrame,
    label_col: str = "label",
    label_names: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, Dict[str, int], Dict[int, str]]:
    """Encode string labels to integers.

    Parameters
    ----------
    df : DataFrame
    label_col : str
    label_names : list of str, optional
        Explicit label ordering. If None, sorted unique values are used.

    Returns
    -------
    df : DataFrame with integer labels
    label2id : dict mapping label name to integer
    id2label : dict mapping integer to label name
    """
    if label_names is None:
        label_names = sorted(df[label_col].unique().tolist())

    label2id = {name: idx for idx, name in enumerate(label_names)}
    id2label = {idx: name for name, idx in label2id.items()}

    df = df.copy()
    df[label_col] = df[label_col].map(label2id)

    # Drop unmapped labels
    unmapped = df[label_col].isna().sum()
    if unmapped:
        logger.warning(f"Dropping {unmapped} samples with unknown labels")
        df = df.dropna(subset=[label_col]).reset_index(drop=True)
    df[label_col] = df[label_col].astype(int)

    logger.info(f"Labels encoded: {label2id}")
    return df, label2id, id2label


def split_dataset(
    df: pd.DataFrame,
    label_col: str = "label",
    val_size: float = 0.15,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified train/validation split.

    Parameters
    ----------
    df : DataFrame
    label_col : str
    val_size : float
    seed : int

    Returns
    -------
    train_df, val_df : DataFrames
    """
    train_df, val_df = train_test_split(
        df,
        test_size=val_size,
        random_state=seed,
        stratify=df[label_col],
    )
    logger.info(f"Split: {len(train_df)} train, {len(val_df)} val")
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True)


class TextDataset:
    """HuggingFace-compatible dataset for text classification.

    Tokenizes text on-the-fly and returns dicts compatible with
    Trainer or manual DataLoader usage.

    Parameters
    ----------
    texts : list of str
    labels : list of int
    tokenizer : PreTrainedTokenizer
    max_length : int
    """

    def __init__(self, texts: List[str], labels: List[int], tokenizer: Any, max_length: int = 256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": self.labels[idx],
        }
