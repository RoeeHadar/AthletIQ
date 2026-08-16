# Implements: FR-001, FR-016, FR-017, FR-018, FR-021, DR-001, ADR-006, ADR-017, CR-004, CR-005
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
    season_depth: int = 3,
    seasons: list[int] | None = None,
    batch_id: str | None = None,
) -> Path:
    """Fetch teams + seasons and land immutable JSON under raw_root/batch_id/.

    When `seasons` is omitted, use the provider's `available_seasons` (fixture files
    or uncapped live NBA). Explicit `seasons` still limits the loop (tests).
    """
    batch_id = batch_id or new_batch_id()
    batch_dir = Path(raw_root) / batch_id
    if batch_dir.exists() and any(batch_dir.iterdir()):
        raise FileExistsError(f"raw batch already exists: {batch_dir}")

    leagues = list(provider.leagues())
    logger.info("ingest batch=%s leagues=%s", batch_id, leagues)

    teams = provider.fetch_teams()
    write_raw_json(batch_dir / "teams.json", {"response": teams})

    written_seasons: list[int] = []
    for league in leagues:
        if seasons is not None:
            league_seasons = list(seasons)
        else:
            avail = getattr(provider, "available_seasons", None)
            if callable(avail):
                league_seasons = list(avail(league))
            else:
                league_seasons = active_season_years(depth=season_depth)
        for season in league_seasons:
            games = provider.fetch_games(season, league=league)
            if league == "nba":
                name = f"games_{season}.json"
            else:
                name = f"games_{league}_{season}.json"
            write_raw_json(
                batch_dir / name,
                {"response": games, "season": season, "league": league},
            )
            written_seasons.append(season)

    write_raw_json(batch_dir / "players.json", {"response": provider.fetch_players()})
    write_raw_json(
        batch_dir / "player_game_stats.json",
        {"response": provider.fetch_player_game_stats()},
    )
    write_raw_json(
        batch_dir / "odds_snapshots.json",
        {"response": provider.fetch_odds_snapshots()},
    )

    meta = {
        "batch_id": batch_id,
        "active_seasons": sorted(set(written_seasons)),
        "season_depth": season_depth,
        "leagues": leagues,
    }
    write_raw_json(batch_dir / "manifest.json", meta)
    return batch_dir
