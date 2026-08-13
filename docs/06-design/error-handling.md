# Error handling design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

## Classes

| Class | Meaning | Behavior |
|---|---|---|
| Execution failure | Stage cannot complete | Non-zero exit; API 5xx/503 |
| Quality gate failure | e.g. ML-005 miss | May exit 0 with failed report; blocks MVP complete |
| Validation skip | Noisy row | Counted; continue |

## Provider HTTP (Q6)

Exponential backoff + jitter, max 5 attempts; honor `Retry-After`; then fail stage. Never log secrets.

## Validation (Q3)

Skip invalid → report; fail if zero teams or zero games for a required season after load.

## Prune (Q4)

Duplicates / noisy / too-old (outside 2–3 season window).

## PostgreSQL failures

| Path | Behavior |
|---|---|
| Pipeline migrate/ETL | Execution failure; log; non-zero |
| `/v1/predict` or `/v1/health` DB read | **503** `db_unavailable` (not generic 500) |
| `/v1/model` if metadata mirrored in DB and DB down | 503 `db_unavailable`; if metadata is file-only, file errors → `model_unavailable` |

## Model / artifact

Missing pin/artifact → **503** `model_unavailable`. **No silent baseline fallback.**

## API codes

See `api-design.md` — distinct `game_not_found` vs `features_not_found`.

## Pipeline stages

Log stage name + reason; operator may rerun `--from-stage` per ADR-005 (train from `feature_matrix.npz` after restart; features is same-process only). State file is written but **not** restored.
