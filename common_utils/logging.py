"""Structured JSON logging for ML services.

Provides consistent, machine-parseable log output across all portfolio services.
In production (LOG_FORMAT=json), emits JSON lines compatible with GCP Cloud Logging,
AWS CloudWatch, and ELK/Loki ingestion. In development, falls back to human-readable
colored output.

Usage::

    from common_utils.logging import get_logger

    logger = get_logger(__name__, service="bankchurn")
    logger.info("prediction", extra={"customer_id": 42, "risk": "high"})
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects.

    Output fields:
        timestamp, level, service, logger, message, plus any ``extra`` keys.
    """

    def __init__(self, service: str = "unknown") -> None:
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "service": self.service,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Merge extra fields (skip internal LogRecord attributes)
        _RESERVED = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)
        for key, value in record.__dict__.items():
            if key not in _RESERVED and key not in (
                "message",
                "msg",
                "args",
                "exc_info",
                "exc_text",
                "stack_info",
            ):
                log_entry[key] = value

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class HumanFormatter(logging.Formatter):
    """Readable format for local development."""

    FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s"

    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt="%H:%M:%S")


def get_logger(
    name: str,
    service: Optional[str] = None,
    level: Optional[int] = None,
) -> logging.Logger:
    """Return a configured logger.

    Parameters
    ----------
    name:
        Logger name (typically ``__name__``).
    service:
        Service identifier embedded in JSON logs.  Falls back to
        ``SERVICE_NAME`` env var or *"ml-service"*.
    level:
        Override log level.  Falls back to ``LOG_LEVEL`` env var or INFO.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    resolved_service = service or os.environ.get("SERVICE_NAME", "ml-service")
    resolved_level = level or getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    logger.setLevel(resolved_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(resolved_level)

    log_format = os.environ.get("LOG_FORMAT", "human").lower()
    if log_format == "json":
        handler.setFormatter(JSONFormatter(service=resolved_service))
    else:
        handler.setFormatter(HumanFormatter())

    logger.addHandler(handler)
    logger.propagate = False
    return logger
