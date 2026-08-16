# API design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

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

**Response 200:** OpenAPI — includes lineage fields, `league`, nullable `market_p_home_win` / `market_source` (`synthetic` or omitted), and nullable home/away `team_name` / `team_abbreviation` from the `teams` table (never invented).

`home_win_pred` = `p_home_win >= 0.5`. Pin chosen by `game.league` (ADR-013).

### `GET /v1/model`

Read-only metadata / limitations / lineage. Optional query `league` (`nba` default).

- 200 — pin present for that league  
- **503** — no selected model / pin/artifact missing (`error.code`: `model_unavailable`)

### `GET /` / `GET /slate` / `GET /board` (HTML)

Same-origin static UI (ADR-016). `Cache-Control: no-store`. Demo bind `127.0.0.1:8000` only (no second uvicorn).

| Path | Role |
|---|---|
| `GET /` | Gamecast (FR-015). No score/clock/quarter. No stake chrome. |
| `GET /slate` | Upcoming table + demo-user switcher + stake/cancel/replace. Displays settlement **results**; does **not** settle (pipeline does). Query `user` (`demo-1` \| `demo-2`). |
| `GET /board` | In-progress only (FR-025). Clock only if the provider sent one. |

Producer-bar links among the three. `/slate` copy may use **stake/settle** (verbs for the simulation). Odds/juice/moneyline/payout language is forbidden on all three. Gamecast still has **no** stake chrome (TEST-019). `/slate` HTML/JSON **display** only — they do not run settle.

### Ledger / slate / board JSON (same FastAPI, no auth)

Design intent (contract in OpenAPI at IMP-023):

| Method | Path | Role |
|---|---|---|
| GET | `/v1/slate` | Next 20 unplayed pre-tip games + that user’s open stakes. Query `user`. |
| GET | `/v1/board` | In-progress games only |
| GET | `/v1/users/{slug}/wallet` | Integer balance |
| POST | `/v1/stakes` | Place or replace. Body: `user`, `game_id`, `side`, `amount`, optional `replace` (boolean, **default false**). |
| POST | `/v1/stakes/{id}/cancel` | Cancel before tip |

Unknown `user` → `user_not_found`. `?user=house` is rejected. Amount is a positive integer, min 1, max unlocked balance.

**Replace (FR-023):** If an open stake already exists for `(user, game)` and `replace` is **false** → 409 `duplicate_open_stake`. If `replace` is **true** and the stake window is still open → update side/amount and adjust the ledger (unlock previous lock, lock the new amount). If `replace` is **true** and no open stake exists → treat as a new place. After tip / scores present → 400 `stake_window_closed` even with `replace=true`.

## Errors

| HTTP | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | Missing/invalid params |
| 400 | `insufficient_balance` | Stake would take unlocked balance below zero |
| 400 | `stake_window_closed` | Scores non-null, tip not in the future, or after-tip cancel/replace |
| 404 | `game_not_found` | Unknown `game_id` / unresolved provider id |
| 404 | `features_not_found` | Game exists but no feature row for pinned `feature_version` |
| 404 | `user_not_found` | Unknown demo slug |
| 409 | `duplicate_open_stake` | Open stake already exists for `(user, game)` and `replace` is false |
| 503 | `model_unavailable` | Pin/artifact missing |
| 503 | `db_unavailable` | PostgreSQL unreachable on read path |
| 500 | `internal_error` | Unexpected |

Envelope:

```json
{ "error": { "code": "features_not_found", "message": "...", "details": { "game_id": "...", "feature_version": "..." } } }
```

`message` must not use odds/juice/moneyline/payout/wager language.

## Non-goals

Paid auth products, async prediction jobs, training triggers, live provider proxy, live book HTTP, Kafka.
