# Change Request CR-001

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-13  
Version: 1.0.0

Decision status: Accepted

```text
CR ID: CR-001
Title: MVP persist/ingest team-level entities only; player tables reserved
Requested by: Managing-architect review 2026-08-13 (F-001) + owner docs-honesty pass
Date: 2026-08-13
Problem / motivation:
  SRS/PRD Musts required persisting players and player statistics. Schema has
  `players` / `player_game_stats`. Pipeline ingest/load never writes those tables
  (adapter is teams+games; fixtures have no players.json). Leaving Musts unchanged
  is schema theater. Implementing player ingest is post-MVP relative to locked
  team-level ML features (ml-design: no player-level features).
Impact analysis:
  - Requirements: FR-001 AC drops fetch-players; FR-002/DR-002 MVP themes =
    teams, games, team statistics; player themes = schema-reserved / Future.
    FR-003 analytics Must = aggregations + windows over persisted team stats.
    FR-004 features from team stats only (already ML design).
  - Architecture: data-architecture notes reserved player tables; no ADR change.
  - ADRs: none superseded (ADR-002 adapter still teams/games for MVP).
  - Design: database-design documents reserved tables + payload envelope;
    analytics examples distinguish team Must vs player Future.
  - Tests: TEST-002 may still assert reserved tables exist; TEST-004 grain =
    teams/games/team_game_stats (not player_game_stats load); TEST-005 Must =
    rolling team windows; top-scorer helper is not a pipeline outcome.
Decision: Accepted — demote player persistence/ingest from MVP Must; keep
  tables+indexes as reserved schema for post-MVP. Do not advertise player
  load or top-scorer SQL as a pipeline outcome.
Resulting implementation plan updates: IMP-004 notes CR-001; no new IMP.
  No code required for this CR (aligns docs to existing team-level path).
```

Register: `docs/00-meta/id-registry.md` (CR-001).
