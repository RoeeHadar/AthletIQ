# Change Request CR-005

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.0.0

Decision status: Accepted

```text
CR ID: CR-005
Title: Basketball platform slice — e-coin ledger, /slate, /board, uncapped live NBA, live player boxes, retrain
Requested by: Project owner (Grill-Me Q1–Q27 close + confirm, 2026-08-16)
Date: 2026-08-16
Problem / motivation:
  Owner opened a post-CR-004 platform fork (accounts, e-coin simulation,
  upcoming slate, live gameboard, more history) and closed Grill-Me Q1–Q27.
  CR-004 is a gamecast + WNBA-fixture + synthetic Market P slice. It does
  not persist unplayed games, has no ledger, drops null-score live rows,
  caps NBA depth at 3, and leaves live player boxes empty.
Impact analysis:
  - Requirements: Amend FR-001/002/015/016/017, DR-001/002/003, CON-009,
    ML-005 (new split; old live 0.623 does not bind). Mint FR-021–028,
    DR-005/006, ML-012. Keep NFR-003 fixture CI. Pull FUTURE-008 live
    gameboard as GET /board (not live in-game *prediction*). Do not pull
    FUTURE-006 live odds. Do not pull FUTURE-007 live WNBA HTTP.
  - Architecture: Extend in-plane (ADR-001/006/008/009/011/012/013).
    New ADRs 014–017. No Kafka/Redis/K8s/GCP. No application auth.
    Predict still does not call a book. Browser never calls nbaapi.com.
  - ADRs: ADR-014 demo identity + e-coin ledger; ADR-015 game lifecycle
    (scheduled persist, in-progress board poll, Finished pipeline settle);
    ADR-016 three FastAPI surfaces; ADR-017 uncapped live NBA + live
    player boxes (extends ADR-011; does not supersede). ADR-012 stays
    synthetic Market P. ADR-009 stays.
  - Design: users/wallets/stakes; integer even-money; /slate next-20;
    /board in-progress; gamecast unchanged (no score/clock); dramatic-
    improvement bar on new surfaces; same feature_version; retrain NBA
    + WNBA pins; CI 48-game pin unchanged.
  - Tests: TEST-020–028; CI remains fixture-only (NFR-003).
Decision: Accepted — owner confirmed shared understanding 2026-08-16.
  Labeled e-coin simulation, not a real-money book. Not extra sports.
  Not live WNBA HTTP. Not live odds. Not Kafka.
Resulting implementation plan updates: IMP-019–025.
```

Register: `docs/00-meta/id-registry.md` (CR-005).
