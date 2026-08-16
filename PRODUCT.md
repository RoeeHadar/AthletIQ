# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

static HTML/CSS/JS served by the existing FastAPI app (same origin). Owner chose this over a separate React/Vite process. Open `http://127.0.0.1:8000/`.

## Users

Primary: a sports/data analyst or developer running AthletIQ locally. Job: check pre-game home-win prediction for a known `game_id`, read methodology/limitations, and (CR-005) use the labeled e-coin slate plus in-progress board.

Stakeholder: project owner doing manual check. Artifact audience: technical reviewers. Not a real-money betting customer.

## Product Purpose

AthletIQ ingests NBA history, trains temporally honest home-win models, and serves binary + `P(home_win)` through a demo API. This UI exists so that check can happen in a browser instead of raw JSON.

Success: look up a loaded game by id, see prediction + probability, see health and model/limitations, without claiming the system “accurately predicts NBA games.”

## Positioning

Prediction is keyed to an already-ingested game (`game_id` / optional `provider_game_id`), uses only pre-tip team features, and always discloses the served pin and known limitations. It is not a live odds board and not a real-money book.

## Operating Context

Local Docker Compose (or the NFR-001 attest clone) on `127.0.0.1:8000`. No application auth (ADR-009). Fixture demo pin may be `xgboost-v1`; live NBA pin may be `logistic_regression-v1`. Same-origin `GET /v1/health`, `/v1/model`, `/v1/predict`. English UI.

## Capabilities and Constraints

- Lookup by `game_id` (required path). League control (NBA | WNBA). Show health, model metadata, methodology, limitations, labeled synthetic Market P.
- Three same-origin surfaces (CR-005 / ADR-016): gamecast `GET /` (no score/clock, no stake chrome); `GET /slate` (upcoming + labeled e-coin stake/settle); `GET /board` (in-progress display only). Producer-bar links among them.
- No real-money betting book (payments, juice, moneyline-as-price). Labeled e-coin simulation is allowed on `/slate` only. No live in-game *prediction* features. No auth, multi-tenant, GCP.
- Must not invent games, metrics, clocks, or win claims. Empty/error states from real API codes (`game_not_found`, `features_not_found`, `model_unavailable`, `db_unavailable`, plus ledger codes in api-design).
- Compose demo must keep `--store postgres`. CI stays fixture-only.

## Brand Commitments

Name **AthletIQ**. Voice: honest ML, not hype. Product copy in English.

Visual world (owner 2026-08-15 Grill-Me): **broadcast win-probability gamecast**. Craft bar: ESPN-style WP graphic language, not NBA.com/Stats. Producer bar + Home/Away split + synthetic Market P + legal chyrons. No film-room, no scorebug, no sportsbook language. Empty-desk convention is anti-reference.

## Evidence on Hand

Live API at `/v1/*`. Model card `docs/06-design/model-card.md`. Do not fabricate testimonials, season records, or “accuracy” marketing numbers. Fixture `game_id=48` is a known demo id on the attest stack.

## Product Principles

1. The prediction is a disclosed estimate, not a promise.
2. The task is lookup, not browsing a fake league.
3. Local demo, localhost, no auth theater.
4. Copy names real endpoints, pins, and failure codes.

## Accessibility & Inclusion

Keyboard-usable form, visible focus, color not the only state signal. English. No WCAG numeric target beyond that (NFR-004: no hard SLOs).
