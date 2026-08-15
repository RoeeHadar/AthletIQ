# Provider fixtures

`# Implements: FR-001, CON-007, DR-001, ADR-006, NFR-003, CR-004`

Recorded payloads for CI, unit ingest, and the Compose fixture demo (no live provider).

| File | Role |
|---|---|
| `teams.json` | NBA + WNBA teams (`league` field) |
| `games_2022.json` / `games_2023.json` / `games_2024.json` | NBA games |
| `games_wnba_2023.json` / `games_wnba_2024.json` | WNBA games (overlapping window) |
| `players.json` | Players for fixture box scores |
| `player_game_stats.json` | Per-game minutes/points |
| `odds_snapshots.json` | Labeled synthetic Market P (`source=synthetic`) |

Live `--provider nba-stats` remains NBA games/teams only (no WNBA HTTP, no box scores).
