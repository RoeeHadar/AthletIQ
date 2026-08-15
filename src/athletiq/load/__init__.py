# Implements: FR-002, FR-013, FR-017, FR-018, DR-002, DR-003, OPS-002, CR-004
"""Validate raw batch → curated upserts + validation report."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from athletiq.load.store import CuratedStore, InMemoryCuratedStore
from athletiq.validate import ValidationReport
from athletiq.validate.parse import (
    parse_game,
    parse_odds_snapshot,
    parse_player,
    parse_player_game_stat,
    parse_team,
)

logger = logging.getLogger("athletiq.load")


class CriticalEmptyError(RuntimeError):
    """Execution failure: zero teams or zero games for a required season."""


def _read_response(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "response" in data:
        return list(data["response"])
    if isinstance(data, list):
        return list(data)
    return []


def _season_and_league_from_games_path(path: Path) -> tuple[int | None, str]:
    parts = path.stem.split("_")
    season: int | None
    try:
        season = int(parts[-1])
    except (IndexError, ValueError):
        season = None
    if len(parts) >= 3:
        return season, parts[1].lower()
    return season, "nba"


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

    provider_to_internal: dict[tuple[str, str], int] = {}
    for raw in _read_response(teams_path):
        parsed = parse_team(raw)
        if isinstance(parsed, str):
            continue
        provider_to_internal[(parsed.league, parsed.provider_team_id)] = store.upsert_team(
            parsed
        )

    game_files = sorted(batch_dir.glob("games_*.json"))
    game_internal: dict[tuple[str, str], int] = {}
    for path in game_files:
        season_default, league_default = _season_and_league_from_games_path(path)
        for raw in _read_response(path):
            report.games_seen += 1
            if "league" not in raw:
                raw = {**raw, "league": league_default}
            parsed = parse_game(raw, default_season=season_default)
            if isinstance(parsed, str):
                report.games_skipped += 1
                report.add_skip(f"game: {parsed}")
                continue
            home_tid = provider_to_internal.get(
                (parsed.league, parsed.home_provider_team_id)
            )
            away_tid = provider_to_internal.get(
                (parsed.league, parsed.away_provider_team_id)
            )
            if home_tid is None or away_tid is None:
                report.games_skipped += 1
                report.add_skip("game: unknown team provider id")
                continue
            game_id = store.upsert_game(parsed, home_tid, away_tid)
            game_internal[(parsed.league, parsed.provider_game_id)] = game_id
            report.games_loaded += 1
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

    player_internal: dict[tuple[str, str], int] = {}
    for raw in _read_response(batch_dir / "players.json"):
        parsed_p = parse_player(raw)
        if isinstance(parsed_p, str):
            report.add_skip(f"player: {parsed_p}")
            continue
        team_id = None
        if parsed_p.provider_team_id:
            team_id = provider_to_internal.get((parsed_p.league, parsed_p.provider_team_id))
        pid = store.upsert_player(parsed_p, team_id)
        player_internal[(parsed_p.league, parsed_p.provider_player_id)] = pid
        report.players_loaded += 1

    for raw in _read_response(batch_dir / "player_game_stats.json"):
        parsed_s = parse_player_game_stat(raw)
        if isinstance(parsed_s, str):
            report.add_skip(f"player_game_stat: {parsed_s}")
            continue
        gid = game_internal.get((parsed_s.league, parsed_s.provider_game_id))
        pid = player_internal.get((parsed_s.league, parsed_s.provider_player_id))
        tid = provider_to_internal.get((parsed_s.league, parsed_s.provider_team_id))
        if gid is None or pid is None or tid is None:
            report.add_skip("player_game_stat: unknown game/player/team")
            continue
        store.upsert_player_game_stats(
            game_id=gid, player_id=pid, team_id=tid, stat=parsed_s
        )
        report.player_stats_upserted += 1

    for raw in _read_response(batch_dir / "odds_snapshots.json"):
        parsed_o = parse_odds_snapshot(raw)
        if isinstance(parsed_o, str):
            report.add_skip(f"odds: {parsed_o}")
            continue
        gid = game_internal.get((parsed_o.league, parsed_o.provider_game_id))
        if gid is None:
            report.add_skip("odds: unknown game")
            continue
        store.upsert_odds_snapshot(gid, parsed_o)
        report.odds_loaded += 1

    for season in required_seasons:
        if store.count_games(season) == 0:
            logger.error(
                "stage=load reason=zero_games_for_season season=%s batch=%s",
                season,
                batch_dir.name,
            )
            raise CriticalEmptyError(f"zero games for required season {season}")

    logger.info(
        "stage=load batch=%s teams=%s games=%s players=%s odds=%s",
        batch_dir.name,
        report.teams_loaded,
        report.games_loaded,
        report.players_loaded,
        report.odds_loaded,
    )
    return store, report


def write_validation_report(report: ValidationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
