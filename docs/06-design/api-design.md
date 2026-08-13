# API design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.0.0

> Design intent. Contract: `api/openapi.yaml`. FastAPI (CON-004). ADR-008, **ADR-009** (no auth).

## NFRs cited

- **NFR-002** — demo-grade  
- **NFR-004** — no hard latency/availability SLOs; sync request lifecycle only  
- **ADR-009** — no application auth on MVP (localhost / Compose assumption)

## Versioning

Base path: `/v1`

## Authentication

**None** for MVP (ADR-009). Not merely “unbuilt” — explicitly unsafe for public internet bind without a future auth ADR + CR.

## Endpoints

### `GET /v1/health`

- 200 — process up **and** selected model pin + artifact readable **and** DB reachable for a trivial check  
- 503 — pin/artifact missing **or** DB unreachable (`error.code`: `model_unavailable` | `db_unavailable`)

### `GET /v1/predict`

**Query:** `game_id` (string form of internal **BIGINT**) preferred; optional `provider_game_id` resolver.

**Response 200:** see OpenAPI — includes lineage fields.

`home_win_pred` = `p_home_win >= 0.5`.

### `GET /v1/model`

Read-only metadata / limitations / lineage.

- 200 — pin present  
- **503** — no selected model / pin/artifact missing (same as health model failure; `error.code`: `model_unavailable`)

## Errors

| HTTP | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | Missing/invalid params |
| 404 | `game_not_found` | Unknown `game_id` / unresolved provider id |
| 404 | `features_not_found` | Game exists but no feature row for pinned `feature_version` |
| 503 | `model_unavailable` | Pin/artifact missing |
| 503 | `db_unavailable` | PostgreSQL unreachable on read path |
| 500 | `internal_error` | Unexpected |

Envelope:

```json
{ "error": { "code": "features_not_found", "message": "...", "details": { "game_id": "...", "feature_version": "..." } } }
```

## Non-goals

Paid auth products, async prediction jobs, training triggers, live provider proxy.
