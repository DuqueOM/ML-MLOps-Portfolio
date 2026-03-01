#!/usr/bin/env python3
"""Download Financial PhraseBank dataset and prepare it for NLPInsight-Analyzer.

The dataset contains 4,846 sentences from English-language financial news,
annotated by financial domain experts for sentiment (positive, negative, neutral).

Source: Malo et al. (2014) — https://huggingface.co/datasets/financial_phrasebank
License: CC BY-NC-SA 3.0

Prerequisites:
    pip install datasets pandas

Usage:
    python scripts/download_financial_phrasebank.py
"""

import sys
import zipfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
NLPINSIGHT_DIR = PROJECT_ROOT / "NLPInsight-Analyzer"
RAW_DATA_DIR = NLPINSIGHT_DIR / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "train.csv"

LABEL_MAP = {"negative": 0, "neutral": 1, "positive": 2}


def download_dataset() -> pd.DataFrame:
    """Download Financial PhraseBank from HuggingFace Hub."""
    print("\U0001f4e5 Downloading Financial PhraseBank from HuggingFace...")
    print("   Config: sentences_allagree (highest annotation agreement)")

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("\u274c 'huggingface_hub' not installed. Run: pip install huggingface-hub")
        sys.exit(1)

    zip_path = hf_hub_download(
        repo_id="financial_phrasebank",
        filename="data/FinancialPhraseBank-v1.0.zip",
        repo_type="dataset",
    )

    # Parse the AllAgree subset from the zip
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("FinancialPhraseBank-v1.0/Sentences_AllAgree.txt") as f:
            raw = f.read().decode("latin-1")

    records = []
    for line in raw.strip().split("\n"):
        parts = line.rsplit("@", 1)
        if len(parts) == 2:
            text = parts[0].strip()
            label = parts[1].strip()
            if label in LABEL_MAP:
                records.append({"text": text, "label": label, "label_id": LABEL_MAP[label]})

    df = pd.DataFrame(records)
    print(f"   Downloaded: {len(df):,} sentences")

    # Show distribution
    print("\n\U0001f4ca Label distribution:")
    for label, count in df["label"].value_counts().items():
        pct = count / len(df) * 100
        print(f"   {label:>10s}: {count:>5d} ({pct:.1f}%)")

    return df


def create_train_test_split(df: pd.DataFrame) -> None:
    """Save train and test splits."""
    from sklearn.model_selection import train_test_split

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label_id"])

    processed_dir = NLPINSIGHT_DIR / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(processed_dir / "train.csv", index=False)
    test_df.to_csv(processed_dir / "test.csv", index=False)

    print("\n📁 Splits saved:")
    print(f"   Train: {len(train_df):,} rows → data/processed/train.csv")
    print(f"   Test:  {len(test_df):,} rows → data/processed/test.csv")


def main():
    print("=" * 60)
    print("📝 NLPInsight — Financial PhraseBank Dataset Integration")
    print("=" * 60)

    # Download (already returns clean text, label, label_id columns)
    df = download_dataset()

    # Save raw
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n✅ Raw dataset saved to: {OUTPUT_FILE}")
    print(f"   Rows: {len(df):,} | Columns: {df.shape[1]} | Size: {size_kb:.1f} KB")

    # Create splits
    create_train_test_split(df)

    # Show sample
    print("\n📊 Sample data:")
    print(df.head(5).to_string(max_colwidth=80))

    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. cd NLPInsight-Analyzer")
    print("  2. python main.py --mode train --config configs/config.yaml")
    print("  3. pytest tests/ -v")
    print("=" * 60)


if __name__ == "__main__":
    main()
