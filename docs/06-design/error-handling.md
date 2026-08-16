# Error handling design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.1.0

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

Duplicates (natural key) and noisy (validation fail). **Live NBA:** do **not** age-prune (ADR-017 / DR-001). **CI fixtures / WNBA:** drop seasons outside authored files.

## Ledger / settle (CR-005)

| Case | Behavior |
|---|---|
| Unknown `user` | API 404 `user_not_found`; no cookie fallback |
| Insufficient unlocked balance | API 400 `insufficient_balance`; no partial lock |
| Stake after tip / scores present | API 400 `stake_window_closed` |
| Second open stake without replace | API 409 `duplicate_open_stake` |
| Pipeline settle on Finished | Idempotent: second run does not double-credit (FR-023) |
| `/slate` | Display only — does not settle |

## PostgreSQL failures

| Path | Behavior |
|---|---|
| Pipeline migrate/ETL | Execution failure; log; non-zero |
| `/v1/predict`, `/v1/health`, slate/board/ledger reads | **503** `db_unavailable` (not generic 500) |
| `/v1/model` if metadata mirrored in DB and DB down | 503 `db_unavailable`; if metadata is file-only, file errors → `model_unavailable` |

## Model / artifact

Missing pin/artifact → **503** `model_unavailable`. **No silent baseline fallback.**

## API codes

See `api-design.md` — distinct `game_not_found` vs `features_not_found`.

## Pipeline stages

Log stage name + reason; operator may rerun `--from-stage` per ADR-005 (train from `feature_matrix.npz` after restart; features is same-process only). State file is written but **not** restored.
