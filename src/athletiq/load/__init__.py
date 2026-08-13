# Implements: FR-002, FR-013, DR-002, DR-003, OPS-002
"""Validate raw batch → curated upserts + validation report."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from athletiq.load.store import CuratedStore, InMemoryCuratedStore
from athletiq.validate import ValidationReport
from athletiq.validate.parse import parse_game, parse_team

logger = logging.getLogger("athletiq.load")


class CriticalEmptyError(RuntimeError):
    """Execution failure: zero teams or zero games for a required season."""


def _read_response(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "response" in data:
        return list(data["response"])
    if isinstance(data, list):
        return list(data)
    return []


def load_raw_batch(
    batch_dir: Path,
    store: CuratedStore | None = None,
    *,
    required_seasons: list[int] | None = None,
) -> tuple[CuratedStore, ValidationReport]:
    """Load one immutable raw batch into curated store.

    Skips invalid rows (counted in report). Fails if teams==0 or any required
    season has zero games after load.
    """
    store = store or InMemoryCuratedStore()
    batch_dir = Path(batch_dir)
    report = ValidationReport(batch_id=batch_dir.name)

    manifest_path = batch_dir / "manifest.json"
    if required_seasons is None and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required_seasons = list(manifest.get("active_seasons") or [])
    required_seasons = required_seasons or []
    report.required_seasons = list(required_seasons)

    teams_path = batch_dir / "teams.json"
    if not teams_path.exists():
        raise CriticalEmptyError(f"missing teams.json in {batch_dir}")

    for raw in _read_response(teams_path):
        report.teams_seen += 1
        parsed = parse_team(raw)
        if isinstance(parsed, str):
            report.teams_skipped += 1
            report.add_skip(f"team: {parsed}")
            continue
        store.upsert_team(parsed)
        report.teams_loaded += 1

    if store.count_teams() == 0:
        logger.error("stage=load reason=zero_teams batch=%s", batch_dir.name)
        raise CriticalEmptyError("zero teams after load")

    provider_to_internal: dict[str, int] = {}
    # Re-walk loaded teams via upserts already done — MemoryStore keeps map;
    # for protocol generality, re-parse valid teams to build id map.
    for raw in _read_response(teams_path):
        parsed = parse_team(raw)
        if isinstance(parsed, str):
            continue
        provider_to_internal[parsed.provider_team_id] = store.upsert_team(parsed)

    game_files = sorted(batch_dir.glob("games_*.json"))
    for path in game_files:
        try:
            season_default = int(path.stem.split("_", 1)[1])
        except (IndexError, ValueError):
            season_default = None
        for raw in _read_response(path):
            report.games_seen += 1
            parsed = parse_game(raw, default_season=season_default)
            if isinstance(parsed, str):
                report.games_skipped += 1
                report.add_skip(f"game: {parsed}")
                continue
            home_tid = provider_to_internal.get(parsed.home_provider_team_id)
            away_tid = provider_to_internal.get(parsed.away_provider_team_id)
            if home_tid is None or away_tid is None:
                report.games_skipped += 1
                report.add_skip("game: unknown team provider id")
                continue
            game_id = store.upsert_game(parsed, home_tid, away_tid)
            report.games_loaded += 1
            # Derived team_game_stats grain
            store.upsert_team_game_stats(
                game_id=game_id,
                team_id=home_tid,
                is_home=True,
                points_for=parsed.home_score,
                points_against=parsed.away_score,
            )
            store.upsert_team_game_stats(
                game_id=game_id,
                team_id=away_tid,
                is_home=False,
                points_for=parsed.away_score,
                points_against=parsed.home_score,
            )
            report.team_stats_upserted += 2

    for season in required_seasons:
        if store.count_games(season) == 0:
            logger.error(
                "stage=load reason=zero_games_for_season season=%s batch=%s",
                season,
                batch_dir.name,
            )
            raise CriticalEmptyError(f"zero games for required season {season}")

    logger.info(
        "stage=load batch=%s teams=%s games=%s skipped_teams=%s skipped_games=%s",
        batch_dir.name,
        report.teams_loaded,
        report.games_loaded,
        report.teams_skipped,
        report.games_skipped,
    )
    return store, report


def write_validation_report(report: ValidationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
