# TEST-003
"""TEST-003 — fixture ingest, immutability, season window, retries."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from athletiq.ingest import ingest_raw, write_raw_json
from athletiq.provider.api_sports import ApiSportsProvider
from athletiq.provider.fixture import FixtureProvider
from athletiq.provider.nba_stats import NbaStatsApiProvider, to_provider_game
from athletiq.provider.retry import compute_backoff_seconds, parse_retry_after, retry_with_backoff
from athletiq.provider.seasons import active_season_years, is_season_in_window

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "provider"


def test_active_season_window_depth() -> None:
    seasons = active_season_years(as_of=date(2026, 3, 1), depth=2)
    assert seasons == [2024, 2023]
    assert is_season_in_window(2024, seasons)
    assert not is_season_in_window(2020, seasons)


def test_retry_honors_retry_after_and_max_attempts() -> None:
    calls = {"n": 0}

    def boom() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            err = RuntimeError("busy")
            err.retry_after = "0"  # type: ignore[attr-defined]
            raise err
        return "ok"

    sleeps: list[float] = []
    result = retry_with_backoff(
        boom,
        is_retryable=lambda _e: True,
        get_retry_after=lambda e: parse_retry_after(getattr(e, "retry_after", None)),
        sleep=sleeps.append,
        max_attempts=5,
    )
    assert result == "ok"
    assert calls["n"] == 3
    assert sleeps == [0.0, 0.0]


def test_retry_gives_up_after_max() -> None:
    def always_fail() -> None:
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError, match="nope"):
        retry_with_backoff(
            always_fail,
            is_retryable=lambda _e: True,
            sleep=lambda _d: None,
            max_attempts=5,
        )


def test_compute_backoff_uses_retry_after() -> None:
    assert compute_backoff_seconds(0, retry_after=1.5) == 1.5


def test_fixture_ingest_writes_immutable_batch(tmp_path: Path) -> None:
    provider = FixtureProvider(FIXTURES)
    batch = ingest_raw(
        provider,
        tmp_path / "raw",
        seasons=[2023, 2024],
        batch_id="batch1",
    )
    assert (batch / "teams.json").is_file()
    assert (batch / "games_2023.json").is_file()
    assert (batch / "games_2024.json").is_file()
    teams = json.loads((batch / "teams.json").read_text(encoding="utf-8"))
    assert len(teams["response"]) == 2

    with pytest.raises(FileExistsError):
        write_raw_json(batch / "teams.json", {"response": []})

    with pytest.raises(FileExistsError):
        ingest_raw(provider, tmp_path / "raw", seasons=[2023], batch_id="batch1")


def test_ingest_skips_out_of_window_seasons(tmp_path: Path) -> None:
    class DualProvider:
        def fetch_teams(self):
            return [{"id": 1, "name": "X"}]

        def fetch_games(self, season: int):
            return [{"id": season, "season": season}]

    batch = ingest_raw(
        DualProvider(),
        tmp_path / "raw",
        seasons=[2024],
        batch_id="win1",
    )
    assert (batch / "games_2024.json").is_file()
    assert not (batch / "games_2020.json").exists()


def test_api_key_injected_not_hardcoded() -> None:
    with pytest.raises(ValueError):
        ApiSportsProvider("")
    client = ApiSportsProvider("from-env-only")
    assert client._api_key == "from-env-only"


def test_nba_stats_maps_aliases_and_skips_unusable() -> None:
    ok = to_provider_game(
        {
            "gameId": "202401150LAL",
            "date": "2024-01-15T02:00:00.000Z",
            "homeTeam": "LAL",
            "visitorTeam": "PHO",
            "homePts": 105,
            "visitorPts": 101,
        }
    )
    assert ok is not None
    assert ok["season"] == 2023
    assert ok["teams"]["away"]["id"] == "PHX"
    assert ok["scores"]["home"]["total"] == 105
    assert to_provider_game(
        {
            "gameId": "202402180ASG",
            "date": "2024-02-18T00:00:00.000Z",
            "homeTeam": "EST",
            "visitorTeam": "WST",
            "homePts": 200,
            "visitorPts": 180,
        }
    ) is None
    assert to_provider_game(
        {
            "gameId": "202310250CHI",
            "date": "2023-10-25T00:00:00.000Z",
            "homeTeam": "CHI",
            "visitorTeam": "ATL",
            "homePts": None,
            "visitorPts": None,
        }
    ) is None


def test_nba_stats_pages_filter_and_stop_without_live_http() -> None:
    pages = {
        1: {
            "data": [
                {
                    "gameId": "202510220BOS",
                    "date": "2025-10-22T23:00:00.000Z",
                    "homeTeam": "BOS",
                    "visitorTeam": "NYK",
                    "homePts": 100,
                    "visitorPts": 90,
                },
                {
                    "gameId": "202410220BOS",
                    "date": "2024-10-22T23:00:00.000Z",
                    "homeTeam": "BOS",
                    "visitorTeam": "NYK",
                    "homePts": 110,
                    "visitorPts": 99,
                },
            ],
            "pagination": {"page": 1, "pages": 3},
        },
        2: {
            "data": [
                {
                    "gameId": "202401150LAL",
                    "date": "2024-01-15T02:00:00.000Z",
                    "homeTeam": "LAL",
                    "visitorTeam": "PHO",
                    "homePts": 105,
                    "visitorPts": 101,
                },
                {
                    "gameId": "202310240BOS",
                    "date": "2023-10-24T23:30:00.000Z",
                    "homeTeam": "BOS",
                    "visitorTeam": "LAL",
                    "homePts": 108,
                    "visitorPts": 104,
                },
            ],
            "pagination": {"page": 2, "pages": 3},
        },
        3: {
            "data": [
                {
                    "gameId": "202206160GSW",
                    "date": "2022-06-16T00:00:00.000Z",
                    "homeTeam": "GSW",
                    "visitorTeam": "BOS",
                    "homePts": 103,
                    "visitorPts": 90,
                }
            ],
            "pagination": {"page": 3, "pages": 3},
        },
    }
    calls: list[str] = []

    def get_json(url: str) -> dict:
        calls.append(url)
        if "page=1" in url:
            return pages[1]
        if "page=2" in url:
            return pages[2]
        if "page=3" in url:
            return pages[3]
        raise AssertionError(f"unexpected url {url}")

    provider = NbaStatsApiProvider(
        seasons=[2023, 2024],
        get_json=get_json,
        pause_seconds=0,
    )
    games_2024 = provider.fetch_games(2024)
    games_2023 = provider.fetch_games(2023)
    assert [g["id"] for g in games_2024] == ["202410220BOS"]
    assert {g["id"] for g in games_2023} == {"202401150LAL", "202310240BOS"}
    teams = {t["id"] for t in provider.fetch_teams()}
    assert "BOS" in teams and "PHX" in teams
    assert len(teams) == 30
    assert len(calls) == 3
    assert all("/api/games?" in c for c in calls)
