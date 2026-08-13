# Data architecture

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

> Zones and lineage. System/deployment: `system-architecture.md`.

## Lifecycle

```text
API-Sports → Adapter → Raw JSON (immutable FS) → Validate
  → Curated PostgreSQL (idempotent upserts)
  → Feature tables (single feature-builder implementation)
  → Train / Validation / Test partitions
  → Select on validation → Test once → Publish artifact + lineage
  → API reads (game_id, feature_version) + pinned model
```

**Replay capability:** A historical transform must be reproducible from persisted raw data **without** another provider API call (ADR-006).

## Zones

| Zone | Medium | Rules |
|---|---|---|
| Raw | Filesystem volume | Immutable after write; new fetch = new batch path; store retrieval metadata in design |
| Curated | PostgreSQL | Natural keys; idempotent reload (DR-003). **MVP load:** teams, games, `team_game_stats`. `players` / `player_game_stats` are **reserved** (CR-001) — present in schema, not written by the pipeline. |
| Features | PostgreSQL (+ optional files) | Key `(game_id, feature_version)`; built by **one** shared feature module; `payload` JSONB envelope `{values, label_home_win, used_cold_start_*}` |
| Artifacts | Local volume | Models + lineage JSON; selection pin |

## Validation boundary

```text
Raw → Validate → valid records → transform/load
                 → invalid → validation report
                 → stop vs skip = `docs/06-design/error-handling.md` (skip+count; fail if zero teams/games for a required season)
```

## Versioning / lineage chain

```text
raw_batch_id → dataset_version → feature_version → training_run
  → model_version (+ code_commit, training_config) → API pin
```

## Idempotency / rerun semantics

Running the same pipeline twice against the same raw dataset must not create duplicate games, team statistics, or feature records for the same logical keys.

## Related

ADR-001, ADR-002, ADR-003, ADR-004, ADR-006, ADR-008, ADR-010; **CR-001**.
