# Provider fixtures

`# Implements: FR-001, CON-007, DR-001, ADR-006, NFR-003, CR-004`

Recorded payloads for CI, unit ingest, and the Compose fixture demo (no live provider).

| File | Role |
|---|---|
| `teams.json` | NBA + WNBA teams (`league` field) |
| `games_2022.json` / `games_2023.json` / `games_2024.json` | NBA completed games |
| `games_2026.json` | NBA scheduled (null scores, future tip) |
| `games_wnba_2021.json` … `games_wnba_2025.json` | WNBA completed (small authored seasons) |
| `games_wnba_2026.json` | WNBA scheduled (null scores) |
| `players.json` | Players for fixture box scores |
| `player_game_stats.json` | Per-game minutes/points |
| `odds_snapshots.json` | Labeled synthetic Market P (`source=synthetic`) |

Live `--provider nba-stats` remains NBA only (no WNBA HTTP). Live NBA boxes come from the same host; CI/WNBA boxes stay in these files.
