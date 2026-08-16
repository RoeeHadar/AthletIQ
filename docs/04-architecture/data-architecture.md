# Data architecture

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-16  
Version: 1.2.0

> Zones and lineage. System/deployment: `system-architecture.md`.

## Lifecycle

```text
NBA Stats API (NBA live: games + player boxes, uncapped) / Fixture adapter (NBA+WNBA+players+synthetic odds+scheduled)
  → Adapter → Raw JSON (immutable FS) → Validate
  → Curated PostgreSQL (idempotent upserts; sport/league; players; odds_snapshots; users/wallets/stakes)
  → Feature tables (single feature-builder; per-league rows; unplayed games from prior completed history)
  → Train / Validation / Test partitions **per league**
  → Select on validation per league → Test once → Publish artifacts + per-league pins
  → API reads (game_id, feature_version) + pin for game.league; optional Market P from odds_snapshots
  → Pipeline settle on Finished; board poll upserts in-progress (newest pages)
```

**Replay capability:** A historical transform must be reproducible from persisted raw data **without** another provider API call (ADR-006).

## Zones

| Zone | Medium | Rules |
|---|---|---|
| Raw | Filesystem volume | Immutable after write; new fetch = new batch path; store retrieval metadata in design |
| Curated | PostgreSQL | Natural keys `(league, provider_*)`; idempotent reload (DR-003). **Loaded:** teams, games, `team_game_stats`, `players`, `player_game_stats`, `odds_snapshots`, **users / wallets / ledger_entries / stakes** (CR-005). |
| Features | PostgreSQL (+ optional files) | Key `(game_id, feature_version)`; built by **one** shared feature module; `payload` JSONB envelope `{values, label_home_win, used_cold_start_*}` |
| Artifacts | Local volume | Models + lineage JSON; **per-league** selection pins (ADR-013) |

## Validation boundary

```text
Raw → Validate → valid records → transform/load
                 → invalid → validation report
                 → stop vs skip = `docs/06-design/error-handling.md` (skip+count; fail if zero teams/games for a required season)
```

## Versioning / lineage chain

```text
raw_batch_id → dataset_version → feature_version → training_run
  → model_version (+ code_commit, training_config) → API pin
```

## Idempotency / rerun semantics

Running the same pipeline twice against the same raw dataset must not create duplicate games, team statistics, feature records, or **double-credit settled stakes**.

## Related

ADR-001, ADR-011, ADR-003, ADR-004, ADR-006, ADR-008, ADR-010, **ADR-012**, **ADR-013**, **ADR-014**, **ADR-015**, **ADR-017**; **CR-001**, **CR-002**, **CR-004**, **CR-005**.
