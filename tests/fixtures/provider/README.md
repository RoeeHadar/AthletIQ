# Provider fixtures

`# Implements: FR-001, CON-007, DR-001, ADR-002, ADR-006, NFR-003`

Recorded API-Sports-shaped payloads for CI, unit ingest, and the Compose fixture demo (no live provider). Each season file has enough finished games for a temporal train split.

| File | Role |
|---|---|
| `teams.json` | Team list |
| `games_2023.json` | Games for season 2023 |
| `games_2024.json` | Games for season 2024 |

No `players.json` — MVP ingest is team/game only (**CR-001**).
