# ML design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

> Design layer. SRS v1.3 + architecture. Artifacts: joblib + JSON (ADR-004). Grill-Me design Q1–Q6.

## Prediction task

Home-win classification: label `home_win ∈ {0,1}`; model outputs `P(home_win)`. Designated team = home (ML-002).

## Temporal splits (Q1)

| Partition | Fraction | Use |
|---|---|---|
| Train | ~70% oldest | Fit LR / XGBoost |
| Validation | ~15% middle | Model selection (ADR-003) |
| Test | ~15% newest | Final metrics once (ML-005) |

No shuffle across time. Exact counts in lineage (`dataset_version`). Splits are computed **inside each league**. Val/test stay newest ~15%/15% of that league. **CR-005** live NBA is uncapped, so train is whatever history remains after that split — do not treat a third season as a cap.

## Active history window & pruning (Q4)

| Rule | Meaning |
|---|---|
| **Too old (CI fixture / WNBA)** | Outside authored fixture seasons → do not ingest |
| **Live NBA** | **No season cap** (ADR-017). Do not age-prune. |
| **Duplicates** | Natural-key upsert / drop |
| **Noisy** | Validation fail → skip + report (Q3) |

Raw writes immutable (ADR-006); prune deletes obsolete batches/rows.

## Baselines (deterministic)

Naive = always home; domain-informed = better pre-game season WR (tie → home). Never served.

## Features — team + aggregated player (CR-004)

Shared builder; key `(game_id, feature_version)`. **`feature_version` = `team_l5_l10_player_agg_v1`.**

**Cold start (team windows):** if a team has fewer than **`min_prior_games = 5`** completed games before tip in-window, use **season-to-date** aggregates for that window’s team features.

**Player aggregates:** for each side, take the team’s players with completed prior games before tip; rank by **minutes in those prior games**; take top 5; mean of their **L5 points** and **L5 minutes**. If fewer than 5 or no box scores, fill **0.0** and do not read post-tip lines. **CR-005:** live NBA boxes are loaded (FR-027); WNBA/CI may still zero-fill. No embeddings. Inference stays `game_id`-keyed. **Do not** change `feature_version` this CR.

| Feature family | Windows |
|---|---|
| Win rate | L5, L10 (or season-to-date if cold start) |
| Mean point differential | L5, L10 |
| Mean points scored / allowed | L5, L10 |
| Season win rate to date | season |
| Top-5-by-minutes L5 points (home/away) | L5 player, then mean |
| Top-5-by-minutes L5 minutes (home/away) | L5 player, then mean |

Train/select **per league** (ADR-013). Do not pool.

## Models

LR + XGBoost **per league**; select on that league’s validation log loss (tie → LR); joblib + JSON metadata (ML-009). Pin map in `selected_pin.json` (`pins` keyed by league; legacy flat pin = nba).

## Metrics

Log loss primary; accuracy secondary; ML-005 on **test**.

## Monitoring (MVP)

| Signal | Approach |
|---|---|
| Pipeline / eval | Validation report + eval report artifacts; quality-gate vs execution-failure distinction |
| API | `/v1/health` + structured logs (OPS-002); no metrics backend required (NFR-004) |
| Model drift / data drift dashboards | **Out of MVP** (PRD non-goal: no production ML ops) — `[FUTURE CONSIDERATION]` |

## Retraining strategy

| Topic | Decision |
|---|---|
| Trigger | **Manual / operator-invoked** via pipeline (or stage from features→publish) |
| **CR-005** | **One-shot** retrain + reselect of NBA and WNBA pins on the new history (ML-012). Same hyperparameters. Test once. CI 48-game pin unchanged. |
| Schedule / automated retrain | **Out** — `[FUTURE CONSIDERATION]` |
| Hot-swap without restart | Not required; API loads pin at startup or documented reload |

## Post-MVP (remaining)

NumPy NN; score/spread; live WNBA HTTP; live odds; scheduled retrain; drift monitoring — document only.

## Open (non-blocking)

- Exact XGBoost hyperparameters → defaults in impl; record in `training_config`
