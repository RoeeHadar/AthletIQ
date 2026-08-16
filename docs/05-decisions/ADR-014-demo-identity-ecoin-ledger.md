# ADR-014: Demo identity and e-coin ledger (no application auth)

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.0.0

Decision status: Accepted

## Context

CR-005 wants a multi-user e-coin simulation without becoming a login product or a real-money book. ADR-009 already binds **no application auth** on the demo API. PRD non-goals still exclude paid accounts and licensed gambling (Grill-Me Q1=B, Q23=A).

## Decision

1. Persist `users`, `wallets`, append-only `ledger_entries`, and `stakes` in PostgreSQL (ADR-001).  
2. Seed **two** demo users (`demo-1`, `demo-2`) at **1000** integer e-coins and a **house** wallet large enough to pay even-money wins. No refill this CR.  
3. Selected user is a query parameter `?user=` (not a cookie, not a password). Unknown users are rejected.  
4. **ADR-009 stays:** no login middleware.  
5. One open stake per `(user_id, game_id)`. Even-money: correct pick returns stake + equal house credit; wrong pick forfeits stake. Settle is **not** this ADR’s trigger (see ADR-015).  
6. Copy is stake/settle. Odds/juice/moneyline/payout language is forbidden. Model `P` and synthetic Market P are not prices.

## Alternatives considered

- Local registration + password hash — would supersede ADR-009  
- `localStorage` identity — hidden, weaker tests  
- Unlimited coins / refill control — rejected (Q7=A)  
- Real-money book — rejected (Q23=A)

## Consequences

- Schema migration for ledger tables; FastAPI JSON for balance/stake/cancel.  
- CON-009 amended: simulation allowed; real-money book still forbidden.  
- House wallet starting balance is a design constant (large integer), not a product Grill-Me number.

## References

- Related requirements: FR-022, FR-023, DR-005, CON-009, CR-005  
- Related architecture: `data-architecture.md`, `api-architecture.md`  
- Does not supersede ADR-009
