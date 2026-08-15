# AthletIQ

Sports analytics system for NBA historical data and pre-game win/lose predictions via API — built as a reproducible portfolio artifact (data → ML → API → DevOps).

**Docs before build.** Non-trivial implementation waits until upstream documents are **Approved**. See the always-on rule `.cursor/rules/engineering-lifecycle.mdc`.

## Local demo (Compose)

Not MVP-complete: PRD acceptance is unchecked. **NFR-001** clean-clone Compose is attested (2026-08-14) on `4a2f713`. Fixture provider needs **no** `API_SPORTS_KEY`. Remote CI (fixture-only) is green on `4a2f713` ([run 31753742525](https://github.com/RoeeHadar/AthletIQ/actions/runs/31753742525)).

**Prerequisites:** Docker Compose, Git.

```text
cp .env.example .env
docker compose up -d --build
docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider fixture
```

Live two completed seasons (no API key; ADR-011) — not the CI/demo path:

```text
docker compose run --rm etl python -m athletiq.pipeline --store postgres --provider nba-stats --seasons 2023 2024
```

Then:

- Open `http://127.0.0.1:8000/` (prediction UI — look up a `game_id`)
- or `GET http://127.0.0.1:8000/v1/health` and `GET http://127.0.0.1:8000/v1/model`

**Store selection:** host `python -m athletiq.pipeline` defaults `--store memory` (unit/offline). Compose demo **must** pass `--store postgres` as above — the etl image does not read `ATHLETIQ_STORE`. Host wrapper `scripts/run_pipeline.sh` also passes `--store postgres` (bash; not the Compose copy-paste). API Compose service sets `ATHLETIQ_STORE=postgres` and shares `artifacts` / `raw_data` with etl.

Clean-machine success of this path is **NFR-001**. Attested 2026-08-14 on a clean clone of `main` at `4a2f713` (not the developer working tree). It is **not** attested by TEST-013 (synthetic train-repeat) or TEST-010 (static Compose topology).

## Start here

| Want | Go to |
|---|---|
| How docs work | [`docs/README.md`](docs/README.md) |
| Why this project exists | [`docs/01-project/project-charter.md`](docs/01-project/project-charter.md) |
| What gets built | [`docs/02-product/PRD.md`](docs/02-product/PRD.md) |
| Gates (when work may start) | [`docs/00-meta/gates.md`](docs/00-meta/gates.md) |
| Quality checks | [`docs/00-meta/quality-checks.md`](docs/00-meta/quality-checks.md) |
| Change requests | [`docs/11-change-management/README.md`](docs/11-change-management/README.md) |
| Source-of-truth rules | [`docs/00-meta/documentation-guide.md`](docs/00-meta/documentation-guide.md) |

## Documentation hierarchy (short)

```text
Charter → PRD → SRS → Architecture → ADRs → Design →
Implementation Plan → Code → Tests → CI/CD → Deploy → Ops → Change Requests
                                                              └→ back to Requirements
```

## Implementation planning

Work is sequenced in [`docs/07-implementation/implementation-plan.md`](docs/07-implementation/implementation-plan.md). Code annotations (`# Implements: FR-XXX`) apply only to files listed under each task’s **Files/modules affected**.

## Contracts

| Path | Role |
|---|---|
| `api/openapi.yaml` | API contract |
| `database/schema.sql` | DB contract |
| `docker-compose.yml` | Local topology (`database` / `etl` / `api`) |
| `.github/workflows/ci.yml` | CI: lint ∥ unit → integration → image |
| `docs/06-design/model-card.md` | FR-010 methodology & limitations |

## Cursor skills

Project skills under `.cursor/skills/`: `project-discovery`, `requirements`, `architecture`, `architecture-decisions`, `implementation-planning`, `testing`, `devops-operations`, `engineering-review`. Elicitation uses Grill-Me (`.cursor/skills/grill-me/`).

## Status

**Gates 0–5 + Gate 7 Approved.** Gate 6: **IMP-001…012 Done**. Post-IMP remainings closed locally (Postgres adapters behind `--store` / `ATHLETIQ_STORE`, TEST-013/014 Passing). Remote CI (fixture-only) green on `4a2f713` ([run 31753742525](https://github.com/RoeeHadar/AthletIQ/actions/runs/31753742525)). **NFR-001** clean-clone Compose attested 2026-08-14. PRD acceptance unchecked.
