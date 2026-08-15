# TEST-009
"""TEST-009 — thin script → CLI; happy path; forced stage failure."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from athletiq.config import Settings
from athletiq.pipeline import STAGE_ORDER, PipelineContext, PipelineError, run_pipeline
from athletiq.pipeline.__main__ import default_fixtures_dir
from athletiq.pipeline.__main__ import main as pipeline_main
from athletiq.pipeline.orchestrator import resolve_stages

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_pipeline.sh"
FIXTURES = ROOT / "tests" / "fixtures" / "provider"


class _ManyGamesProvider:
    """Offline provider with enough finished games for temporal train."""

    def __init__(self, n_games: int = 40) -> None:
        self.n_games = n_games

    def leagues(self) -> list[str]:
        return ["nba"]

    def fetch_teams(self) -> list[dict[str, Any]]:
        return [
            {"id": 1, "name": "Boston Celtics", "code": "BOS", "league": "nba"},
            {"id": 2, "name": "Los Angeles Lakers", "code": "LAL", "league": "nba"},
        ]

    def fetch_games(self, season: int, league: str = "nba") -> list[dict[str, Any]]:
        if league != "nba" or season != 2023:
            return []
        start = datetime(2023, 10, 24, 23, 30, tzinfo=timezone.utc)
        games: list[dict[str, Any]] = []
        for i in range(self.n_games):
            home_score = 100 + (i % 20)
            away_score = 95 + ((i * 3) % 20)
            tip = start + timedelta(days=i)
            games.append(
                {
                    "id": 10_000 + i,
                    "date": tip.isoformat(),
                    "season": season,
                    "status": "Finished",
                    "teams": {
                        "home": {"id": 1, "name": "Boston Celtics"},
                        "away": {"id": 2, "name": "Los Angeles Lakers"},
                    },
                    "scores": {
                        "home": {"total": home_score},
                        "away": {"total": away_score},
                    },
                }
            )
        return games

    def fetch_players(self) -> list[dict[str, Any]]:
        return []

    def fetch_player_game_stats(self) -> list[dict[str, Any]]:
        return []

    def fetch_odds_snapshots(self) -> list[dict[str, Any]]:
        return []


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url="postgresql://athletiq:athletiq@localhost:5432/athletiq",
        api_sports_key=None,
        seed=42,
        raw_path=tmp_path / "raw",
        artifacts_path=tmp_path / "artifacts",
        log_level="INFO",
    )


def test_default_fixtures_dir_finds_repo_fixtures() -> None:
    found = default_fixtures_dir()
    assert (found / "teams.json").is_file()
    assert found.resolve() == FIXTURES.resolve()


def test_script_is_thin_wrapper_to_python_cli() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "python -m athletiq.pipeline" in text
    assert "--store postgres" in text
    # No per-stage orchestration in bash (ADR-005).
    for stage in STAGE_ORDER:
        assert f"stage={stage}" not in text
        assert f"athletiq.{stage}" not in text


def test_resolve_stages_window_and_only() -> None:
    assert resolve_stages(from_stage="load", to_stage="features") == ["load", "features"]
    assert resolve_stages(only=["train", "ingest"]) == ["ingest", "train"]
    with pytest.raises(PipelineError):
        resolve_stages(from_stage="train", to_stage="ingest")


def test_happy_path_exit_zero_and_artifacts(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="athletiq.pipeline")
    ctx = PipelineContext(
        settings=_settings(tmp_path),
        provider=_ManyGamesProvider(40),
        raw_root=tmp_path / "raw",
        artifacts_dir=tmp_path / "artifacts",
        seasons=[2023],
        batch_id="happy1",
    )
    run_pipeline(ctx, list(STAGE_ORDER))
    assert (tmp_path / "artifacts" / "pipeline_state.json").is_file()
    assert (tmp_path / "artifacts" / "feature_matrix.npz").is_file()
    assert (tmp_path / "artifacts" / "selected_pin.json").is_file()
    assert (tmp_path / "artifacts" / "reports" / "validation_happy1.json").is_file()
    assert any("stage=train status=ok" in r.message for r in caplog.records)
    pin = json.loads((tmp_path / "artifacts" / "selected_pin.json").read_text(encoding="utf-8"))
    assert pin.get("schema") == "athletiq.pins.v2"
    assert "nba" in pin.get("pins", {})


def test_postgres_store_applies_migrations_before_stages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[str] = []

    def fake_apply(url: str, *, directory=None):  # noqa: ANN001
        called.append(url)
        return ["001_initial", "002_cr004_league_players_odds"]

    monkeypatch.setattr("athletiq.db.migrate.apply_migrations", fake_apply)
    ctx = PipelineContext(
        settings=_settings(tmp_path),
        provider=_ManyGamesProvider(3),
        raw_root=tmp_path / "raw",
        artifacts_dir=tmp_path / "artifacts",
        store_kind="postgres",
        seasons=[2023],
        batch_id="mig1",
    )
    run_pipeline(ctx, [])
    assert called == ["postgresql://athletiq:athletiq@localhost:5432/athletiq"]


def test_forced_stage_failure_nonzero_and_stage_in_logs(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR, logger="athletiq.pipeline")

    def boom(_ctx: PipelineContext) -> None:
        raise RuntimeError("forced failure")

    ctx = PipelineContext(
        settings=_settings(tmp_path),
        provider=_ManyGamesProvider(5),
        raw_root=tmp_path / "raw",
        artifacts_dir=tmp_path / "artifacts",
        seasons=[2023],
        batch_id="fail1",
    )
    with pytest.raises(PipelineError) as ei:
        run_pipeline(ctx, ["ingest", "load"], stage_fns={"load": boom})
    assert ei.value.stage == "load"
    assert any("stage=load" in r.message and "failed" in r.message for r in caplog.records)


def test_cli_main_failure_returns_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATHLETIQ_RAW_PATH", str(tmp_path / "raw"))
    monkeypatch.setenv("ATHLETIQ_ARTIFACTS_PATH", str(tmp_path / "artifacts"))
    tiny = tmp_path / "tiny_fixtures"
    tiny.mkdir()
    (tiny / "teams.json").write_text(
        (FIXTURES / "teams.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    one_game = {
        "response": [
            {
                "id": 1,
                "date": "2023-10-24T23:30:00+00:00",
                "status": "Finished",
                "teams": {
                    "home": {"id": 1, "name": "Boston Celtics"},
                    "away": {"id": 2, "name": "Los Angeles Lakers"},
                },
                "scores": {"home": {"total": 110}, "away": {"total": 105}},
            }
        ]
    }
    (tiny / "games_2023.json").write_text(json.dumps(one_game), encoding="utf-8")
    one_game["response"][0]["id"] = 2
    one_game["response"][0]["date"] = "2024-10-22T23:30:00+00:00"
    (tiny / "games_2024.json").write_text(json.dumps(one_game), encoding="utf-8")
    # Two labeled games → train must fail with identifiable stage.
    code = pipeline_main(
        [
            "--provider",
            "fixture",
            "--fixtures-dir",
            str(tiny),
            "--seasons",
            "2023",
            "2024",
            "--batch-id",
            "cli-fail",
            "--raw-path",
            str(tmp_path / "raw"),
            "--artifacts-path",
            str(tmp_path / "artifacts"),
        ]
    )
    assert code == 1
