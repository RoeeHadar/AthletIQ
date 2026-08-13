# TEST-009
"""TEST-009 — thin script → CLI; happy path; forced stage failure."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from athletiq.config import Settings
from athletiq.pipeline import STAGE_ORDER, PipelineContext, PipelineError, run_pipeline
from athletiq.pipeline.__main__ import main as pipeline_main
from athletiq.pipeline.orchestrator import resolve_stages

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_pipeline.sh"
FIXTURES = ROOT / "tests" / "fixtures" / "provider"


class _ManyGamesProvider:
    """Offline provider with enough finished games for temporal train."""

    def __init__(self, n_games: int = 40) -> None:
        self.n_games = n_games

    def fetch_teams(self) -> list[dict[str, Any]]:
        return [
            {"id": 1, "name": "Boston Celtics", "code": "BOS"},
            {"id": 2, "name": "Los Angeles Lakers", "code": "LAL"},
        ]

    def fetch_games(self, season: int) -> list[dict[str, Any]]:
        if season != 2023:
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


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url="postgresql://athletiq:athletiq@localhost:5432/athletiq",
        api_sports_key=None,
        seed=42,
        raw_path=tmp_path / "raw",
        artifacts_path=tmp_path / "artifacts",
        log_level="INFO",
    )


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
    # Fixture provider only has 2 games → train must fail with identifiable stage.
    code = pipeline_main(
        [
            "--provider",
            "fixture",
            "--fixtures-dir",
            str(FIXTURES),
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
