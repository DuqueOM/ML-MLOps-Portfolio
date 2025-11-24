import logging
import sys
from typing import Optional


def setup_logging(name: str, level: int = logging.INFO, log_format: Optional[str] = None) -> logging.Logger:
    """
    Configure consistent logging across all projects.

    Args:
        name: Logger name (usually __name__)
        level: Logging level
        log_format: Optional custom format string

    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding duplicate handlers if setup is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
