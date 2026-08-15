# Infrastructure

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 0.3.1

## Local (MVP)

Docker Compose (`docker-compose.yml`) services:

| Service | Role |
|---|---|
| `database` | PostgreSQL 16 (ADR-001); init via `001_initial.sql` + `002_cr004_league_players_odds.sql`; pipeline/API also apply forward migrations |
| `etl` | Batch image (`Dockerfile.etl`); shares `raw_data` + `artifacts` volumes. **Canonical Compose pipeline:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture` |
| `api` | FastAPI (`api/Dockerfile`); publishes `127.0.0.1:8000` (ADR-009) |

Volumes: `pgdata`, `raw_data` (immutable raw JSON, ADR-006), `artifacts` (model pin/joblib, ADR-004).

Credentials: `POSTGRES_*` / `DATABASE_URL` from environment or `.env` (never commit secrets).

**Store selection:** host `python -m athletiq.pipeline` defaults `--store memory` (intentional for unit/offline). Compose demo **must** pass `--store postgres` (canonical command above). `scripts/run_pipeline.sh` is the **host** bash wrapper that also passes `--store postgres` — do not treat it as the etl-container command (image has no bash). API uses `ATHLETIQ_STORE=postgres|memory` (Compose sets postgres). Pipeline CLI does **not** read `ATHLETIQ_STORE`. `DATABASE_URL` is connection-only.

## Open

- `[OPEN QUESTION: cloud hosting / registry for images]`
- Resource limits and scalability targets: `[OPEN QUESTION: not defined — Grill-Me when architecture reaches this]`
