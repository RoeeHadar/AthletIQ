# Implements: FR-023, ADR-014
"""Ledger domain errors (mapped to API codes by the HTTP layer)."""

from __future__ import annotations


class LedgerError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
