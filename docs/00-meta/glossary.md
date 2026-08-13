# Glossary

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 0.9.0

| Term | Definition |
|---|---|
| AthletIQ | Product/project name |
| Game | An NBA scheduled contest with a unique provider/`game_id` |
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
| Quality gate failure | Eval acceptance miss (≠ execution failure) |
| Quality gate / attestation | Empirical ML acceptance (e.g. ML-005); not a flaky PR unit invariant |
| Execution failure | Pipeline hard failure / non-zero exit |
| Active history window | Most recent **2 Must / ≤3 Should** completed NBA seasons; older data pruned as “too old” |
| Prune policy | Drop duplicates (natural key), noisy (validation fail), and too-old (outside active window) |
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
| Cold start | Team has fewer than `min_prior_games` (MVP = 5) completed prior games before tip; use season-to-date aggregates instead of sparse L5/L10 |
