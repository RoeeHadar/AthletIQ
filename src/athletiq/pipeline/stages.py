# Implements: FR-011, FR-021, FR-023, CON-001, OPS-002, ADR-005, ML-010, ADR-013, ADR-015, CR-004, CR-005
"""Concrete pipeline stage implementations (offline-capable)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

from athletiq.features.builder import (
    FEATURE_VERSION,
    PlayerGameHistory,
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
    from athletiq.ledger.settle import settle_finished_on_store

    settled = settle_finished_on_store(store)
    logger.info(
        "stage=load batch=%s teams=%s games=%s report=%s store=%s settled=%s",
        batch_dir.name,
        report.teams_loaded,
        report.games_loaded,
        report_path,
        ctx.store_kind,
        settled,
    )


def stage_features(ctx: PipelineContext) -> None:
    store = ctx.store
    if store is None:
        raise PipelineError("features", "no curated store; run load first")

    history: list[TeamGameHistory] = []
    games = store.iter_games()
    tip_by_game = {g.game_id: g.record.game_start_time for g in games}
    for g in games:
        rec = g.record
        if rec.status != "Finished" or rec.home_score is None or rec.away_score is None:
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

    finished_ids = {g.game_id for g in games if g.record.status == "Finished"}
    player_history: list[PlayerGameHistory] = []
    iter_pgs = getattr(store, "iter_player_game_stats", None)
    if iter_pgs is not None:
        for stat in iter_pgs():
            if int(stat["game_id"]) not in finished_ids:
                continue
            tip = stat.get("game_start_time") or tip_by_game.get(stat["game_id"])
            if tip is None:
                continue
            minutes = float(stat["minutes"] or 0.0)
            points = float(stat["points"] or 0.0)
            player_history.append(
                PlayerGameHistory(
                    player_id=int(stat["player_id"]),
                    team_id=int(stat["team_id"]),
                    game_start_time=tip,
                    minutes=minutes,
                    points=points,
                )
            )

    feature_store = _open_feature_store(ctx)
    rows_meta: list[dict] = []
    X_rows: list[list[float]] = []
    y_rows: list[float] = []
    home_wr: list[float] = []
    away_wr: list[float] = []
    league_rows: list[str] = []

    try:
        txn = getattr(feature_store, "transaction", None)
        if txn is not None:
            with txn():
                _build_and_persist_features(
                    games,
                    history,
                    player_history,
                    feature_store,
                    rows_meta,
                    X_rows,
                    y_rows,
                    home_wr,
                    away_wr,
                    league_rows,
                )
        else:
            _build_and_persist_features(
                games,
                history,
                player_history,
                feature_store,
                rows_meta,
                X_rows,
                y_rows,
                home_wr,
                away_wr,
                league_rows,
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
        league=np.asarray(league_rows),
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
    player_history,
    feature_store,
    rows_meta,
    X_rows,
    y_rows,
    home_wr,
    away_wr,
    league_rows,
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
            player_history=player_history,
        )
        feature_store.upsert(row)
        if label is None:
            continue
        vec = feature_vector(row.payload)
        X_rows.append(vec)
        y_rows.append(float(label))
        home_wr.append(float(row.payload["home_season_wr"]))
        away_wr.append(float(row.payload["away_season_wr"]))
        league_rows.append(getattr(rec, "league", None) or "nba")
        rows_meta.append({"game_id": g.game_id, "label": label, "league": league_rows[-1]})


def stage_train(ctx: PipelineContext) -> None:
    matrix_path = ctx.matrix_path
    if matrix_path is None or not Path(matrix_path).exists():
        candidate = ctx.artifacts_dir / "feature_matrix.npz"
        if candidate.exists():
            matrix_path = candidate
            ctx.matrix_path = candidate
        else:
            raise PipelineError("train", "missing feature_matrix.npz; run features first")

    data = np.load(matrix_path, allow_pickle=True)
    X = data["X"]
    y = data["y"]
    home_wr = data["home_season_wr"]
    away_wr = data["away_season_wr"]
    if "league" in data.files:
        leagues = np.asarray(data["league"]).astype(str)
    else:
        leagues = np.array(["nba"] * len(y), dtype=str)

    dataset_version = ctx.batch_id or "local"
    pins: dict[str, dict] = {}
    unique_leagues = sorted(set(leagues.tolist()))
    for league in unique_leagues:
        mask = leagues == league
        n = int(mask.sum())
        if n < 3:
            logger.warning("stage=train skip league=%s labeled=%s", league, n)
            continue
        result = run_train_select_publish(
            X=X[mask],
            y=y[mask],
            home_season_wr=home_wr[mask],
            away_season_wr=away_wr[mask],
            artifacts_dir=ctx.artifacts_dir,
            dataset_version=f"{dataset_version}:{league}",
            seed=ctx.settings.seed,
            feature_version=FEATURE_VERSION,
            model_version=None,
            evaluate_test=True,
            pin_name=f"selected_pin_{league}.json",
            model_version_prefix=f"{league}-",
        )
        pin_obj = json.loads(Path(result.pin_path).read_text(encoding="utf-8"))
        pins[league] = pin_obj
        if result.ml005_pass is False:
            logger.warning(
                "stage=train status=quality_gate_miss league=%s ml005=false selected=%s",
                league,
                result.selected_family,
            )
        logger.info(
            "stage=train league=%s pin=%s model_version=%s ml005=%s",
            league,
            result.pin_path,
            result.model_version,
            result.ml005_pass,
        )

    if not pins:
        raise PipelineError("train", "no league had at least 3 labeled games")

    combined = ctx.artifacts_dir / "selected_pin.json"
    combined.write_text(
        json.dumps({"schema": "athletiq.pins.v2", "default_league": "nba", "pins": pins}, indent=2),
        encoding="utf-8",
    )
    ctx.pin_path = combined
    logger.info("stage=train pin=%s leagues=%s", combined, sorted(pins))


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
