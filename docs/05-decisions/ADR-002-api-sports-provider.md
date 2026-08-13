# ADR-002: API-Sports NBA as MVP data provider

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-12  
Version: 1.0.0

Decision status: Accepted

## Context

CON-007 requires an external NBA provider behind an adapter; Charter preferred API-Sports. PRD keeps provider abstract.

## Decision

MVP default provider is **API-Sports NBA** (free-tier class). All provider I/O goes through an **adapter interface** so transform/load stay provider-agnostic.

## Alternatives considered

- BALLDONTLIE — free tier historically weak on per-game stats without paid tier
- `nba_api` — deep history, unofficial/breakage risk; weaker “Sports API” narrative
- Multi-provider from day one — unnecessary MVP complexity

## Consequences

- Secrets: API-Sports key via env (SEC-001).
- Rate limits may force multi-day backfill for DR-001 Should(3); Must(2) remains the bar.
- Fallbacks documented only; switching provider requires adapter implementation + possible CR if seasons/fields change.

## References

- Related requirements: FR-001, CON-007, DR-001, SEC-001  
- Related architecture docs: `system-architecture.md`, `data-architecture.md`  
- Grill-Me architecture Q2 (2026-08-12)
