#!/usr/bin/env python3
"""Download Craigslist Cars dataset from Kaggle and adapt it for CarVision.

Prerequisites:
    pip install kaggle pandas
    Place kaggle.json in ~/.kaggle/kaggle.json

Usage:
    python scripts/download_craigslist_cars.py
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
CARVISION_DIR = PROJECT_ROOT / "CarVision-Market-Intelligence"
RAW_DATA_DIR = CARVISION_DIR / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "vehicles_us.csv"


def download_from_kaggle(tmp_dir: str) -> Path:
    """Download the Craigslist dataset using Kaggle API."""
    print("📥 Downloading Craigslist Cars dataset from Kaggle...")
    print("   Dataset: austinreese/craigslist-carstrucks-data")

    os.system(f"kaggle datasets download -d austinreese/craigslist-carstrucks-data -p {tmp_dir} --quiet")

    zip_path = Path(tmp_dir) / "craigslist-carstrucks-data.zip"
    if not zip_path.exists():
        print("❌ Download failed. Check your Kaggle API key (~/.kaggle/kaggle.json)")
        sys.exit(1)

    print("📦 Extracting...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tmp_dir)

    # The dataset file is typically named vehicles.csv
    csv_path = Path(tmp_dir) / "vehicles.csv"
    if not csv_path.exists():
        # Try other common names
        for f in Path(tmp_dir).glob("*.csv"):
            csv_path = f
            break

    if not csv_path.exists():
        print("❌ Could not find CSV file in downloaded archive")
        sys.exit(1)

    return csv_path


def adapt_dataset(input_path: Path) -> pd.DataFrame:
    """Adapt Kaggle Craigslist format to CarVision expected format.

    Kaggle columns: id, url, region, region_url, price, year, manufacturer,
                    model, condition, cylinders, fuel, odometer, title_status,
                    transmission, VIN, drive, size, type, paint_color,
                    image_url, description, county, state, lat, long, posting_date

    CarVision expected: price, model_year, model, condition, cylinders, fuel,
                        odometer, transmission, type, paint_color, is_4wd,
                        date_posted, days_listed
    """
    print("🔄 Loading raw Kaggle data...")
    df = pd.read_csv(input_path, low_memory=False)
    print(f"   Raw rows: {len(df):,}")

    # --- Column mapping ---
    print("🔧 Adapting columns to CarVision format...")

    # Combine manufacturer + model into "model" column (e.g. "ford f-150")
    df["model"] = (df["manufacturer"].fillna("").str.strip() + " " + df["model"].fillna("").str.strip()).str.strip()

    # Rename year -> model_year
    df = df.rename(columns={"year": "model_year", "posting_date": "date_posted"})

    # Create is_4wd from drive column (1 if 4wd, else NaN to match original format)
    df["is_4wd"] = df["drive"].apply(lambda x: 1.0 if x == "4wd" else float("nan"))

    # Create days_listed (synthetic: random 1-90 since Kaggle data doesn't have this)
    import numpy as np

    rng = np.random.default_rng(42)
    df["days_listed"] = rng.integers(1, 91, size=len(df))

    # --- Filter: keep only clean title vehicles ---
    df = df[df["title_status"] == "clean"]
    print(f"   After clean title filter: {len(df):,}")

    # --- Select CarVision columns ---
    carvision_cols = [
        "price",
        "model_year",
        "model",
        "condition",
        "cylinders",
        "fuel",
        "odometer",
        "transmission",
        "type",
        "paint_color",
        "is_4wd",
        "date_posted",
        "days_listed",
    ]
    df = df[carvision_cols]

    # --- Basic quality filters (matching CarVision config) ---
    df = df[df["price"] > 0]
    df = df[df["price"] < 1_000_000]  # Remove obvious outliers
    df = df.dropna(subset=["model_year", "odometer"])  # Need these for features
    print(f"   After quality filters: {len(df):,}")

    # --- Sample to ~100K rows for manageable size ---
    max_rows = 100_000
    if len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=42)
        print(f"   Sampled to: {len(df):,} rows")

    df = df.reset_index(drop=True)
    return df


def main():
    print("=" * 60)
    print("🚗 CarVision — Craigslist Cars Dataset Integration")
    print("=" * 60)

    # Backup existing dataset
    if OUTPUT_FILE.exists():
        backup = OUTPUT_FILE.with_suffix(".csv.bak")
        OUTPUT_FILE.rename(backup)
        print(f"📋 Backed up existing dataset to {backup.name}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = download_from_kaggle(tmp_dir)
        df = adapt_dataset(csv_path)

    # Save
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\n✅ Dataset saved to: {OUTPUT_FILE}")
    print(f"   Rows: {len(df):,} | Columns: {df.shape[1]} | Size: {size_mb:.1f} MB")

    # Show sample
    print("\n📊 Sample data:")
    print(df.head(3).to_string())

    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. cd CarVision-Market-Intelligence")
    print("  2. python main.py --mode train --config configs/config.yaml")
    print("  3. pytest tests/ -v")
    print("=" * 60)


if __name__ == "__main__":
    main()
