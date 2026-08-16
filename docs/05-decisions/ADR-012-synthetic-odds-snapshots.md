# ADR-012: Fixture/synthetic odds snapshots (no live book)

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.1.0

Decision status: Accepted

## Context

Post-MVP Grill-Me (CR-004) wants a **Market P(home)** comparison beside the model without becoming a betting book. No odds provider is named. Predict must not call a book at request time (ADR-008 precomputed path). CI must stay fixture-only (NFR-003).

## Decision

1. This iteration persists **`odds_snapshots`** via the existing adapter → immutable raw JSON → curated Postgres path (ADR-006 / ADR-001).  
2. Snapshots are **fixture/synthetic** and **labeled** `source = synthetic` (API + UI).  
3. Implied probability is stored as `implied_p_home_win` captured **before** the game start in fixture time (no post-tip snapshots used for the served comparison).  
4. The prediction API **reads** the latest eligible snapshot for `game_id`; it does not fetch odds over the network.  
5. No real-money book, payments, or paid book API/key. CR-005 adds a **labeled e-coin simulation** (ADR-014); that is not a live odds feed and does not change `source=synthetic`.  
6. A **live** odds adapter is a follow-on ADR when the owner **names** a provider (CR-005 Q27 = not this CR).

## Alternatives considered

- Live book HTTP at predict time — rejected (latency, NFR-003, ADR-008, no named provider)  
- Omit Market P until a live feed exists — rejected (owner pulled comparison into this iteration)  
- Paid odds API this CR — rejected (Grill-Me: no paid book key)

## Consequences

- Schema grows `odds_snapshots`; OpenAPI may include nullable `market_p_home_win` + `market_source`.  
- UI must label the column synthetic; CR-003 “no odds chrome” applies only to the MVP-shipped surface, superseded for this iteration by CR-004.  
- Missing snapshot → omit Market P (null), do not invent a price.

## References

- Related requirements: FR-018, DR-004, CON-009, CR-004  
- Related architecture: `data-architecture.md`, `api-architecture.md`  
- Supersedes / superseded by: none (does not supersede ADR-011)
