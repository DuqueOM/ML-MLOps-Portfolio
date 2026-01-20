"""Optimized model persistence utilities using Joblib.

This module provides enhanced model serialization with:
- Compression for smaller file sizes (60-80% reduction)
- Protocol versioning for compatibility
- Robust error handling
- Integrity validation
- Logging and monitoring
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

import joblib

logger = logging.getLogger(__name__)


class ModelPersistenceError(Exception):
    """Custom exception for model persistence errors."""

    pass


def save_model(
    model: Any,
    path: str | Path,
    compress: int | str = 3,
    protocol: Optional[int] = None,
    create_dirs: bool = True,
    compute_hash: bool = True,
) -> dict[str, Any]:
    """Save model with compression and metadata.

    Parameters
    ----------
    model : Any
        Model object to save (sklearn Pipeline, estimator, etc.)
    path : str or Path
        Output file path (will create parent dirs if needed)
    compress : int or str, default=3
        Compression level:
        - 0: no compression
        - 1-9: zlib compression (3 is good balance)
        - 'lz4': fast compression (requires lz4)
        - 'gzip': standard gzip
        - ('gzip', 3): gzip with level 3
    protocol : int, optional
        Pickle protocol version (None = highest available)
    create_dirs : bool, default=True
        Create parent directories if they don't exist
    compute_hash : bool, default=True
        Compute SHA256 hash for integrity validation

    Returns
    -------
    metadata : dict
        Dictionary with:
        - path: str - saved file path
        - size_bytes: int - file size
        - hash_sha256: str - file hash (if compute_hash=True)
        - compression: str - compression method used

    Raises
    ------
    ModelPersistenceError
        If save operation fails

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> model = RandomForestClassifier()
    >>> metadata = save_model(model, "models/rf_model.pkl", compress=3)
    >>> print(f"Saved {metadata['size_bytes']} bytes")
    """
    path = Path(path)

    # Create parent directories
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Save with compression
        joblib.dump(model, path, compress=compress, protocol=protocol)
        logger.info(f"Model saved to {path} with compression={compress}")

        # Get file metadata
        size_bytes = path.stat().st_size
        metadata = {
            "path": str(path),
            "size_bytes": size_bytes,
            "compression": str(compress),
        }

        # Compute hash for integrity
        if compute_hash:
            hash_sha256 = _compute_file_hash(path)
            metadata["hash_sha256"] = hash_sha256
            logger.debug(f"Model hash: {hash_sha256}")

        return metadata

    except Exception as e:
        error_msg = f"Failed to save model to {path}: {e}"
        logger.error(error_msg)
        raise ModelPersistenceError(error_msg) from e


def load_model(
    path: str | Path,
    validate_hash: Optional[str] = None,
    mmap_mode: Optional[str] = None,
) -> Any:
    """Load model with validation and error handling.

    Parameters
    ----------
    path : str or Path
        Path to saved model file
    validate_hash : str, optional
        Expected SHA256 hash for integrity validation
    mmap_mode : str, optional
        Memory-map mode for large arrays:
        - None: load into memory (default)
        - 'r': read-only mmap
        - 'r+': read-write mmap
        - 'c': copy-on-write mmap

    Returns
    -------
    model : Any
        Loaded model object

    Raises
    ------
    FileNotFoundError
        If model file doesn't exist
    ModelPersistenceError
        If load fails or hash validation fails

    Examples
    --------
    >>> model = load_model("models/rf_model.pkl")
    >>> # With hash validation
    >>> model = load_model("models/rf_model.pkl", validate_hash="abc123...")
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    # Validate hash if provided
    if validate_hash:
        actual_hash = _compute_file_hash(path)
        if actual_hash != validate_hash:
            error_msg = f"Hash mismatch for {path}. Expected: {validate_hash}, Got: {actual_hash}"
            logger.error(error_msg)
            raise ModelPersistenceError(error_msg)
        logger.debug(f"Hash validation passed for {path}")

    try:
        model = joblib.load(path, mmap_mode=mmap_mode)
        logger.info(f"Model loaded from {path}")
        return model

    except Exception as e:
        error_msg = f"Failed to load model from {path}: {e}"
        logger.error(error_msg)
        raise ModelPersistenceError(error_msg) from e


def _compute_file_hash(path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of file for integrity validation.

    Parameters
    ----------
    path : Path
        File path
    algorithm : str, default='sha256'
        Hash algorithm (sha256, md5, etc.)

    Returns
    -------
    hash_hex : str
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)

    with open(path, "rb") as f:
        # Read in chunks for memory efficiency
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def get_model_info(path: str | Path) -> dict[str, Any]:
    """Get metadata about saved model file.

    Parameters
    ----------
    path : str or Path
        Path to model file

    Returns
    -------
    info : dict
        Dictionary with file metadata:
        - exists: bool
        - size_bytes: int
        - size_mb: float
        - hash_sha256: str
        - path: str

    Examples
    --------
    >>> info = get_model_info("models/rf_model.pkl")
    >>> print(f"Model size: {info['size_mb']:.2f} MB")
    """
    path = Path(path)

    if not path.exists():
        return {"exists": False, "path": str(path)}

    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    hash_sha256 = _compute_file_hash(path)

    return {
        "exists": True,
        "path": str(path),
        "size_bytes": size_bytes,
        "size_mb": size_mb,
        "hash_sha256": hash_sha256,
    }


# Convenience aliases for backward compatibility
dump_model = save_model
load_model_safe = load_model
