"""
Structured (JSON) logging setup.

Call configure_logging() exactly once, at application startup (main.py).
Every other module should obtain a logger via:

    import logging
    logger = logging.getLogger(__name__)

and never configure logging itself. This keeps a single source of truth
for log format/level, consistent with how Settings is the single source
of truth for configuration (see core/config.py).
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Any


# Attributes every standard LogRecord has. Anything else attached to a
# record (via `logger.info(..., extra={...})`) is "extra" structured
# data we want to surface in the JSON output.
_STANDARD_RECORD_ATTRS = frozenset(
    logging.LogRecord(
        name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
    ).__dict__.keys()
) | {"message", "asctime"}


class JSONFormatter(logging.Formatter):
    """Formats each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Surface exception info if this record came from logger.exception()
        # or logger.error(..., exc_info=True)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Surface any extra fields the caller attached, e.g.:
        # logger.info("prediction served", extra={"model_version_label": "canary"})
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_RECORD_ATTRS
        }
        if extras:
            payload.update(extras)

        import json

        return json.dumps(payload, default=str)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure the root logger to emit structured JSON to stdout.

    Idempotent-ish: calling this more than once replaces existing
    handlers on the root logger rather than stacking duplicates, but it
    should still only be called once, at startup.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Remove any handlers a library may have already attached (e.g. from
    # an earlier logging.basicConfig() call), so we have exactly one.
    root_logger.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)