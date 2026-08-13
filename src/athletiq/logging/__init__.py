# Implements: SEC-001, OPS-002
"""Structured logging with secret redaction."""

from __future__ import annotations

import logging
from typing import Iterable

_REDACTED = "***REDACTED***"


class SecretRedactingFilter(logging.Filter):
    """Replace known secret substrings in log records."""

    def __init__(self, secrets: Iterable[str]) -> None:
        super().__init__()
        # Longest first so overlapping fragments redact cleanly.
        self._secrets = tuple(sorted((s for s in secrets if s), key=len, reverse=True))

    def filter(self, record: logging.LogRecord) -> bool:
        if self._secrets:
            record.msg = self._redact(str(record.msg))
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {k: self._redact(str(v)) for k, v in record.args.items()}
                else:
                    record.args = tuple(self._redact(str(a)) for a in record.args)
            if record.exc_info and record.exc_info[1] is not None:
                # Ensure formatted exception text is scrubbed when getMessage/format runs.
                exc = record.exc_info[1]
                scrubbed = self._redact(str(exc))
                if scrubbed != str(exc):
                    try:
                        exc.args = (scrubbed, *exc.args[1:]) if exc.args else (scrubbed,)
                    except Exception:
                        pass
        return True

    def _redact(self, text: str) -> str:
        out = text
        for secret in self._secrets:
            if secret and secret in out:
                out = out.replace(secret, _REDACTED)
        return out


def redact_text(text: str, secrets: Iterable[str]) -> str:
    """Redact secrets in an arbitrary string (errors, retry messages)."""
    out = text
    for secret in sorted((s for s in secrets if s), key=len, reverse=True):
        out = out.replace(secret, _REDACTED)
    return out


def configure_logging(
    level: str = "INFO",
    secrets: Iterable[str] | None = None,
    *,
    logger_name: str = "athletiq",
) -> logging.Logger:
    """Configure the AthletIQ logger with optional secret redaction."""
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    if secrets:
        handler.addFilter(SecretRedactingFilter(secrets))
    logger.addHandler(handler)
    return logger


def get_logger(name: str = "athletiq") -> logging.Logger:
    return logging.getLogger(name)
