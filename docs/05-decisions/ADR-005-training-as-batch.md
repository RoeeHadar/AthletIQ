# ADR-005: Training as pipeline batch via Python orchestrator

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.2.0

Decision status: Accepted

## Context

MVP needs train/val/test without a long-running trainer. Owner review: shell script should be a thin entrypoint; Python owns orchestration.

## Decision

- Feature build + train/validate + test-eval + publish run as **batch stages** in the etl image family.  
- `scripts/run_pipeline.sh` (host) or Compose `python -m athletiq.pipeline --store postgres` only checks env and invokes a **Python CLI orchestrator** (e.g. `python -m athletiq.pipeline`).  
- Stage **selection** (`--from-stage`) is supported. **Process restart** is limited: `--from-stage train` may resume if `feature_matrix.npz` exists; `--from-stage load` may rediscover the latest raw batch; `--from-stage features` requires an in-process curated store (same process after load). `PipelineContext.save_state()` writes a state file that is **not** restored on restart.

## Alternatives considered

- Shell script calls every component directly — rejected (logic in bash)  
- Always-on training microservice — unnecessary  
- Notebook-only — weak NFR-001

## Consequences

- Clearer testing of pipeline modules in Python.  
- CI does not equal full live pipeline (see system architecture).

## References

- Related requirements: FR-005–FR-008, FR-011, CON-006, OPS-002  
- Related architecture docs: `system-architecture.md`  
- Owner architecture review 2026-08-12
