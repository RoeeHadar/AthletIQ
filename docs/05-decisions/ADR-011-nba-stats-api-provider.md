# ADR-011: NBA Stats API as MVP live data provider

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-14  
Version: 1.0.0

Decision status: Accepted

## Context

CON-007 requires an external NBA provider behind an adapter. ADR-002 chose API-Sports. Owner cannot use API-Sports or commercial signup dashboards (empty pages). Owner confirmed `GET https://api.server.nbaapi.com/api/games` returns JSON with home/away and scores (CR-002). PRD stays provider-abstract and NBA-scoped.

## Decision

MVP **live** ingest uses the public **NBA Stats API** at `https://api.server.nbaapi.com` (no API key). All provider I/O still goes through the adapter interface. CI and the Compose fixture demo keep `FixtureProvider` (NFR-003).

The `season` query parameter on this API is unreliable. The adapter pages newest-first and filters by tip date / `gameId` into AthletIQ season start years (Oct–June).

## Alternatives considered

- API-Sports / RapidAPI API-Basketball — locked by ADR-002; dashboards unreachable for the owner
- Highlightly / BALLDONTLIE — JS signup pages empty for the owner
- Sports Information (RapidAPI) — not a drop-in; day-based scoreboard; multi-sport product risk
- `nba_api` / stats.nba.com — unofficial; stats.nba.com timed out from this workspace
- Stay fixture-only — fails DR-001 live seasons and real ML-005

## Consequences

- No `API_SPORTS_KEY` required for the live path (`--provider nba-stats`).
- Third-party unofficial feed (Basketball-Reference-sourced). Document as a limitation; adapter can be replaced later.
- Pagination + date filter instead of one season-scoped call; polite delay between pages.
- `provider_game_id` is the API `gameId` string (e.g. `202406170BOS`); internal `game_id` remains BIGSERIAL (ADR-010).
- Post-MVP other sports use additional adapters (e.g. MLB StatsAPI), not this CR.
- ADR-002 is **Superseded**.

## References

- Related requirements: FR-001, CON-007, DR-001, SEC-001, NFR-003, CR-002
- Related architecture docs: `system-architecture.md`, `data-architecture.md`
- Supersedes: [ADR-002](ADR-002-api-sports-provider.md)
