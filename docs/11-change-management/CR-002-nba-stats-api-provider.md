# Change Request CR-002

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-14  
Version: 1.0.0

Decision status: Accepted

```text
CR ID: CR-002
Title: Bind live NBA ingest to no-key NBA Stats API (api.server.nbaapi.com)
Requested by: Project owner (2026-08-14) after API-Sports / RapidAPI / Highlightly /
  BALLDONTLIE signup dashboards rendered empty; owner confirmed PowerShell JSON probe
Date: 2026-08-14
Problem / motivation:
  ADR-002 bound MVP live ingest to API-Sports. Owner cannot reach API-Sports or
  RapidAPI/Highlightly/BALLDONTLIE dashboards (empty pages / NXDOMAIN / 403).
  A no-key JSON API at https://api.server.nbaapi.com/api/games returns teams,
  scores, and dates. Owner confirmed the documented PowerShell probe ("JSON works").
  Product scope stays NBA-only (not multi-sport).
Impact analysis:
  - Requirements: CON-007 preferred provider becomes NBA Stats API per ADR-011;
    FR-001 adapter boundary unchanged; SEC-001 still env-only (this provider
    needs no secret); NFR-003 still no live calls in CI (fixtures remain).
  - Architecture: system/data diagrams cite NBA Stats API + ADR-011.
  - ADRs: ADR-002 Superseded; ADR-011 Accepted.
  - Design: no feature/ML/schema change; raw JSON still teams.json + games_{season}.json.
  - Tests: TEST-003 adds offline unit coverage for the new adapter (mocked pages);
    live two-season ingest is attestation (DR-001 / ML-005), not CI.
Decision: Accepted — live default provider is api.server.nbaapi.com (no API key).
  Keep FixtureProvider for CI/demo. Keep ApiSportsProvider as unused fallback.
  Do not expand to other sports in this CR.
Resulting implementation plan updates: IMP-003 note — additional adapter module;
  no new IMP id. CLI --provider nba-stats.
```

Register: `docs/00-meta/id-registry.md` (CR-002, ADR-011).
