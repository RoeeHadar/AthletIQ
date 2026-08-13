# TEST-013
"""TEST-013 — training reproducibility on a controlled synthetic fixture.

Environment assumptions (pinned):
- Exact structural/selection equality is required for this controlled fixture + seed.
- Exact numeric metric equality is expected on the CI/local pinned Python/sklearn/xgboost
  toolchain for this fixture. This is NOT a claim of bit-for-bit XGBoost identity on every
  machine forever. If floating-point drift appears across platforms, document a tolerance
  here rather than weakening structural asserts (architecture: reproducible within
  documented tolerances).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from athletiq.features import FEATURE_VERSION, TeamGameHistory, build_feature_row, feature_vector
from athletiq.ml.pipeline import run_train_select_publish
from athletiq.ml.publish import load_pin
from athletiq.ml.splits import temporal_split

# Controlled fixture seed — keep stable for TEST-013.
SEED = 42
DATASET_VERSION = "test-013-synthetic-v1"


def _history(n_games: int = 40) -> tuple[list[TeamGameHistory], list[dict]]:
    """Deterministic team history + tips for feature rows."""
    start = datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc)
    history: list[TeamGameHistory] = []
    games_meta: list[dict] = []
    for i in range(n_games):
        tip = start + timedelta(days=i)
        # Alternate outcomes with a slight home bias tied to index.
        home_win = (i % 3) != 0
        pf, pa = 100 + (i % 10), 95 + ((i * 2) % 10)
        history.append(
            TeamGameHistory(
                team_id=1,
                game_start_time=tip,
                won=home_win,
                points_for=pf,
                points_against=pa,
                season=2023,
            )
        )
        history.append(
            TeamGameHistory(
                team_id=2,
                game_start_time=tip,
                won=not home_win,
                points_for=pa,
                points_against=pf,
                season=2023,
            )
        )
        games_meta.append(
            {
                "game_id": i + 1,
                "tip": tip,
                "label": 1 if home_win else 0,
            }
        )
    return history, games_meta


def _build_matrix(history: list[TeamGameHistory], games_meta: list[dict]):
    X_rows: list[list[float]] = []
    y: list[float] = []
    home_wr: list[float] = []
    away_wr: list[float] = []
    versions: list[str] = []
    for g in games_meta:
        row = build_feature_row(
            game_id=g["game_id"],
            tip=g["tip"],
            season=2023,
            home_team_id=1,
            away_team_id=2,
            history=history,
            label_home_win=g["label"],
        )
        versions.append(row.feature_version)
        vec = feature_vector(row.payload)
        X_rows.append(vec)
        y.append(float(g["label"]))
        home_wr.append(float(row.payload["home_season_wr"]))
        away_wr.append(float(row.payload["away_season_wr"]))
    return (
        np.asarray(X_rows, dtype=float),
        np.asarray(y, dtype=float),
        np.asarray(home_wr, dtype=float),
        np.asarray(away_wr, dtype=float),
        versions,
    )


def _run_once(artifacts: Path):
    history, meta = _history()
    X, y, home_wr, away_wr, versions = _build_matrix(history, meta)
    split = temporal_split(len(y))
    result = run_train_select_publish(
        X=X,
        y=y,
        home_season_wr=home_wr,
        away_season_wr=away_wr,
        artifacts_dir=artifacts,
        dataset_version=DATASET_VERSION,
        code_commit="test-013",
        seed=SEED,
        feature_version=FEATURE_VERSION,
        model_version=None,
        evaluate_test=True,
    )
    pin = load_pin(artifacts)
    return {
        "X": X,
        "y": y,
        "versions": versions,
        "split": split,
        "result": result,
        "pin": pin,
        "test_metrics": result.test_metrics,
        "selected_family": result.selected_family,
    }


def test_reproducibility_two_runs_exact_structure_and_selection(tmp_path: Path) -> None:
    a = _run_once(tmp_path / "a")
    b = _run_once(tmp_path / "b")

    # Exact: feature version + vectors + labels
    assert a["versions"] == b["versions"]
    assert all(v == FEATURE_VERSION for v in a["versions"])
    assert np.array_equal(a["X"], b["X"])
    assert np.array_equal(a["y"], b["y"])

    # Exact: split membership
    assert a["split"].train == b["split"].train
    assert a["split"].validation == b["split"].validation
    assert a["split"].test == b["split"].test

    # Exact: selection decision / family / dataset / seed lineage
    assert a["selected_family"] == b["selected_family"]
    assert a["pin"]["feature_version"] == b["pin"]["feature_version"] == FEATURE_VERSION
    assert a["result"].feature_version == b["result"].feature_version
    assert a["result"].model_version == b["result"].model_version
    assert a["pin"]["model_version"] == a["result"].model_version
    assert a["pin"]["artifact"] == b["pin"]["artifact"]

    # Numeric metrics: exact on this controlled path (tolerance documented in module docstring)
    assert a["test_metrics"] is not None and b["test_metrics"] is not None
    assert a["test_metrics"]["log_loss"] == b["test_metrics"]["log_loss"]
    assert a["test_metrics"]["accuracy"] == b["test_metrics"]["accuracy"]
