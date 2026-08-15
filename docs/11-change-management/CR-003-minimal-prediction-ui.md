# Change Request CR-003

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 1.0.0

Decision status: Accepted

```text
CR ID: CR-003
Title: Pull FUTURE-004 — minimal prediction UI for owner manual check
Requested by: Project owner (2026-08-15)
Date: 2026-08-15
Problem / motivation:
  MVP API is ready for owner manual test. Owner asked for a browser UI
  (Impeccable) to look up a game by id and read health / model / limitations
  without raw JSON. Confirmed: static HTML/CSS/JS served by FastAPI; English;
  category-standard dashboard (NBA.com/Stats craft bar).
Impact analysis:
  - Requirements: FUTURE-004 pulled; FR-015 minted (demo UI, no auth).
  - Architecture: UI is a same-origin static surface on the API container; not a new service.
  - ADRs: none; ADR-009 (no auth, localhost) still binds.
  - Design: Impeccable PRODUCT.md + approved comp A; not a betting product.
  - Tests: GET / returns HTML; existing TEST-008 still covers /v1/*.
Decision: Accepted — serve a local prediction UI at GET / from the API image.
  No extra Compose service. No betting, live odds, or player pages.
Resulting implementation plan updates: no new IMP id; files under api/static/.
```
