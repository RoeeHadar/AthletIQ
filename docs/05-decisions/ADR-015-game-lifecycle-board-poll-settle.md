# ADR-015: Game lifecycle — scheduled persist, board poll, pipeline settle

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.0.0

Decision status: Accepted

## Context

Live `nba-stats` currently drops games with null scores and hardcodes `Finished`. A slate needs unplayed rows. A live board needs in-progress scores. Even-money stakes must settle when a game becomes real, not when a browser loads `/slate` (Grill-Me Q4, Q8, Q24–Q25). Kafka/WebSockets are out. NFR-003: CI stays fixture-only.

## Decision

1. **Scheduled/unplayed:** Persist rows with null scores and status not Finished. Live ingest **keeps** null-score games when the provider sends them. CI fixtures include scheduled NBA and WNBA rows.  
2. **Features / `P(home_win)`:** Built only from **prior completed** games (ML-001). Unplayed games still get feature rows from that history (ADR-008 precompute).  
3. **In-progress:** Upsert games whose scores may be non-null while status is not Finished. Display on `GET /board` only. Do not invent a clock.  
4. **Board poll:** A Compose loop polls **newest** `nba-stats` pages through the adapter (not a full unbounded re-page). Browser polls AthletIQ only.  
5. **Settle:** When the **pipeline** ingests a previously unplayed/in-progress game as Finished, it settles every open stake on that game. Re-runs are **idempotent**. `/slate` displays only.  
6. **Stake window:** New stake only if scores are still null and `game_start_time` is still in the future (UTC). Cancel/replace allowed only before tip.

## Alternatives considered

- Synthetic upcoming fixtures only — rejected (Q4=A)  
- Lazy settle on `GET /slate` — rejected (Q8=A)  
- Browser calls `nbaapi.com` — rejected (adapter lock)  
- Score/clock on the gamecast — rejected (Q24=A)

## Consequences

- `games.status` values and nullable scores become first-class.  
- Pipeline gains a settle stage after load.  
- Compose gains a documented poll loop (interval is a design default, e.g. 30s).  
- Live WNBA HTTP remains out: board live updates are NBA; WNBA in-progress rows are fixture if authored.

## References

- Related requirements: FR-021, FR-023, FR-025, FR-026, DR-006, CR-005  
- Related architecture: `system-architecture.md`, `data-architecture.md`  
- Related: ADR-006 (raw landing still binds), ADR-008, ADR-017
