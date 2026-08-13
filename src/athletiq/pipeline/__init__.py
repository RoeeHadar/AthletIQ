# Implements: FR-011, CON-006, CON-001, OPS-002, ADR-005
"""Python pipeline orchestrator (thin shell → this package)."""

from athletiq.pipeline.orchestrator import (
    STAGE_ORDER,
    PipelineContext,
    PipelineError,
    run_pipeline,
)

__all__ = [
    "STAGE_ORDER",
    "PipelineContext",
    "PipelineError",
    "run_pipeline",
]
