# AthletIQ model card (methodology & limitations)

<!-- Implements: FR-010 -->

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.0

> **FR-010** disclosure for evaluation and API consumers. Design source: `ml-design.md`.  
> Runtime summary: `GET /v1/model` (`limitations_ref` → this document).

## Intended use

Portfolio / demo **pre-game home-win** prediction for NBA contests keyed by existing `game_id`.  
Output: binary `home_win_pred` and `P(home_win)`. **Not** a betting product; **not** a claim of accurate game forecasting.

## Temporal boundary (no leakage)

Features, training labels for prior games, model selection, and evaluation use only information available **before** the predicted game’s tip (`game_start_time`). Post-tip information must not influence features, selection, or evaluation for that game.

## Features

- **Version:** `team_l5_l10_v1` (MVP).
- **Team-level only:** L5/L10 win rate, point differential, points for/against; season win rate to date.
- **Cold start:** if fewer than `min_prior_games = 5` completed prior games → season-to-date aggregates for that side.
- **No player-level features** in MVP.
- Train and serve share the same feature definitions / preprocessing contract (ML-008).

## Data window

Active history: **2 Must / ≤3 Should** most recent **completed** NBA seasons (DR-001). Seasons outside the window are too old (do not ingest; prune if present).

## Splits

Temporal split by `game_start_time`, **no random shuffle**:

| Partition | ~Fraction | Role |
|---|---|---|
| Train | 70% oldest | Fit logistic regression + XGBoost |
| Validation | 15% middle | **Model selection only** |
| Test | 15% newest | Final report **once** (ML-005) |

## Baselines (never served)

| Baseline | Rule |
|---|---|
| Naive | Always predict home win |
| Domain-informed | Higher pre-game season win rate wins; **tie → home** |

Baselines are reference predictors for evaluation. **They are never loaded as the served pin** and never returned by `/v1/predict`.

## Candidates & selection

- Candidates: **logistic regression** and **XGBoost** (defaults recorded in artifact `training_config`).
- **Selection metric:** validation **log loss** (lower is better).
- **Tie:** prefer logistic regression (ADR-003).
- Test partition is **not** used for selection.

## Metrics & quality gate (ML-005)

- **Primary:** log loss on the held-out **test** set (after selection).
- **Secondary:** accuracy.
- Quality gate: selected model should beat the **domain-informed** baseline on **test log loss**. A miss is recorded in artifacts / logs; it is not an infrastructure crash.

## Artifacts & lineage

Publish: **joblib** model + **JSON** metadata + **selection pin** (`model_version`, `feature_version`, `dataset_version`, `code_commit`, `training_config`, metrics, selection rule). API serves only the pinned artifact (ADR-004 / ADR-003).

## API disclosure

- `GET /v1/model` — versions, metrics snapshot, methodology summary, limitations text, `model_card_ref`.
- `GET /v1/predict` — includes `limitations_ref` pointing operators to `/v1/model` / this card.
- No application auth (ADR-009); demo-grade local/Compose bind (NFR-002); **no hard latency/availability SLO** (NFR-004).

## Known limitations

1. Team-level features only; ignores injuries, rest, travel, coaching, lineup, market odds.
2. Cold-start games use coarse season-to-date proxies.
3. Small / fixture datasets can pass local demos without reflecting production NBA signal.
4. Provider free-tier coverage and schema drift can affect ingest completeness.
5. Manual retrain only — no drift dashboards or automated retrain in MVP.
6. Honest evaluation ≠ guaranteed predictive skill on future seasons.

## Non-claims

AthletIQ does **not** claim to “accurately predict NBA games.” It evaluates whether historical pre-tip features provide measurable signal under this methodology and surfaces limitations with predictions.
