# Implements: FR-009, FR-014, CON-004, NFR-002, NFR-004, ADR-008, ADR-009
"""AthletIQ demo FastAPI application (no auth)."""

from __future__ import annotations

from api.app.main import create_app

__all__ = ["create_app"]
