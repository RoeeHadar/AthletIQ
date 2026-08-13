# ML design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

> Design layer. SRS v1.3 + architecture. Artifacts: joblib + JSON (ADR-004). Grill-Me design Q1–Q6.

## Prediction task

Home-win classification: label `home_win ∈ {0,1}`; model outputs `P(home_win)`. Designated team = home (ML-002).

## Temporal splits (Q1)

| Partition | Fraction | Use |
|---|---|---|
| Train | ~70% oldest | Fit LR / XGBoost |
| Validation | ~15% middle | Model selection (ADR-003) |
| Test | ~15% newest | Final metrics once (ML-005) |

No shuffle across time. Exact counts in lineage (`dataset_version`). Third season (Should) extends early train; val/test stay newest ~15%/15%.

## Active history window & pruning (Q4)

| Rule | Meaning |
|---|---|
| **Too old** | Outside **2 Must / ≤3 Should** completed seasons (DR-001) → do not ingest; prune if present |
| **Duplicates** | Natural-key upsert / drop |
| **Noisy** | Validation fail → skip + report (Q3) |

Raw writes immutable (ADR-006); prune deletes obsolete batches/rows.

## Baselines (deterministic)

Naive = always home; domain-informed = better pre-game season WR (tie → home). Never served.

## Features (Q2) — team-level MVP

Shared builder; key `(game_id, feature_version)`.

**Cold start (decided):** if a team has fewer than **`min_prior_games = 5`** completed games before tip in-window, use **season-to-date** aggregates for that window’s features instead of a sparse L5/L10. This value is fixed for MVP; sensitivity analysis is optional post-run commentary in the model card — not an open parameter.

| Feature family | Windows |
|---|---|
| Win rate | L5, L10 (or season-to-date if cold start) |
| Mean point differential | L5, L10 |
| Mean points scored / allowed | L5, L10 |
| Season win rate to date | season |

No player-level features in MVP.

## Models

LR + XGBoost; select on validation log loss (tie → LR); joblib + JSON metadata (ML-009).

## Metrics

Log loss primary; accuracy secondary; ML-005 on **test**.

## Monitoring (MVP)

| Signal | Approach |
|---|---|
| Pipeline / eval | Validation report + eval report artifacts; quality-gate vs execution-failure distinction |
| API | `/v1/health` + structured logs (OPS-002); no metrics backend required (NFR-004) |
| Model drift / data drift dashboards | **Out of MVP** (PRD non-goal: no production ML ops) — `[FUTURE CONSIDERATION]` |

## Retraining strategy (MVP)

| Topic | Decision |
|---|---|
| Trigger | **Manual / operator-invoked** via `scripts/run_pipeline.sh` (or stage from features→publish) |
| Schedule / automated retrain | **Out of MVP** — `[FUTURE CONSIDERATION]` |
| Hot-swap without restart | Not required; API loads pin at startup or documented reload |
| Alignment | Matches “no automated retraining” PRD non-goal |

## Post-MVP

NumPy NN; score/spread; player features; scheduled retrain; drift monitoring — document only.

## Open (non-blocking)

- Exact XGBoost hyperparameters → defaults in impl; record in `training_config`
