# Post-IMP integration invariants

## Must never miss

- **Store selection:** explicit `--store` / config wins. Unit/offline tests default **in-memory**. `DATABASE_URL` supplies **connection only** — its presence must **not** silently switch pytest or unit tests onto Postgres.
- **Demo vs CLI defaults:** `./scripts/run_pipeline.sh` explicitly passes `--store postgres` for Compose/demo e2e; `python -m athletiq.pipeline` defaults `--store memory`; API/ASGI uses `ATHLETIQ_STORE=postgres|memory` (Compose sets `postgres`).
- **Canonical Compose pipeline:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture` — Compose demo **must** pass `--store postgres`; the etl service does **not** read `ATHLETIQ_STORE`. Default fixture dir must resolve in the **installed wheel** (cwd `/app/tests/fixtures/provider`), not `Path(__file__).parents[3]` (site-packages). Offline fixtures need enough finished games for a temporal split (48 labeled as of 2026-08-13).
- **Live ingest:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider nba-stats --seasons 2023 2024`. CI stays `--provider fixture` (NFR-003).
- **Verification semantics (LEAD-001):** **TEST-010** = static Compose topology (`docker compose config`) only. **TEST-013** = controlled-fixture training repeatability — **not** clean-clone **NFR-001**. **NFR-001** closes only on a **clean GitHub clone outside the developer working tree**. Do **not** add Compose e2e pytest. **ML-005:** TEST-007 remains **synthetic** CI smoke; live attestation ≠ PRD-ticked until owner/lead-manager closeout. **FR-012** Passing = static topology only. Attest/CI/publish-bar process: `engineering-lifecycle` + `docs/00-meta/reviews/2026-08-14-lead-nfr001-attest.md`.
- **TEST_DATABASE_URL safety:** integration tests target a **disposable / test-only** database only; must **never** drop/reset schemas on the developer's normal `DATABASE_URL`.
- **Persistence abstraction:** pipeline and API depend on store/repository **protocols**, not `psycopg` or Postgres-specific types in app/routes.
- **Protocol minimalism:** extend shared protocols only for operations required by existing pipeline/API consumers — no backend-admin-only capabilities on the shared surface.
- **Dumb adapters:** repositories and feature stores query/map/persist only — no ML feature calc, model selection, historical→feature transforms, or provider HTTP.
- **Idempotency:** same logical source record → one row; identical re-upsert unchanged count/values; same natural key with changed fields → **UPDATE**, never duplicate INSERT.
- **DB integrity + transactions:** uniqueness enforced by named DB constraints (at least `provider_team_id` UNIQUE, `provider_game_id` UNIQUE, `(game_id, team_id)` on `team_game_stats`, `(game_id, feature_version)` on `features`); stage-appropriate transactions with **rollback** on failure.
- **Feature identity:** `(game_id, feature_version)`; `feature_version` = feature-definition/preprocessing **contract**, not JSON serialization version. Postgres round-trip equals full **`FeatureRow` contract**.
- **Artifact identity:** API loads the **exact** pin-referenced artifact — not merely matching version strings. TEST-014: correct `game_id` + `feature_version` → predict + lineage match pin; `/v1/model` and `/v1/predict` vs same on-disk pin.
- **TEST-013 env pin:** module docstring records controlled-fixture/toolchain assumptions — exact numeric equality is not bit-for-bit XGBoost on every machine.
- **Regression rule:** existing tests must stay passing — **no** previously passing test weakened, skipped, or deleted to accommodate new adapters.
- **2026-08-14** · `SOURCE: agent` · **Provider adapters:** Live module `src/athletiq/provider/nba_stats.py` (`NbaStatsApiProvider`, CLI `--provider nba-stats`). Do **not** name it `nba_api.py` (PyPI clash). Protocol: `fetch_teams()` / `fetch_games(season start year)`. Page newest-first; API `pageSize` effectively **50**. Stop when a full mapped page is before Oct 1 of min wanted season. Map to `parse_game` shape; `provider_game_id` = string `gameId`; skip missing scores and non-NBA abbreviations (aliases PHO→PHX, BRK→BKN, CHO→CHA). No live HTTP in unit tests (inject `get_json`). ApiSportsProvider remains unused fallback. Product/provider policy: `athletiq-product`.
- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Dropped duplicate attest numbers/CI IDs (canonical in `engineering-lifecycle` reviews). Post-IMP gap pass closed locally 2026-08-13. No silent edits to Approved architecture/ADRs/SRS/implementation-plan **scope** — report blocking contradictions. Discovering UPDATE ≠ permission to redesign.

## Notes

- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Discarded Notes status (attest clone path, Compose port hold, local-only commit gossip).
