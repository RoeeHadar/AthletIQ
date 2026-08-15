# Change Request CR-004

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 1.0.0

Decision status: Accepted

```text
CR ID: CR-004
Title: Post-MVP iteration — WNBA, 3 NBA seasons, player load, synthetic odds, per-league pins, Comp A UI reconstruction
Requested by: Project owner (Grill-Me close + Implement, 2026-08-15)
Date: 2026-08-15
Problem / motivation:
  Owner closed post-MVP Grill-Me: one iteration covering more data, WNBA,
  player context, labeled synthetic Market P (not a book), and reconstructing
  the prediction UI to Comp A. MVP CR-001 reserved player tables; CR-003 UI
  has no odds chrome; DR-001 was 2 Must / 3 Should NBA seasons.
Impact analysis:
  - Requirements: Pull FUTURE-003 (WNBA, same basketball grain). Reopen player
    load (CR-001 reserved tables become loaded). Raise DR-001 to 3 completed
    NBA seasons Must + overlapping WNBA. Reverse betting *book* non-goal only;
    Market P is a labeled comparison column. Amend FR-001/002/004/015,
    DR-002/003; mint FR-016–019, DR-004, ML-010/011, CON-009.
  - Architecture: Extend in-plane (keep ADR-001/006/008/009). league/sport on
    teams/games; activate players; odds_snapshots via adapter→raw→Postgres.
    Predict does not call a book. Demo UI still FastAPI GET /. Live WNBA HTTP
    and live odds adapters are out of this CR (no-key NBA Stats API is NBA
    games-only; no named odds provider).
  - ADRs: ADR-012 (fixture/synthetic odds); ADR-013 (per-league selection pins).
    ADR-003 still binds inside each league. ADR-011 still binds live NBA.
  - Design: New feature_version with team-aggregated top-5-by-minutes L5
    pts/minutes; Comp A reconstruction then league + Market P.
  - Tests: TEST-015–019; CI remains fixture-only (NFR-003).
Decision: Accepted — owner Implement after Grill-Me close. Not a betting
  product. Not Comp B/C. Not film-room. Not pooled NBA+WNBA classifier.
Resulting implementation plan updates: IMP-013–018.
```

Register: `docs/00-meta/id-registry.md` (CR-004).
