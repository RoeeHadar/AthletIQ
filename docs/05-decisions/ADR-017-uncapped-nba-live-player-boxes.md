# ADR-017: Uncapped live NBA ingest and live player boxes

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.0.0

Decision status: Accepted

## Context

ADR-011 binds live ingest to no-key `api.server.nbaapi.com` (games/teams). CR-004 clamped `season_depth` at 3 and left live player fetches empty (`[]`), so `player_agg` cold-started at 0.0. CR-005 Grill-Me Q13=C (no NBA season cap) and Q26=A (live player boxes on the **same** host). CI must stay fixture-only (NFR-003). Live WNBA HTTP is still out. Live odds are still out (Q27=B; ADR-012).

## Decision

1. **Live NBA history:** Do **not** clamp season depth at 3. Page `nba-stats` until pagination ends; keep every mappable NBA game. Do **not** age-prune live NBA seasons.  
2. **CI / Compose fixture demo:** Stay small (not a historical dump). Include scheduled rows (ADR-015).  
3. **Live player boxes:** Extend `NbaStatsApiProvider` to fetch per-game player stats from the same host (documented `include=playerGameBasicStats` or equivalent). Persist via existing `players` / `player_game_stats` grains.  
4. **WNBA:** Fixture only (2021–2025 completed + 2026 scheduled). Adapter still returns no live WNBA HTTP.  
5. **Retrain:** New NBA and WNBA pins on the new history (ML-012). Same protocol/hyperparameters/`feature_version`. CI 48-game fixture pin **unchanged**.  
6. ADR-011 remains the **provider choice**. This ADR extends its consequences; it does **not** supersede ADR-011.

## Alternatives considered

- Keep DR-001 at 3 seasons — rejected (Q12=B, Q13=C)  
- Keyed player/odds vendor — rejected (no signup URLs; Q26=A same host; Q27=B synthetic odds)  
- Retrain the CI 48-game pin — rejected (Q15)

## Consequences

- Uncapped paging is slow; board poll (ADR-015) uses **newest pages only** so `/board` does not re-page all history.  
- Live player HTTP volume is large; still Must for this CR.  
- Model-card / limitations must disclose distribution shift vs the CR-004 3-season pin and that old test log loss 0.623 does not bind the new pin.  
- `active_season_years` depth clamp of 3 is removed on the live path.

## References

- Related requirements: DR-001, FR-001, FR-027, FR-028, ML-012, CR-005  
- Related: [ADR-011](ADR-011-nba-stats-api-provider.md) (not superseded), ADR-012, ADR-013
