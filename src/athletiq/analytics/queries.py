# Implements: FR-003, NFR-005
"""Canonical SQL for curated Postgres analytics (indexes support join/order paths)."""

from __future__ import annotations

# Top scorers by season — uses player_game_stats + games (idx on season / player+game).
TOP_SCORERS_BY_SEASON_SQL = """
SELECT
    p.player_id,
    p.full_name,
    g.season,
    SUM(pgs.points) AS points
FROM player_game_stats pgs
JOIN games g ON g.game_id = pgs.game_id
JOIN players p ON p.player_id = pgs.player_id
WHERE g.season = %(season)s
  AND pgs.points IS NOT NULL
GROUP BY p.player_id, p.full_name, g.season
ORDER BY points DESC, p.full_name ASC
"""

# Rolling mean points_for over last N completed games before a cutoff tip
# (window ordered by game_start_time — idx_games_start).
ROLLING_TEAM_POINTS_SQL = """
WITH prior AS (
    SELECT
        tgs.team_id,
        tgs.points_for,
        g.game_start_time,
        ROW_NUMBER() OVER (
            PARTITION BY tgs.team_id
            ORDER BY g.game_start_time DESC
        ) AS rn
    FROM team_game_stats tgs
    JOIN games g ON g.game_id = tgs.game_id
    WHERE g.game_start_time < %(cutoff)s
      AND tgs.points_for IS NOT NULL
)
SELECT team_id, AVG(points_for)::float AS mean_points_for
FROM prior
WHERE rn <= %(window)s
GROUP BY team_id
ORDER BY team_id
"""
