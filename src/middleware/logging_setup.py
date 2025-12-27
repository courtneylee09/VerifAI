"""Logging setup for structured logging across the application."""
import logging

from config.settings import LOG_LEVEL, LOG_FORMAT


def setup_logging():
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )
    return logging.getLogger(__name__)


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance for a specific module."""
    if name is None:
        name = __name__
    return logging.getLogger(name)
