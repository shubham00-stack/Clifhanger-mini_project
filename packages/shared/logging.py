"""Structured JSON logger with request-id tracking and context fields."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Context variable for request correlation ID
current_request_id: ContextVar[Optional[str]] = ContextVar("current_request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Injects the current request_id into all log records."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id.get() or "system"
        return True


class JSONFormatter(logging.Formatter):
    """Outputs structured JSON log records for observability."""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "system"),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def configure_logging(level: str = "INFO") -> None:
    """Configures root logger with JSON formatting and request filter."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(level.upper())
    # Clear existing handlers to prevent duplicate lines
    root.handlers = [handler]


def get_logger(name: str) -> logging.Logger:
    """Returns a module logger with RequestIdFilter applied."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())
    return logger
