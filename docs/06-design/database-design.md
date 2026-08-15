# Database design

Status: Approved  
Owner: Project owner  
Last Updated: 2026-08-15  
Version: 1.1.0

> Design intent. Contract: `database/schema.sql`. PostgreSQL (ADR-001). Raw landing is **filesystem** (**ADR-006**), not Postgres staging.  
> **CR-004:** load path writes teams / games / `team_game_stats` / `players` / `player_game_stats` / `odds_snapshots` / features. `sport`/`league` on teams and games. CR-001 reserved-empty expectation is superseded for the fixture path.

## NFRs cited

- **NFR-004** — no hard DB latency SLO in MVP  
- **NFR-005** — indexes for local analytics/feature access paths  

## Principles

- Natural keys: `provider_*`  
- Idempotent upserts (DR-003) on **MVP** grains  
- Active history window **3** completed NBA seasons + overlapping WNBA (DR-001); prune older  
- **Curated schema only** — raw JSON on volume (ADR-006), not `raw_*` tables  

## Identity types (**ADR-010**)

| Id | Type | Notes |
|---|---|---|
| `game_id`, `team_id`, `player_id` | **BIGINT** (`BIGSERIAL`) | API exposes as decimal string; **not** UUID (**ADR-010**; inference key semantics still ADR-008) |

> Older sketches mentioning UUID/serial are **superseded**. Design, contract (`schema.sql`), IMP-002, and TEST-002 must agree on BIGINT.

## Logical schema

| Table | MVP role |
|---|---|
| `teams`, `games`, `team_game_stats` | Loaded; `sport` TEXT default `basketball`; `league` TEXT (`nba`\|`wnba`). Natural key `(league, provider_*_id)`. |
| `features` | Written by feature builder; JSONB **envelope** (below) |
| `players`, `player_game_stats` | **Loaded** on fixture path (CR-004). Empty after live nba-stats-only ingest is expected. |
| `odds_snapshots` | Synthetic implied P(home) (ADR-012). Grain `(game_id, source, captured_at)`. |
| `model_registry` | Optional mirror; **files** (pins + joblib + JSON) remain canonical lineage (ADR-004). |
| `schema_migrations` | Migrate-runner bookkeeping. |

### `games`

`game_id BIGSERIAL PK`, `provider_game_id`, `league`, `sport`, unique `(league, provider_game_id)`, `season`, `game_start_time`, FKs, scores, `home_win`, `status`.

### `features.payload` envelope

JSONB object (not a bare feature-key map):

```json
{
  "values": { "<feature_name>": <float>, "...": "..." },
  "label_home_win": true,
  "used_cold_start_home": false,
  "used_cold_start_away": false
}
```

Readers must accept a legacy bare map (`values` missing → treat the object as `values`) for older rows. Writers use the envelope.

## Index strategy (NFR-005)

| Index | Purpose |
|---|---|
| `games (game_start_time)` | Temporal splits, ordered history |
| `games (season)` | Season filters / prune |
| `team_game_stats (team_id, game_id)` | Per-team history joins (**MVP** analytics/features) |
| `player_game_stats (player_id, game_id)` | Reserved per-player history / top scorers |
| `player_game_stats (team_id, game_id)` | Reserved team roster lines |
| `features (feature_version, game_id)` | Predict lookup by pin version |
| `games (league)` | Pin routing / UI filter |
| `odds_snapshots (game_id)` | Market P lookup |

Rolling averages: join `team_game_stats` → `games.game_start_time` and order by time. Window performance is best-effort local (NFR-004).

## Analytics examples

- **CR-004 Must:** aggregations and rolling windows over **team** stats ordered by `game_start_time`; player stats feed **aggregated** features only.

## Migrations

Forward-only under `database/migrations/` at implementation; `schema.sql` is the consolidated snapshot including `schema_migrations`.
