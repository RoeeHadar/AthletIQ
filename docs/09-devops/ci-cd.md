# CI/CD

Status: Draft  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 0.3.1

## MVP pipeline (OPS-001 / CON-005)

```text
push/PR → lint ∥ unit → integration (ephemeral Postgres) → Docker image build
```

Workflow: `.github/workflows/ci.yml` (MVP workflow; not a stub).

| Job | Role |
|---|---|
| `lint` | `ruff check` + `compileall` |
| `unit` | `pytest tests/unit` — fixtures only (**NFR-003**; no live `nba-stats` / no `API_SPORTS_KEY`). CR-005 TEST-020–028 stay fixture/injected-HTTP. |
| `integration` | `needs: [lint, unit]`; Postgres 16 service + `TEST_DATABASE_URL` |
| `image` | `needs: [integration]`; build `Dockerfile.etl` + `api/Dockerfile` (build-only) |

## Post-MVP / open

- `[OPEN QUESTION: deploy target and CD after image build]` — discovery mentioned deploy; publish bar stopped at image build.

## Secrets (SEC-002)

CI uses repository secrets / env when needed — never commit API keys. Fixture CI path requires **no** live provider secret.
