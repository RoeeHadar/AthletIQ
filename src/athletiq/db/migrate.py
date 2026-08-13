# Implements: FR-002, DR-002, CON-002, NFR-005, ADR-001, ADR-010
"""Apply forward-only SQL migrations."""

from __future__ import annotations

import logging
from pathlib import Path

import psycopg

logger = logging.getLogger("athletiq.db")

REPO_ROOT = Path(__file__).resolve().parents[3]


def migrations_dir() -> Path:
    return REPO_ROOT / "database" / "migrations"


def apply_migrations(database_url: str, *, directory: Path | None = None) -> list[str]:
    """Apply all `*.sql` migrations in sorted order. Safe to re-run (IF NOT EXISTS).

    Returns versions recorded in `schema_migrations` after apply.
    """
    directory = directory or migrations_dir()
    files = sorted(directory.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"No migrations in {directory}")

    applied: list[str] = []
    with psycopg.connect(database_url) as conn:
        conn.execute("SELECT 1")  # fail fast
        for path in files:
            sql = path.read_text(encoding="utf-8")
            logger.info("applying migration %s", path.name)
            with conn.transaction():
                conn.execute(sql)
            applied.append(path.stem)

        rows = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        return [r[0] for r in rows]
