# TEST-004
"""TEST-004 — validate/load/report/idempotency (in-memory curated store)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from athletiq.ingest import ingest_raw, write_raw_json
from athletiq.load import CriticalEmptyError, load_raw_batch, write_validation_report
from athletiq.load.store import InMemoryCuratedStore
from athletiq.provider.fixture import FixtureProvider
from athletiq.prune import seasons_to_prune

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "provider"


@pytest.fixture
def raw_batch(tmp_path: Path) -> Path:
    provider = FixtureProvider(FIXTURES)
    return ingest_raw(
        provider,
        tmp_path / "raw",
        seasons=[2023, 2024],
        batch_id="t004",
    )


def test_load_valid_batch(raw_batch: Path) -> None:
    store, report = load_raw_batch(raw_batch, required_seasons=[2023, 2024])
    assert store.count_teams() == 2
    assert store.count_games(2023) >= 1
    assert store.count_games(2024) >= 1
    assert report.teams_loaded == 2
    assert report.games_loaded >= 2
    assert report.teams_skipped == 0


def test_skip_invalid_row_counted(raw_batch: Path, tmp_path: Path) -> None:
    # Copy batch and inject invalid team
    dirty = tmp_path / "dirty"
    shutil.copytree(raw_batch, dirty)
    teams_path = dirty / "teams.json"
    data = json.loads(teams_path.read_text(encoding="utf-8"))
    data["response"].append({"id": 99})  # missing name
    # teams.json is immutable in real raw — for test we rewrite a copy
    teams_path.write_text(json.dumps(data), encoding="utf-8")

    store, report = load_raw_batch(dirty, required_seasons=[2023, 2024])
    assert report.teams_skipped == 1
    assert any("missing id or name" in r for r in report.skip_reasons)
    assert store.count_teams() == 2


def test_idempotent_rerun_no_duplicate_grain(raw_batch: Path) -> None:
    store = InMemoryCuratedStore()
    load_raw_batch(raw_batch, store, required_seasons=[2023, 2024])
    teams_1 = store.count_teams()
    games_1 = store.count_games()
    stats_1 = store.count_team_game_stats()

    load_raw_batch(raw_batch, store, required_seasons=[2023, 2024])
    assert store.count_teams() == teams_1
    assert store.count_games() == games_1
    assert store.count_team_game_stats() == stats_1


def test_zero_games_for_required_season_fails(tmp_path: Path) -> None:
    batch = tmp_path / "empty_games"
    batch.mkdir()
    write_raw_json(
        batch / "teams.json",
        {"response": [{"id": 1, "name": "Only Team"}]},
    )
    write_raw_json(batch / "games_2024.json", {"response": [], "season": 2024})
    write_raw_json(
        batch / "manifest.json",
        {"batch_id": "empty_games", "active_seasons": [2024]},
    )

    with pytest.raises(CriticalEmptyError, match="zero games"):
        load_raw_batch(batch, required_seasons=[2024])


def test_zero_teams_fails(tmp_path: Path) -> None:
    batch = tmp_path / "no_teams"
    batch.mkdir()
    write_raw_json(batch / "teams.json", {"response": [{"id": 1}]})  # invalid only
    write_raw_json(batch / "manifest.json", {"active_seasons": [2024]})

    with pytest.raises(CriticalEmptyError, match="zero teams"):
        load_raw_batch(batch, required_seasons=[2024])


def test_validation_report_written(raw_batch: Path, tmp_path: Path) -> None:
    _, report = load_raw_batch(raw_batch, required_seasons=[2023, 2024])
    out = tmp_path / "reports" / "validation.json"
    write_validation_report(report, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["teams_loaded"] == 2
    assert "skip_reasons" in payload


def test_prune_helper_flags_too_old() -> None:
    from unittest.mock import patch

    with patch(
        "athletiq.prune.active_season_years",
        return_value=[2024, 2023],
    ):
        assert seasons_to_prune({2024, 2023, 2020}, depth=2) == [2020]
