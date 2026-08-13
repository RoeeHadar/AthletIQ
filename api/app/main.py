# Implements: FR-009, FR-010, FR-014, CON-004, NFR-002, NFR-004, ADR-008, ADR-009
"""FastAPI factory — no auth middleware (ADR-009)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from api.app.errors import ApiError, api_error_handler
from api.app.routes import router
from api.app.state import AppState


def create_app(state: AppState | None = None) -> FastAPI:
    app = FastAPI(
        title="AthletIQ Demo API",
        version="1.0.0",
        description=(
            "MVP prediction API (sync, game_id-keyed). No application auth (ADR-009). "
            "No hard latency SLO (NFR-004)."
        ),
    )
    app.state.athletiq = state or AppState()
    app.add_exception_handler(ApiError, api_error_handler)
    app.include_router(router)

    # Explicitly no auth / tenancy middleware (NFR-002, ADR-009).
    return app


def create_app_from_artifacts(artifacts_dir: Path) -> FastAPI:
    state = AppState(artifacts_dir=Path(artifacts_dir))
    state.load_pin()
    return create_app(state)
