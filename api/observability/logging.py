"""
Structured JSON logging with correlation IDs.

Provides structured logging that automatically includes request_id and trace_id
from the current context.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any, Optional

from .context import get_context_dict


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.

    Each log entry includes:
    - timestamp (ISO 8601 with timezone)
    - level (INFO, ERROR, etc.)
    - logger name
    - message
    - request_id (if available)
    - trace_id (if available)
    - Additional fields from extra
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        # Get context variables
        context = get_context_dict()

        # Build the log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context IDs if available
        if context.get("request_id"):
            log_entry["request_id"] = context["request_id"]
        if context.get("trace_id"):
            log_entry["trace_id"] = context["trace_id"]
        if context.get("parent_span_id"):
            log_entry["parent_span_id"] = context["parent_span_id"]

        # Add location info
        log_entry["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_entry)


class StructuredLogger(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes context and supports extra fields.

    Usage:
        logger = get_logger(__name__)
        logger.info("User action", extra_fields={"user_id": 123, "action": "login"})
    """

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        """Process the logging call to add context and extra fields."""
        # Extract extra_fields from kwargs
        extra_fields = kwargs.pop("extra_fields", {})

        # Ensure 'extra' exists in kwargs
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # Store extra_fields in a way the formatter can access
        kwargs["extra"]["extra_fields"] = extra_fields

        return msg, kwargs


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance with context support
    """
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger, {})


def setup_logging(
    level: str = "INFO",
    json_output: bool = True,
    include_stdlib: bool = False,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Use JSON formatter (True) or simple text (False)
        include_stdlib: Include verbose stdlib logs (uvicorn, etc.)
    """
    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if json_output:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(handler)

    # Configure third-party loggers
    if not include_stdlib:
        # Reduce noise from third-party libraries
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("starlette").setLevel(logging.WARNING)

    # Set application loggers to the requested level
    logging.getLogger("api").setLevel(log_level)
    logging.getLogger("core").setLevel(log_level)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """
    Log an HTTP request with structured data.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        extra: Additional fields to include
    """
    logger = get_logger("api.requests")

    extra_fields = {
        "http": {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
    }

    if extra:
        extra_fields.update(extra)

    # Choose log level based on status code
    if status_code >= 500:
        logger.error(
            f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)",
            extra_fields=extra_fields,
        )
    elif status_code >= 400:
        logger.warning(
            f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)",
            extra_fields=extra_fields,
        )
    else:
        logger.info(
            f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)",
            extra_fields=extra_fields,
        )
