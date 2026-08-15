# Implements: FR-011, CON-006, CON-001, OPS-002, ADR-005, CR-004
"""Stage ordering, resume window, and failure reporting."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

from athletiq.config import Settings
from athletiq.features.store import FeatureStore
from athletiq.load.store import CuratedStore
from athletiq.provider.base import ProviderClient

logger = logging.getLogger("athletiq.pipeline")

STAGE_ORDER: tuple[str, ...] = ("ingest", "load", "features", "train")
StoreKind = Literal["memory", "postgres"]


class PipelineError(RuntimeError):
    """Execution failure bound to a stage name (OPS-002)."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(message)


@dataclass
class PipelineContext:
    """Mutable run state shared across stages."""

    settings: Settings
    provider: ProviderClient
    raw_root: Path
    artifacts_dir: Path
    store_kind: StoreKind = "memory"
    seasons: list[int] | None = None
    season_depth: int = 3
    batch_id: str | None = None
    batch_dir: Path | None = None
    store: CuratedStore | None = None
    feature_store: FeatureStore | None = None
    matrix_path: Path | None = None
    pin_path: Path | None = None
    completed: list[str] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def state_path(self) -> Path:
        return self.artifacts_dir / "pipeline_state.json"

    def save_state(self) -> None:
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "completed": list(self.completed),
            "batch_id": self.batch_id,
            "batch_dir": str(self.batch_dir) if self.batch_dir else None,
            "matrix_path": str(self.matrix_path) if self.matrix_path else None,
            "pin_path": str(self.pin_path) if self.pin_path else None,
        }
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


StageFn = Callable[[PipelineContext], None]


def resolve_stages(
    *,
    from_stage: str | None = None,
    to_stage: str | None = None,
    only: list[str] | None = None,
) -> list[str]:
    """Select an inclusive stage window or an explicit list."""
    if only:
        unknown = [s for s in only if s not in STAGE_ORDER]
        if unknown:
            raise PipelineError("cli", f"unknown stage(s): {unknown}")
        # Preserve canonical order even if caller shuffled.
        return [s for s in STAGE_ORDER if s in only]

    start = STAGE_ORDER.index(from_stage) if from_stage else 0
    end = STAGE_ORDER.index(to_stage) if to_stage else len(STAGE_ORDER) - 1
    if from_stage and from_stage not in STAGE_ORDER:
        raise PipelineError("cli", f"unknown from-stage: {from_stage}")
    if to_stage and to_stage not in STAGE_ORDER:
        raise PipelineError("cli", f"unknown to-stage: {to_stage}")
    if start > end:
        raise PipelineError("cli", f"from-stage {from_stage} is after to-stage {to_stage}")
    return list(STAGE_ORDER[start : end + 1])


def run_pipeline(
    ctx: PipelineContext,
    stages: list[str],
    *,
    stage_fns: dict[str, StageFn] | None = None,
) -> PipelineContext:
    """Run selected stages; on failure log stage=… and raise PipelineError."""
    from athletiq.pipeline import stages as default_stages

    fns: dict[str, StageFn] = {
        "ingest": default_stages.stage_ingest,
        "load": default_stages.stage_load,
        "features": default_stages.stage_features,
        "train": default_stages.stage_train,
    }
    if stage_fns:
        fns.update(stage_fns)

    ctx.artifacts_dir.mkdir(parents=True, exist_ok=True)
    ctx.raw_root.mkdir(parents=True, exist_ok=True)

    if ctx.store_kind == "postgres":
        url = ctx.settings.database_url
        if not url:
            raise PipelineError("cli", "DATABASE_URL required for --store postgres")
        try:
            from athletiq.db.migrate import apply_migrations

            apply_migrations(url)
        except Exception as exc:  # noqa: BLE001 — bound for OPS-002
            logger.error("stage=load status=failed reason=migrations %s", exc)
            raise PipelineError("load", f"migrations failed: {exc}") from exc

    for name in stages:
        fn = fns.get(name)
        if fn is None:
            raise PipelineError("cli", f"no implementation for stage={name}")
        logger.info("stage=%s status=start", name)
        try:
            fn(ctx)
        except PipelineError:
            raise
        except Exception as exc:  # noqa: BLE001 — bound to stage for OPS-002
            logger.error("stage=%s status=failed reason=%s", name, exc)
            raise PipelineError(name, str(exc)) from exc
        if name not in ctx.completed:
            ctx.completed.append(name)
        ctx.save_state()
        logger.info("stage=%s status=ok", name)
    return ctx
