# ADR-016: Three FastAPI UI surfaces

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.0.0

Decision status: Accepted

## Context

CR-004 locked `GET /` as a broadcast win-probability **gamecast** (no score/clock, no sportsbook chrome). CR-005 adds an upcoming slate and an in-progress board. Folding those into the first viewport would wreck the gamecast (Grill-Me Q6, Q19, Q21, Q24).

## Decision

1. Keep the gamecast at **`GET /`** (FR-015). No score/clock/quarter.  
2. Add **`GET /slate`** (upcoming table, demo-user switcher, stake/settle, balance).  
3. Add **`GET /board`** (in-progress only).  
4. **Producer bar** on all three: two-way links among `/`, `/slate`, `/board`. Same origin. Not a marketing nav.  
5. **Visual bar:** `/slate` and `/board` share the gamecast **instrument family**. Dramatic-improvement bar applies. Not a gray admin table, not a second NBA.com desk, not sportsbook chrome.  
6. JSON APIs for slate/board/ledger live on the same FastAPI app (localhost bind, ADR-009).

## Alternatives considered

- Fold slate into `GET /` — rejected (Q6=A)  
- Replace `GET /` with a dashboard — rejected  
- Unlinked `/slate` (type the URL) — rejected (Q19=A)  
- Score/clock on gamecast — rejected (Q24=A)

## Consequences

- Static assets for two additional pages; `Cache-Control: no-store` remains.  
- TEST-019 still forbids sportsbook words on gamecast; TEST-024/028 cover `/slate` and `/board`.  
- Demo UI remains `http://127.0.0.1:8000/` only (no second uvicorn).

## References

- Related requirements: FR-015, FR-024, FR-025, CR-005  
- Related architecture: `api-architecture.md`  
- Does not supersede CR-004 gamecast lock
