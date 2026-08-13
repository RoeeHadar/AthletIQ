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
