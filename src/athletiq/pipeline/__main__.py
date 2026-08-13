# Implements: FR-011, CON-006, CON-001, OPS-002, ADR-005
"""CLI entry: python -m athletiq.pipeline"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from athletiq.config import load_settings
from athletiq.logging import configure_logging
from athletiq.pipeline.orchestrator import (
    PipelineContext,
    PipelineError,
    resolve_stages,
    run_pipeline,
)
from athletiq.provider.api_sports import ApiSportsProvider
from athletiq.provider.fixture import FixtureProvider
from athletiq.provider.nba_stats import NbaStatsApiProvider


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="athletiq.pipeline",
        description="AthletIQ batch pipeline (ingest → load → features → train)",
    )
    p.add_argument(
        "--provider",
        choices=("fixture", "nba-stats", "api-sports"),
        default="fixture",
        help="Data source (default: fixture / offline; live: nba-stats, no key)",
    )
    p.add_argument(
        "--fixtures-dir",
        type=Path,
        default=None,
        help="Fixture JSON directory (fixture provider)",
    )
    p.add_argument("--from-stage", choices=("ingest", "load", "features", "train"))
    p.add_argument("--to-stage", choices=("ingest", "load", "features", "train"))
    p.add_argument(
        "--only",
        nargs="+",
        choices=("ingest", "load", "features", "train"),
        help="Run only these stages (canonical order)",
    )
    p.add_argument("--batch-id", default=None)
    p.add_argument(
        "--seasons",
        nargs="+",
        type=int,
        default=None,
        help="Override active seasons (else season_depth window)",
    )
    p.add_argument("--season-depth", type=int, default=2)
    p.add_argument("--raw-path", type=Path, default=None)
    p.add_argument("--artifacts-path", type=Path, default=None)
    p.add_argument(
        "--store",
        choices=("memory", "postgres"),
        default="memory",
        help="Curated/feature persistence (default: memory). DATABASE_URL is connection only.",
    )
    return p


def default_fixtures_dir() -> Path:
    """Locate recorded fixtures whether running from a checkout or an installed image.

    `__file__` is repo-relative only for an editable/src layout. The Compose ETL
    image installs the wheel into site-packages and copies fixtures to
    `/app/tests/fixtures/provider` (WORKDIR `/app`).
    """
    candidates = (
        Path.cwd() / "tests" / "fixtures" / "provider",
        Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "provider",
    )
    for path in candidates:
        if (path / "teams.json").is_file():
            return path
    return candidates[0]


def _provider(args: argparse.Namespace, api_key: str | None):
    if args.provider == "fixture":
        fixtures = args.fixtures_dir if args.fixtures_dir is not None else default_fixtures_dir()
        return FixtureProvider(fixtures)
    if args.provider == "nba-stats":
        return NbaStatsApiProvider(seasons=args.seasons, season_depth=args.season_depth)
    if not api_key:
        raise PipelineError("cli", "API_SPORTS_KEY required for --provider api-sports")
    return ApiSportsProvider(api_key=api_key)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level, secrets=settings.secret_values())

    try:
        if args.store == "postgres" and not settings.database_url:
            raise PipelineError("cli", "DATABASE_URL required for --store postgres")
        provider = _provider(args, settings.api_sports_key)
        stages = resolve_stages(
            from_stage=args.from_stage,
            to_stage=args.to_stage,
            only=args.only,
        )
        ctx = PipelineContext(
            settings=settings,
            provider=provider,
            raw_root=args.raw_path or settings.raw_path,
            artifacts_dir=args.artifacts_path or settings.artifacts_path,
            store_kind=args.store,
            seasons=args.seasons,
            season_depth=args.season_depth,
            batch_id=args.batch_id,
        )
        run_pipeline(ctx, stages)
        return 0
    except PipelineError as exc:
        # Stage already logged in run_pipeline for stage failures.
        if exc.stage == "cli":
            print(f"pipeline error: {exc}", file=sys.stderr)
        else:
            print(f"pipeline failed stage={exc.stage}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
