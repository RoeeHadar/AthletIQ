# Gate 6 code review — CR-004 (IMP-013–018)

Status: Complete  
Date: 2026-08-16  
Reviewer role: Gate 6 code reviewer (lead-engineer bar)  
Scope: AthletIQ CR-004 implementation vs Accepted CR, IMP-013–018, TEST-015–019  
No Grill-Me. No primary-doc edits. No implementation fixes.

## Verdict

**APPROVE**

The slice matches Accepted CR-004. Must requirements for IMP-013–018 are implemented. TEST-015–019 exist and cover the plan’s material steps (player leakage, pin routing, no sportsbook chrome). Remaining items are nits, defensive gaps that do not fire on the fixture/demo pin map, or already-documented limitations (fixture `xgboost-v1` extremes; live player cold-start zeros).

Code-review DoD for IMP-013–018 is this verdict. This file does not tick plan checkboxes.

## SHA range

| Ref | SHA | Note |
|---|---|---|
| Base (Close MVP, pre-CR-004) | `ec2156b980a8ce2a3601c55191626c7bde3d3510` | Exclusive start: `ec2156b` |
| Implementation | `491c5c0` | Land CR-004 |
| HEAD (this review) | `54babff95fbf1c876a7b8ef591da5e145c996c1f` | CI-evidence docs; does not reopen DoD |
| Remote CI | [run 31913410157](https://github.com/RoeeHadar/AthletIQ/actions/runs/31913410157) | Green on `491c5c0` (NFR-003 fixture/offline) |

Range reviewed: **`ec2156b` … `HEAD` (`54babff`)**.

## Gates (this slice)

| Gate | Artifacts | Status |
|---|---|---|
| 0–5 | Charter/PRD/SRS/architecture/ADRs/design/IMP plan | Approved (pre-code; see `2026-08-15-cr004-gate6-entry.md`) |
| 7 docs | Test strategy/plan TEST-015–019 | Approved before code (§22) |
| 6 | IMP-013–018 at `491c5c0` | **APPROVE** (this review) |

## Per-IMP

| IMP | Evidence | Result |
|---|---|---|
| **013** schema | `database/schema.sql` + `002_cr004_league_players_odds.sql`: `sport`/`league`, composite `(league, provider_*_id)`, `odds_snapshots`, indexes. Compose mounts 001+002. `migrations_dir()` probes cwd `/app/database/migrations`, env, then checkout — not wheel-path-only. | Pass |
| **014** ingest/load | Fixture NBA 2022–2024 + overlapping WNBA; `players.json` / `player_game_stats.json` / `odds_snapshots.json`. Protocol optional fetches; `nba-stats` returns `[]` (no live WNBA HTTP, no live odds). Default `--season-depth 3`. Load grain `(league, provider_*)`. | Pass |
| **015** features | `FEATURE_VERSION = team_l5_l10_player_agg_v1`; four `*_top5_l5_*` keys; `_player_agg` uses `game_start_time < tip`. | Pass |
| **016** pins | `stage_train` splits by `league`, publishes `nba-*` / `wnba-*`, writes `selected_pin.json` v2 `pins` map; legacy flat pin = nba. | Pass |
| **017** API | Predict routes on `game.league`; `market_p_home_win` / `market_source=synthetic` from curated snapshot (no book HTTP); `/v1/model?league=`; FR-020 names from `teams` join, nullable, not invented. OpenAPI matches. | Pass |
| **018** UI | `GET /` broadcast gamecast: producer bar, Home/Away split, Game ID + TAKE, labeled synthetic Market P, methodology/limitations chyrons. No stake/payout/wager/moneyline. `Cache-Control: no-store` on `/` and `/static` (allowed). | Pass |

`# Implements` present on listed Python/SQL/OpenAPI modules. `api/static/` has no Implements comment (HTML/JS); not a Must miss.

## TEST-015–019 mapping

| ID | Plan steps | Where | Coverage |
|---|---|---|---|
| TEST-015 | 002 + `games.league` / `odds_snapshots`; depth-3 NBA 2022–2024 + WNBA; league distinguish; no live HTTP | `test_cr004.py`, `test_schema.py`, CI `ci.yml` | **Present.** Live migrate in CI (`TEST_DATABASE_URL`). Ingest test uses seasons 2023–2024 rather than depth 3; `games_2022.json` + `active_season_years(depth=3)` still asserted. |
| TEST-016 | Idempotent `(game_id, player_id)`; player keys; post-tip line ignored | `test_cr004.py`, `test_features.py` (`test_player_aggregates_ignore_post_tip_lines`) | **Present.** Postgres player upsert not extra-tested in `test_postgres_stores.py` (unit grain holds; SQL `ON CONFLICT`). |
| TEST-017 | Odds load/idempotent; predict synthetic in [0,1]; missing → null; no book HTTP | `test_cr004.py` `test_synthetic_odds_on_predict` | **Present.** Second-load odds count not separately asserted (dict / `ON CONFLICT` grain). |
| TEST-018 | Both pins; NBA→nba; WNBA→wnba; drop wnba → 503 | `test_cr004.py` `test_per_league_pin_routing`; pipeline happy-path writes v2 | **Present.** Routing is unit-tested with published pins, not a full fixture-train of both leagues (pipeline loop is real; WNBA fixtures are large enough for `n >= 3`). |
| TEST-019 | GET / HTML; league/split/Market P; no wager/stake/payout/moneyline | `test_comp_a_ui_has_league_and_market_p_not_a_book` | **Present.** Does not string-assert “no score/clock/quarter”; those strings are absent from the shipped UI. |

## Findings

### Medium

1. **Asymmetric pin fallback (ADR-013 edge).** `AppState.require_model` falls back to `_loaded` when `league == "nba"` and the `nba` map entry is missing. `load_pin` sets `_loaded` to the first remaining v2 pin if the default league failed to load. A **degraded** v2 map with only `wnba` loaded would serve the WNBA artifact for NBA `game_id`s (and `/v1/health` would look healthy). The **inverse** (drop WNBA) correctly 503s and is TEST-018. Fixture `stage_train` writes both pins when both leagues have enough labeled games, so this does not fire on the CR-004 demo path. Not a Must hole on the shipped pin map; do not treat as pooled-classifier in production of this slice. Follow-up: fall back to `_loaded` only for legacy flat pins.

### Low (nits)

2. **`PostgresGameRepo.resolve_provider_game_id`** ignores `league` after uniqueness moved to `(league, provider_game_id)`. Fixture NBA ids (`901+`) and WNBA ids (`3001+`) do not collide; UI is `game_id`-keyed.
3. **Market P lookup** does not filter `captured_at < game_start_time`. ADR-012 asks for pre-tip snapshots. Fixture odds are one hour before tip; missing snapshots stay null. Live book is out of this CR.
4. **TEST-004/015** still ingest `[2023, 2024]` in the shared load test; depth-3 is covered by the season helper + `games_2022.json` presence, not a full ingest of 2022 in that test.
5. **`api/static/`** (IMP-018) has no `# Implements` banner; Python/SQL/OpenAPI modules listed on IMP-013–017 do.
6. **TEST-019** does not read `app.css` or assert FR-015 “no score/clock/quarter”; the HTML/JS/CSS have no scorebug chrome.

No High findings. No secrets in source. CI does not set `API_SPORTS_KEY` or call live providers. Demo Cache-Control `no-store` is accepted.

## Drift (§13a) — this slice

| Layer | DB | API | ML |
|---|---|---|---|
| Design | `sport`/`league`; players loaded; `odds_snapshots` | league + Market P + team identity; no auth | `team_l5_l10_player_agg_v1`; per-league pins |
| Contract | `schema.sql` matches 001+002 end state | `openapi.yaml` has FR-018/019/020 fields | FEATURE_VERSION + v2 pin schema in code |
| Implementation | migrate 002 + postgres upserts | `state.py` / `api_repos.py` / static gamecast | `builder.py` + `stages.stage_train` |

No design-vs-contract-vs-code contradiction that would ship wrong labels, leak post-tip box scores, or add book chrome.

## Locks honored (not demanded)

- No betting book (CON-009 / ADR-012).
- CI fixture-only (NFR-003).
- No live WNBA HTTP; nba-stats stays NBA games/teams.
- No Kafka/Redis/K8s/GCP.
- ADR-009: no application auth.
- No retune of live LR vs test log loss 0.623.
- Fixture `xgboost-v1` not mixed with live `logistic_regression-v1`.

## Out of scope

- CR-005 and any later change request.
- Live WNBA HTTP; named live odds adapter; betting product.
- Comp B/C, film-room, pooled NBA+WNBA classifier.
- NFR-001 clean-clone attest outside this tree; ticking IMP/TEST plan checkboxes.
- Retuning fixture XGBoost leaf extremes or live LR `max_iter`.
- Application auth, GCP, Kafka, Redis, Kubernetes.

## Owning skills if follow-up

- Pin fallback (finding 1): **fixed after this review** — v2 maps no longer fall back to `_loaded` for NBA; TEST-018 extended. Provider-id resolver / pre-tip Market P filter remain nits.
