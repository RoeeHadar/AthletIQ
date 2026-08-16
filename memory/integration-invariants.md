# Post-IMP integration invariants

## Must never miss

- **Store selection:** explicit `--store` / config wins. Unit/offline tests default **in-memory**. `DATABASE_URL` supplies **connection only** — its presence must **not** silently switch pytest or unit tests onto Postgres.
- **Demo vs CLI defaults:** `./scripts/run_pipeline.sh` explicitly passes `--store postgres` for Compose/demo e2e; `python -m athletiq.pipeline` defaults `--store memory`; API/ASGI uses `ATHLETIQ_STORE=postgres|memory` (Compose sets `postgres`).
- **Canonical Compose pipeline:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture` — Compose demo **must** pass `--store postgres`; the etl service does **not** read `ATHLETIQ_STORE`. Default fixture dir must resolve in the **installed wheel** (cwd `/app/tests/fixtures/provider`), not `Path(__file__).parents[3]` (site-packages). Fixture set: small NBA + WNBA including authored WNBA 2021–2025 + 2026 scheduled and NBA 2026 scheduled (`tests/fixtures/provider/`).
- **Live ingest:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider nba-stats` (CR-005: **no** season-depth clamp of 3). CI stays `--provider fixture` (NFR-003). No live WNBA HTTP. Board poll: `python -m athletiq.board_poll` in the **etl** image (newest pages; default 30s; not a fourth service).
- **Postgres migrate:** `--store postgres` pipeline and `ATHLETIQ_STORE=postgres` API apply `database/migrations/*.sql` (**001, 002, 003**). `migrations_dir()` must **not** use `Path(__file__).parents[3]` alone (installed wheel → `/usr/local/lib/python3.11/database`). Resolve cwd `/app/database/migrations`, then env `ATHLETIQ_MIGRATIONS_DIR`. Compose initdb mounts files for **fresh** volumes; existing `pgdata` still needs the apply path.
- **Verification semantics (LEAD-001):** **TEST-010** = static Compose topology (`docker compose config`) only. **TEST-013** = controlled-fixture training repeatability — **not** clean-clone **NFR-001**. **NFR-001** closes only on a **clean GitHub clone outside the developer working tree**. Do **not** add Compose e2e pytest. **ML-005:** TEST-007 remains **synthetic** CI smoke; live attestation ≠ PRD-ticked until owner/lead-manager closeout. **FR-012** Passing = static topology only. Attest/CI/publish-bar process: `engineering-lifecycle` + `docs/00-meta/reviews/2026-08-14-lead-nfr001-attest.md`.
- **TEST_DATABASE_URL safety:** integration tests target a **disposable / test-only** database only; must **never** drop/reset schemas on the developer's normal `DATABASE_URL`.
- **Persistence abstraction:** pipeline and API depend on store/repository **protocols**, not `psycopg` or Postgres-specific types in app/routes.
- **Protocol minimalism:** extend shared protocols only for operations required by existing pipeline/API consumers — no backend-admin-only capabilities on the shared surface.
- **Dumb adapters:** repositories and feature stores query/map/persist only — no ML feature calc, model selection, historical→feature transforms, or provider HTTP.
- **Idempotency:** same logical source record → one row; identical re-upsert unchanged count/values; same natural key with changed fields → **UPDATE**, never duplicate INSERT.
- **DB integrity + transactions:** uniqueness enforced by named DB constraints (at least `(league, provider_team_id)`, `(league, provider_game_id)`, `(game_id, team_id)` on `team_game_stats`, `(game_id, feature_version)` on `features`, `(game_id, source, captured_at)` on `odds_snapshots`); stage-appropriate transactions with **rollback** on failure.
- **Feature identity:** `(game_id, feature_version)`; `feature_version` = feature-definition/preprocessing **contract**, not JSON serialization version. Postgres round-trip equals full **`FeatureRow` contract**.
- **Artifact identity:** API loads the **exact** pin-referenced artifact — not merely matching version strings. TEST-014: correct `game_id` + `feature_version` → predict + lineage match pin; `/v1/model` and `/v1/predict` vs same on-disk pin.
- **TEST-013 env pin:** module docstring records controlled-fixture/toolchain assumptions — exact numeric equality is not bit-for-bit XGBoost on every machine.
- **Regression rule:** existing tests must stay passing — **no** previously passing test weakened, skipped, or deleted to accommodate new adapters.
- **2026-08-16** · `SOURCE: agent` · **WHY:** CR-005 Gate 6 code landed locally (IMP-019–025). **HOW:** Live NBA player boxes come from the same `nba-stats` host (`include=playerGameBasicStats`); mapper keeps null-score scheduled rows; do not hard-return `[]`. Odds snapshots stay synthetic (ADR-012). Page newest-first; do not drop games solely for missing scores (FR-021). Map to `parse_game` shape; `provider_game_id` = string `gameId`. No live HTTP in unit tests (inject `get_json`). ApiSportsProvider remains unused fallback. Product/provider policy: `athletiq-product`. Do **not** name the module `nba_api.py` (PyPI clash).
- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Dropped duplicate attest numbers/CI IDs (canonical in `engineering-lifecycle` reviews). Post-IMP gap pass closed locally 2026-08-13. No silent edits to Approved architecture/ADRs/SRS/implementation-plan **scope** — report blocking contradictions.
- **2026-08-16** · `SOURCE: consolidate` · **WHY:** Merged same-day Compose UI/demo ops bullets. Compose **`api` image bakes `api/static/` at build** — after UI edits: `docker compose up -d --build api` then hard-refresh. **Only demo UI is `http://127.0.0.1:8000/`** — do **not** start a second uvicorn on **8010**. **`GET /` and `/static` send `Cache-Control: no-store`**; stale-looking :8000 with current repo static often means **browser cache** — hard-refresh (`Ctrl+F5`) before assuming a stale image. Discovering UPDATE ≠ permission to redesign. **Demo model/methodology:** UI chyrons come from `GET /v1/model`; **503 MODEL_UNAVAILABLE** means no trained pin on the API artifacts path — run canonical Compose fixture pipeline, then restart/rebuild `api`; do not treat as a UI bug.

## Notes

- **2026-08-14** · `SOURCE: consolidate` · **WHY:** Discarded Notes status (attest clone path, Compose port hold, local-only commit gossip).

```yaml
id: ep_2026-08-16_migrate_001
time: 2026-08-16T00:25:00+03:00
what: "Compose fixture pipeline crashed: migrations_dir() used Path(__file__).parents[3] alone → site-packages/database/migrations (missing). Fixed to probe cwd /app/database/migrations, env ATHLETIQ_MIGRATIONS_DIR, then src checkout; added test_migrations_dir_finds_sql."
source_type: failure
confidence: high
tags: [compose, migrate, wheel-path, cr-004]
cause: "parents[3] from installed athletiq.db.migrate resolves to site-packages, not /app"
next: "Standing rule is Postgres migrate bullet above; rebuild api image after migrate.py change"
```

```yaml
id: ep_2026-08-16_cache_001
time: 2026-08-16T00:56:00+03:00
what: "Owner reported :8000 wrong UI (old desk) vs :8010 correct gamecast; root cause was browser cache on the :8000 tab — server already served gamecast after hard refresh. Fixed Cache-Control no-store on GET / and /static; stopped leftover :8010 uvicorn."
source_type: failure
confidence: high
tags: [demo-ui, browser-cache, compose, port-8010, gamecast]
cause: "Browser cached pre-gamecast desk HTML while parallel :8010 uvicorn served live static from disk"
next: "Standing rule is Compose/static bullet above; hard-refresh before rebuild"
```
