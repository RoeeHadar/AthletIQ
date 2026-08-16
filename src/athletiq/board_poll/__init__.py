# Implements: FR-026, ADR-015, CR-005
"""Compose board poll: newest nba-stats pages through the adapter (not a fourth service)."""

from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Callable

from athletiq.config import load_settings
from athletiq.db.migrate import apply_migrations
from athletiq.logging import configure_logging
from athletiq.provider.nba_stats import NBA_TEAM_NAMES, NbaStatsApiProvider
from athletiq.validate.parse import parse_game, parse_team

logger = logging.getLogger("athletiq.board_poll")

DEFAULT_INTERVAL = 30


def _team_record(code: str):
    return parse_team(
        {
            "id": code,
            "name": NBA_TEAM_NAMES.get(code, code),
            "code": code,
            "league": "nba",
        }
    )


def upsert_mapped_games(database_url: str, games: list[dict[str, Any]]) -> int:
    import psycopg
    from psycopg.rows import dict_row

    from athletiq.load.postgres import PostgresCuratedStore

    n = 0
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        store = PostgresCuratedStore(conn)
        with conn.transaction():
            for raw in games:
                parsed = parse_game(raw)
                if isinstance(parsed, str):
                    continue
                home_rec = _team_record(parsed.home_provider_team_id)
                away_rec = _team_record(parsed.away_provider_team_id)
                if isinstance(home_rec, str) or isinstance(away_rec, str):
                    continue
                home_id = store.upsert_team(home_rec)
                away_id = store.upsert_team(away_rec)
                gid = store.upsert_game(parsed, home_id, away_id)
                store.upsert_team_game_stats(
                    game_id=gid,
                    team_id=home_id,
                    is_home=True,
                    points_for=parsed.home_score,
                    points_against=parsed.away_score,
                )
                store.upsert_team_game_stats(
                    game_id=gid,
                    team_id=away_id,
                    is_home=False,
                    points_for=parsed.away_score,
                    points_against=parsed.home_score,
                )
                n += 1
    return n


def poll_once(
    *,
    database_url: str,
    get_json: Callable[[str], dict[str, Any]] | None = None,
    pages: int = 1,
) -> int:
    provider = NbaStatsApiProvider(get_json=get_json, pause_seconds=0, max_pages=pages)
    mapped = provider.fetch_newest_pages(pages=pages)
    return upsert_mapped_games(database_url, mapped)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="athletiq.board_poll")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level, secrets=settings.secret_values())
    if not settings.database_url:
        logger.error("DATABASE_URL required for board poll")
        return 1
    apply_migrations(settings.database_url)
    while True:
        try:
            n = poll_once(database_url=settings.database_url, pages=args.pages)
            logger.info("board_poll upserted=%s", n)
        except Exception:
            logger.exception("board_poll failed")
        if args.once:
            return 0
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
