# Post-IMP integration invariants

## Must never miss

- **Store selection:** explicit `--store` / config wins. Unit/offline tests default **in-memory**. `DATABASE_URL` supplies **connection only** — its presence must **not** silently switch pytest or unit tests onto Postgres.
- **Demo vs CLI defaults:** `./scripts/run_pipeline.sh` explicitly passes `--store postgres` for Compose/demo e2e; `python -m athletiq.pipeline` defaults `--store memory`; API/ASGI uses `ATHLETIQ_STORE=postgres|memory` (Compose sets `postgres`).
- **Canonical Compose pipeline:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture` — Compose demo **must** pass `--store postgres`; the etl service does **not** read `ATHLETIQ_STORE`.
- **Verification semantics (LEAD-001):** **TEST-010** = static Compose topology (`docker compose config`) only — not bring-up, pipeline, or `/v1/health`. **TEST-013** = controlled-fixture training repeatability — **not** clean-clone **NFR-001**. **NFR-001** Implementation **Partial** until owner attestation of documented README workflow. **ML-005** verification = synthetic TEST-007 only — not attested NBA holdout. **FR-012** Passing = static topology only.
- **TEST_DATABASE_URL safety:** integration tests target a **disposable / test-only** database only; must **never** drop/reset schemas on the developer's normal `DATABASE_URL`.
- **Persistence abstraction:** pipeline and API depend on store/repository **protocols**, not `psycopg` or Postgres-specific types in app/routes.
- **Protocol minimalism:** extend shared protocols only for operations required by existing pipeline/API consumers — no backend-admin-only capabilities on the shared surface.
- **Dumb adapters:** repositories and feature stores query/map/persist only — no ML feature calc, model selection, historical→feature transforms, or provider HTTP.
- **Idempotency:** same logical source record → one row; identical re-upsert unchanged count/values; same natural key with changed fields → **UPDATE**, never duplicate INSERT.
- **DB integrity + transactions:** uniqueness enforced by named DB constraints (verify at least `provider_team_id` UNIQUE, `provider_game_id` UNIQUE, `(game_id, team_id)` PK/UNIQUE on `team_game_stats`, `(game_id, feature_version)` PK on `features`); stage-appropriate transactions with **rollback** on failure — rollback tests may use invalid op/controlled failure, not production-only artificial hooks.
- **Feature identity:** `(game_id, feature_version)`; `feature_version` = feature-definition/preprocessing **contract**, not JSON serialization version. Postgres round-trip equals full **`FeatureRow` contract** (`game_id`, `feature_version`, `payload`, every metadata field) — do not invent extra metadata requirements.
- **Artifact identity:** API loads the **exact** pin-referenced artifact (path/name mandatory; hash optional if pin already carries it) — not merely matching version strings. TEST-014: correct `game_id` + `feature_version` → predict succeeds + lineage matches pin; `/v1/model` and `/v1/predict` compared to the **same** on-disk pin/artifact.
- **TEST-013 env pin:** module docstring records controlled-fixture/toolchain assumptions — exact numeric equality is not a claim of bit-for-bit XGBoost on every machine.
- **Regression rule:** existing tests must stay passing — **no** previously passing test weakened, skipped, or deleted to accommodate new adapters.
- **Post-IMP gap pass (closed locally):** owner-approved plan **implemented** 2026-08-13 — no new IMP-IDs; no live `API_SPORTS_KEY`; no remote GitHub CI green claims from local runs alone. No edits to Approved architecture/ADRs/SRS/implementation-plan **scope** unless a blocking contradiction is **reported** — never silently resolved in Approved docs. Discovering inconvenience is **not** permission to redesign.

## Notes

- **2026-08-13** · `SOURCE: sweep` · LEAD-001: canonical Compose command with `--store postgres`; honest NFR-001 Partial / TEST-010 static topology / TEST-013 ≠ clean-clone labels propagated to SRS, traceability, test-plan, README.
