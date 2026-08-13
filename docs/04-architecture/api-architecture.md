# API architecture

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.1

> Sync demo FastAPI (CON-004). Contract details in Gate 4 `api-design.md`.

## Purpose

Synchronous home-win predictions for a known **`game_id`** using precomputed features and a batch-pinned model (FR-009, ADR-008).

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
| Model | Published pin only |
| Optional resolver (MVP) | `provider_game_id` → unique `game_id`. Home/away/date matchup is **Future / not MVP**. |

## Non-responsibilities

No training, provider download, dataset mutation, or per-request model selection.

## CI note

API integration tests use fixtures — not the live NBA provider (NFR-003).
