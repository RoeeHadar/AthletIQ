# Implements: FR-001, DR-001, ADR-006
"""Immutable raw JSON landing (filesystem)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from athletiq.provider.base import ProviderClient
from athletiq.provider.seasons import active_season_years

logger = logging.getLogger("athletiq.ingest")


def new_batch_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.strftime("%Y%m%dT%H%M%SZ")


def write_raw_json(path: Path, payload: Any) -> None:
    """Write JSON once. Refuses to overwrite (immutability)."""
    if path.exists():
        raise FileExistsError(f"raw file already exists (immutable): {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def ingest_raw(
    provider: ProviderClient,
    raw_root: Path,
    *,
    season_depth: int = 2,
    seasons: list[int] | None = None,
    batch_id: str | None = None,
) -> Path:
    """Fetch teams + in-window seasons and land immutable JSON under raw_root/batch_id/.

    Seasons outside the active window are skipped (DR-001 / too-old prune at ingest).
    """
    batch_id = batch_id or new_batch_id()
    batch_dir = Path(raw_root) / batch_id
    if batch_dir.exists() and any(batch_dir.iterdir()):
        # Never mutate an existing batch; force a new id.
        raise FileExistsError(f"raw batch already exists: {batch_dir}")

    active = seasons if seasons is not None else active_season_years(depth=season_depth)
    logger.info("ingest batch=%s active_seasons=%s", batch_id, active)

    teams = provider.fetch_teams()
    write_raw_json(batch_dir / "teams.json", {"response": teams})

    for season in active:
        games = provider.fetch_games(season)
        write_raw_json(batch_dir / f"games_{season}.json", {"response": games, "season": season})

    meta = {"batch_id": batch_id, "active_seasons": active, "season_depth": season_depth}
    write_raw_json(batch_dir / "manifest.json", meta)
    return batch_dir
