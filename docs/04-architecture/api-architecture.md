# API architecture

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

> Sync demo FastAPI (CON-004). Contract details in Gate 4 `api-design.md`.

## Purpose

Synchronous home-win predictions for a known **`game_id`** using precomputed features and the **batch pin for `game.league`** (FR-009, ADR-008, ADR-013). Optional labeled synthetic Market P from `odds_snapshots` (ADR-012). Same-origin UI at `GET /`, `GET /slate`, `GET /board` (FR-015, FR-024, FR-025, ADR-016). Ledger JSON for demo users (ADR-014) on the same app. Predict does **not** call a book or the live provider. Browser does **not** call `nbaapi.com`. Gamecast has no score/clock and no stake chrome. `/slate` may use stake/settle copy. `/board` is in-progress display only.

## Request lifecycle

```text
HTTP request (sync)
  → validate
  → resolve feature row (game_id, feature_version from pin)
  → shared preprocessing
  → infer
  → JSON response + lineage
```

No async queues/workers in MVP.

## Contract summary

| Item | Rule |
|---|---|
| Primary key | `game_id` |
| Feature row | `(game_id, feature_version)` |
| Model | Published **per-league** pin only (ADR-013) |
| Market P | Nullable; from curated synthetic snapshot; never live HTTP |
| Team identity | Nullable name + abbreviation from `teams` via `home_team_id` / `away_team_id` (FR-020). Never invented. |
| Optional resolver (MVP) | `provider_game_id` → unique `game_id`. Home/away/date matchup browse is **Future / not MVP**. |

## Non-responsibilities

No training, provider download, dataset mutation, or per-request model selection.

## CI note

API integration tests use fixtures — not the live NBA provider (NFR-003).
