# Implements: FR-012, FR-009, FR-018, FR-022, ADR-001, ADR-004, ADR-009, ADR-014, CR-004, CR-005
"""Uvicorn ASGI entry — explicit store selection; DATABASE_URL is connection only."""

from __future__ import annotations

import os

from api.app.main import create_app
from api.app.state import AppState, InMemoryFeatureRepo, InMemoryGameRepo
from athletiq.config import load_settings
from athletiq.logging import configure_logging


def _db_ping(database_url: str) -> bool:
    import psycopg

    with psycopg.connect(database_url, connect_timeout=3) as conn:
        conn.execute("SELECT 1")
    return True


def build_app():
    settings = load_settings()
    configure_logging(settings.log_level, secrets=settings.secret_values())
    # Explicit store mode — presence of DATABASE_URL alone does not switch.
    store_kind = (os.environ.get("ATHLETIQ_STORE") or "memory").strip().lower()
    url = settings.database_url

    if store_kind == "postgres":
        from athletiq.db.api_repos import PostgresFeatureRepo, PostgresGameRepo
        from athletiq.db.migrate import apply_migrations
        from athletiq.ledger.postgres import PostgresLedger

        apply_migrations(url)
        games = PostgresGameRepo.connect(url)
        features = PostgresFeatureRepo.connect(url)
        ledger = PostgresLedger(games._conn)
        db_ping = lambda: _db_ping(url)  # noqa: E731
    else:
        from athletiq.ledger.memory import MemoryLedger

        games = InMemoryGameRepo()
        features = InMemoryFeatureRepo()
        ledger = MemoryLedger()
        # Optional health ping when URL configured; empty in-memory repos still need explicit ping
        # only if ATHLETIQ_STORE requests postgres. Memory mode: ping if caller wants DB check via env.
        db_ping = (lambda: _db_ping(url)) if os.environ.get("ATHLETIQ_DB_PING") == "1" else None

    state = AppState(
        artifacts_dir=settings.artifacts_path,
        games=games,
        features=features,
        db_ping=db_ping,
        ledger=ledger,
    )
    state.load_pin()
    return create_app(state)


app = build_app()
