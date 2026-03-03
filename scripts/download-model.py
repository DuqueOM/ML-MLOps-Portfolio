#!/usr/bin/env python3
"""
Init Container script: Download ML model from Google Cloud Storage.

Architecture decisions documented in docs/architecture/infrastructure.md:
- Uses emptyDir volume (ephemeral) — models are ~4MB, download takes 2-5s
- python:3.11-alpine with google-cloud-storage==2.18.2 (pinned for reproducibility)
- 3 retries with 10s fixed backoff — covers transient GCS issues
- GCS handles integrity verification internally (MD5 checksum on download)

Environment variables (injected via ConfigMap):
  GCS_BUCKET        — GCS bucket name (e.g., ml-portfolio-duque-om-202602-ml-models-production)
  GCS_MODEL_PATH    — Blob path in bucket (e.g., bankchurn/model.joblib)
  LOCAL_MODEL_PATH  — Local destination path (e.g., /models/model.joblib)

Usage in K8s Init Container:
  command: ["python", "/scripts/download-model.py"]
"""

import os
import sys
import tarfile
import time

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


def download_model():
    bucket_name = os.environ.get("GCS_BUCKET")
    blob_path = os.environ.get("GCS_MODEL_PATH")
    local_path = os.environ.get("LOCAL_MODEL_PATH", "/models/model.joblib")

    if not bucket_name or not blob_path:
        print("ERROR: GCS_BUCKET and GCS_MODEL_PATH environment variables are required")
        sys.exit(1)

    print(f"Downloading gs://{bucket_name}/{blob_path} -> {local_path}")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            blob.download_to_filename(local_path)
            size_mb = os.path.getsize(local_path) / (1024 * 1024)
            print(f"OK: Downloaded {size_mb:.2f} MB (attempt {attempt}/{MAX_RETRIES})")

            # Auto-extract tar.gz archives (used for transformer models)
            if local_path.endswith(".tar.gz"):
                extract_dir = os.path.dirname(local_path) or "."
                print(f"Extracting archive to {extract_dir}/")
                with tarfile.open(local_path, "r:gz") as tar:
                    tar.extractall(path=extract_dir)
                extracted = [m.name for m in tarfile.open(local_path, "r:gz").getmembers()]
                print(f"Extracted {len(extracted)} files: {extracted}")
                os.remove(local_path)

            sys.exit(0)
        except Exception as e:
            print(f"WARN: Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)

    print("ERROR: All download attempts failed")
    sys.exit(1)


if __name__ == "__main__":
    download_model()
