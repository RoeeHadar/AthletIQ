# Implements: FR-011, CON-001, OPS-002, ADR-005
"""Concrete pipeline stage implementations (offline-capable)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

from athletiq.features.builder import (
    FEATURE_VERSION,
    TeamGameHistory,
    build_feature_row,
    feature_vector,
)
from athletiq.features.store import InMemoryFeatureStore
from athletiq.ingest import ingest_raw, new_batch_id
from athletiq.load import load_raw_batch, write_validation_report
from athletiq.load.store import InMemoryCuratedStore
from athletiq.ml.pipeline import run_train_select_publish
from athletiq.pipeline.orchestrator import PipelineContext, PipelineError

logger = logging.getLogger("athletiq.pipeline")


def _open_curated_store(ctx: PipelineContext):
    if ctx.store_kind == "memory":
        return InMemoryCuratedStore()
    if ctx.store_kind == "postgres":
        from athletiq.load.postgres import PostgresCuratedStore

        return PostgresCuratedStore.connect(ctx.settings.database_url)
    raise PipelineError("load", f"unknown store_kind={ctx.store_kind}")


def _open_feature_store(ctx: PipelineContext):
    if ctx.store_kind == "memory":
        return InMemoryFeatureStore()
    if ctx.store_kind == "postgres":
        from athletiq.features.postgres import PostgresFeatureStore

        return PostgresFeatureStore.connect(ctx.settings.database_url)
    raise PipelineError("features", f"unknown store_kind={ctx.store_kind}")


def stage_ingest(ctx: PipelineContext) -> None:
    batch_id = ctx.batch_id or new_batch_id()
    batch_dir = ingest_raw(
        ctx.provider,
        ctx.raw_root,
        season_depth=ctx.season_depth,
        seasons=ctx.seasons,
        batch_id=batch_id,
    )
    ctx.batch_id = batch_id
    ctx.batch_dir = batch_dir
    logger.info("stage=ingest batch=%s path=%s", batch_id, batch_dir)


def stage_load(ctx: PipelineContext) -> None:
    batch_dir = ctx.batch_dir
    if batch_dir is None:
        batch_dir = _latest_batch(ctx.raw_root)
        ctx.batch_dir = batch_dir
        ctx.batch_id = batch_dir.name

    store = _open_curated_store(ctx)
    try:
        txn = getattr(store, "transaction", None)
        if txn is not None:
            with txn():
                store, report = load_raw_batch(batch_dir, store=store)
        else:
            store, report = load_raw_batch(batch_dir, store=store)
    except Exception:
        close = getattr(store, "close", None)
        if close:
            close()
        raise

    report_path = ctx.artifacts_dir / "reports" / f"validation_{batch_dir.name}.json"
    write_validation_report(report, report_path)
    ctx.store = store
    logger.info(
        "stage=load batch=%s teams=%s games=%s report=%s store=%s",
        batch_dir.name,
        report.teams_loaded,
        report.games_loaded,
        report_path,
        ctx.store_kind,
    )


def stage_features(ctx: PipelineContext) -> None:
    store = ctx.store
    if store is None:
        raise PipelineError("features", "no curated store; run load first")

    history: list[TeamGameHistory] = []
    games = store.iter_games()
    for g in games:
        rec = g.record
        if rec.home_score is None or rec.away_score is None:
            continue
        home_stat = store.team_stat(g.game_id, g.home_team_id) or {}
        away_stat = store.team_stat(g.game_id, g.away_team_id) or {}
        history.append(
            TeamGameHistory(
                team_id=g.home_team_id,
                game_start_time=rec.game_start_time,
                won=bool(rec.home_win),
                points_for=int(home_stat.get("points_for") or rec.home_score),
                points_against=int(home_stat.get("points_against") or rec.away_score),
                season=rec.season,
            )
        )
        history.append(
            TeamGameHistory(
                team_id=g.away_team_id,
                game_start_time=rec.game_start_time,
                won=not bool(rec.home_win) if rec.home_win is not None else False,
                points_for=int(away_stat.get("points_for") or rec.away_score),
                points_against=int(away_stat.get("points_against") or rec.home_score),
                season=rec.season,
            )
        )

    feature_store = _open_feature_store(ctx)
    rows_meta: list[dict] = []
    X_rows: list[list[float]] = []
    y_rows: list[float] = []
    home_wr: list[float] = []
    away_wr: list[float] = []

    try:
        txn = getattr(feature_store, "transaction", None)
        if txn is not None:
            with txn():
                _build_and_persist_features(
                    games,
                    history,
                    feature_store,
                    rows_meta,
                    X_rows,
                    y_rows,
                    home_wr,
                    away_wr,
                )
        else:
            _build_and_persist_features(
                games,
                history,
                feature_store,
                rows_meta,
                X_rows,
                y_rows,
                home_wr,
                away_wr,
            )
    except Exception:
        close = getattr(feature_store, "close", None)
        if close:
            close()
        raise

    matrix_path = ctx.artifacts_dir / "feature_matrix.npz"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        matrix_path,
        X=np.asarray(X_rows, dtype=float),
        y=np.asarray(y_rows, dtype=float),
        home_season_wr=np.asarray(home_wr, dtype=float),
        away_season_wr=np.asarray(away_wr, dtype=float),
    )
    meta_path = ctx.artifacts_dir / "feature_matrix_meta.json"
    meta_path.write_text(
        json.dumps(
            {
                "feature_version": FEATURE_VERSION,
                "n_labeled": len(y_rows),
                "n_feature_rows": feature_store.count(),
                "rows": rows_meta,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    ctx.feature_store = feature_store
    ctx.matrix_path = matrix_path
    logger.info(
        "stage=features labeled=%s feature_rows=%s matrix=%s store=%s",
        len(y_rows),
        feature_store.count(),
        matrix_path,
        ctx.store_kind,
    )


def _build_and_persist_features(
    games,
    history,
    feature_store,
    rows_meta,
    X_rows,
    y_rows,
    home_wr,
    away_wr,
) -> None:
    for g in sorted(games, key=lambda x: x.record.game_start_time):
        rec = g.record
        label = None if rec.home_win is None else (1 if rec.home_win else 0)
        row = build_feature_row(
            game_id=g.game_id,
            tip=rec.game_start_time,
            season=rec.season,
            home_team_id=g.home_team_id,
            away_team_id=g.away_team_id,
            history=history,
            label_home_win=label,
        )
        feature_store.upsert(row)
        if label is None:
            continue
        vec = feature_vector(row.payload)
        X_rows.append(vec)
        y_rows.append(float(label))
        home_wr.append(float(row.payload["home_season_wr"]))
        away_wr.append(float(row.payload["away_season_wr"]))
        rows_meta.append({"game_id": g.game_id, "label": label})


def stage_train(ctx: PipelineContext) -> None:
    matrix_path = ctx.matrix_path
    if matrix_path is None or not Path(matrix_path).exists():
        candidate = ctx.artifacts_dir / "feature_matrix.npz"
        if candidate.exists():
            matrix_path = candidate
            ctx.matrix_path = candidate
        else:
            raise PipelineError("train", "missing feature_matrix.npz; run features first")

    data = np.load(matrix_path)
    X = data["X"]
    y = data["y"]
    home_wr = data["home_season_wr"]
    away_wr = data["away_season_wr"]
    if len(y) < 3:
        raise PipelineError(
            "train",
            f"need at least 3 labeled games for temporal split; got {len(y)}",
        )

    dataset_version = ctx.batch_id or "local"
    result = run_train_select_publish(
        X=X,
        y=y,
        home_season_wr=home_wr,
        away_season_wr=away_wr,
        artifacts_dir=ctx.artifacts_dir,
        dataset_version=str(dataset_version),
        seed=ctx.settings.seed,
        feature_version=FEATURE_VERSION,
        evaluate_test=True,
    )
    ctx.pin_path = result.pin_path
    # Quality-gate miss is recorded, not an infra crash (FR-011).
    if result.ml005_pass is False:
        logger.warning(
            "stage=train status=quality_gate_miss ml005=false selected=%s",
            result.selected_family,
        )
    logger.info(
        "stage=train pin=%s model_version=%s ml005=%s",
        result.pin_path,
        result.model_version,
        result.ml005_pass,
    )


def _latest_batch(raw_root: Path) -> Path:
    root = Path(raw_root)
    if not root.exists():
        raise PipelineError("load", f"raw root missing: {root}")
    batches = sorted(
        [p for p in root.iterdir() if p.is_dir() and (p / "manifest.json").exists()],
        key=lambda p: p.name,
    )
    if not batches:
        raise PipelineError("load", f"no raw batches under {root}")
    return batches[-1]
