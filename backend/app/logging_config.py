"""O&G Agentic Canvas - Structured Logging Configuration."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to every log entry."""
    event_dict["app"] = "ong-agentic-canvas"
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging with structlog."""

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            add_app_context,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None, **kwargs: Any) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance with optional initial context."""
    logger = structlog.get_logger(name)
    if kwargs:
        logger = logger.bind(**kwargs)
    return logger
