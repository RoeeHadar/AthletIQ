# Implements: FR-002, DR-002, DR-005, CON-002, NFR-005, ADR-001, ADR-010, CR-004, CR-005
"""Apply forward-only SQL migrations."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import psycopg

logger = logging.getLogger("athletiq.db")

# Dev checkout: src/athletiq/db/migrate.py → repo root. Installed wheel: site-packages.
_SRC_REPO_ROOT = Path(__file__).resolve().parents[3]


def migrations_dir() -> Path:
    env = os.environ.get("ATHLETIQ_MIGRATIONS_DIR")
    if env:
        return Path(env)
    candidates = [
        Path.cwd() / "database" / "migrations",
        Path("/app/database/migrations"),
        _SRC_REPO_ROOT / "database" / "migrations",
    ]
    for path in candidates:
        if path.is_dir() and any(path.glob("*.sql")):
            return path
    return candidates[0]


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
