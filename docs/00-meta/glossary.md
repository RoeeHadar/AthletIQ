# Glossary

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 0.11.0

| Term | Definition |
|---|---|
| AthletIQ | Product/project name |
| Game | A scheduled basketball contest (NBA or WNBA) with a unique `(league, provider_game_id)` / `game_id` |
| Matchup | Home/away pairing (product language). **Not** an MVP predict input. MVP optional resolver is `provider_game_id` → `game_id`. |
| Prediction time | Game start; features may use only info available by then |
| Temporal boundary / no leakage | Invariant: no post-`t` info in features, selection, or evaluation |
| Feature row key | `(game_id, feature_version)` |
| Feature version | Shared feature definition + preprocessing contract id |
| Dataset version | Id of curated/feature snapshot used to train |
| Model version | Published artifact id served by API pin |
| Train / validation / test | Temporal partitions; val→selection; test→final once |
| Baseline | Deterministic/reference predictor (not necessarily a fitted ML model) |
| Raw landing | Immutable provider JSON on filesystem |
| NBA Stats API | No-key live MVP provider at `api.server.nbaapi.com` (ADR-011 / CR-002); CI still uses fixtures |
| Quality gate failure | Eval acceptance miss (≠ execution failure) |
| Quality gate / attestation | Empirical ML acceptance (e.g. ML-005); not a flaky PR unit invariant |
| Execution failure | Pipeline hard failure / non-zero exit |
| Active history window | **CR-004:** 3 completed NBA seasons + overlapping WNBA, older pruned. **CR-005 live NBA:** no season cap (page everything `nba-stats` returns); CI fixtures stay small; WNBA fixture window is 2021–2025 completed + 2026 scheduled |
| Prune policy | Drop duplicates (natural key) and noisy (validation fail). **CR-005:** do **not** prune live NBA seasons for age. CI fixtures are not a historical dump |
| E-coin | Fake integer token in the CR-005 labeled simulation; not money |
| Stake / settle | Even-money simulation verbs (not odds/juice/moneyline/payout). Pipeline settles when a game is ingested as Finished |
| House wallet | System wallet that pays even-money wins; not a sportsbook bankroll product |
| Slate | Upcoming-game table at `GET /slate` |
| Board | In-progress game table at `GET /board` (not the gamecast; not live prediction features) |
| Board poll | Compose loop in the **etl** image that pulls **newest** `nba-stats` pages and upserts in-progress NBA games; browser polls AthletIQ only; design default interval **30s**; not a fourth Compose service |
| Feature windows | Team form last **5** and **10** games before tip (MVP) |
| Surrogate key | Internal BIGINT / BIGSERIAL id (`game_id`, …) per **ADR-010**; not UUID |
| Test level: unit | Pure-function / in-process tests (`test-strategy.md`) |
| Test level: integration | Cross-component tests (often ephemeral Postgres / API / Compose topology) |
| Test level: pipeline | Operator script/CLI end-to-end with fixtures |
| Test level: ci | GHA path + static workflow DAG/`needs` asserts (NFR-003/OPS-001); not `ci-meta` |
| Also (test plan) | Nested cases at a secondary level under one TEST suite — primary Level stays singular |
| Gate | Docs Status = Approved for phase entry |
| ADR | Architecture Decision Record |
| CR | Change Request |
| Selection pin | Batch-time JSON that names the served `model_version` / artifact / `feature_version`; API loads this only (ADR-003) — never a live baseline |
| Cold start | Team has fewer than `min_prior_games` (MVP = 5) completed prior games before tip; use season-to-date aggregates instead of sparse L5/L10. Player-agg features use zeros / empty-window analogue when box scores are missing. **CR-005:** live NBA boxes are loaded; WNBA/CI may still cold-start player_agg |
| League | `nba` or `wnba` on teams/games; routes the served pin (ADR-013) |
| Sport | `basketball` for both leagues this CR |
| Market P | Labeled implied `P(home_win)` from `odds_snapshots` (synthetic this CR; not a book) |
| Odds snapshot | Pre-tip implied home-win probability row; `source=synthetic` for CR-004 (ADR-012) |
| Per-league pin | Selection pin scoped to one `league` (ADR-013); API loads the pin matching `game.league` |
