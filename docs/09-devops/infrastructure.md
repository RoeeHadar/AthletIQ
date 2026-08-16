# Infrastructure

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 0.4.0

## Local (MVP + CR-005)

Docker Compose (`docker-compose.yml`) services — **still three** (`database`, `etl`, `api`). **Do not** add Kafka, Redis, Kubernetes, GCP, or a fourth Compose service for the board.

| Service | Role |
|---|---|
| `database` | PostgreSQL 16 (ADR-001); init via `001_initial.sql` + `002_cr004_league_players_odds.sql` + `003_cr005_ledger_game_lifecycle.sql`; pipeline/API also apply forward migrations |
| `etl` | Batch image (`Dockerfile.etl`); shares `raw_data` + `artifacts` volumes. **Canonical Compose pipeline:** `docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture`. **Board poll** (ADR-015) runs in this **same** image: `python -m athletiq.board_poll` (or documented equivalent) against newest `nba-stats` pages only. Design default interval **30s**. CI does **not** run live poll (NFR-003). |
| `api` | FastAPI (`api/Dockerfile`); publishes `127.0.0.1:8000` (ADR-009); HTML `/`, `/slate`, `/board` |

Volumes: `pgdata`, `raw_data` (immutable raw JSON, ADR-006), `artifacts` (model pin/joblib, ADR-004).

Credentials: `POSTGRES_*` / `DATABASE_URL` from environment or `.env` (never commit secrets).

**Store selection:** host `python -m athletiq.pipeline` defaults `--store memory` (intentional for unit/offline). Compose demo **must** pass `--store postgres` (canonical command above). `scripts/run_pipeline.sh` is the **host** bash wrapper that also passes `--store postgres` — do not treat it as the etl-container command (image has no bash). API uses `ATHLETIQ_STORE=postgres|memory` (Compose sets postgres). Pipeline CLI does **not** read `ATHLETIQ_STORE`. `DATABASE_URL` is connection-only.

**Board poll vs history job:** unbounded live NBA paging is the pipeline job (ADR-017). The poll loop must not re-page all history. The browser polls AthletIQ only — never `nbaapi.com`.

## Open

- `[OPEN QUESTION: cloud hosting / registry for images]`
- Resource limits and scalability targets: `[OPEN QUESTION: not defined — Grill-Me when architecture reaches this]`
