# TEST-005
"""TEST-005 — exact analytics aggregates on mini fixtures."""

from __future__ import annotations

from datetime import datetime, timezone

from athletiq.analytics import (
    ROLLING_TEAM_POINTS_SQL,
    TOP_SCORERS_BY_SEASON_SQL,
    PlayerGameLine,
    rolling_team_points_last_n,
    top_scorers_by_season,
)
from athletiq.analytics.memory import TeamGameLine


def test_sql_templates_present() -> None:
    assert "SUM(pgs.points)" in TOP_SCORERS_BY_SEASON_SQL
    assert "ROW_NUMBER()" in ROLLING_TEAM_POINTS_SQL
    assert "game_start_time" in ROLLING_TEAM_POINTS_SQL


def test_top_scorers_exact_order_and_totals() -> None:
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2024, 1, 2, tzinfo=timezone.utc)
    lines = [
        PlayerGameLine(1, "Alice", 2024, 20, t0),
        PlayerGameLine(1, "Alice", 2024, 15, t1),
        PlayerGameLine(2, "Bob", 2024, 30, t0),
        PlayerGameLine(3, "Carol", 2024, 30, t1),
        PlayerGameLine(2, "Bob", 2023, 50, t0),  # other season
    ]
    rows = top_scorers_by_season(lines, 2024)
    # Bob 30, Carol 30 → name ASC; Alice 35
    assert rows == [
        (1, "Alice", 2024, 35),
        (2, "Bob", 2024, 30),
        (3, "Carol", 2024, 30),
    ]


def test_rolling_window_exact_membership() -> None:
    cutoff = datetime(2024, 1, 10, tzinfo=timezone.utc)
    lines = [
        TeamGameLine(1, 100, datetime(2024, 1, 1, tzinfo=timezone.utc)),
        TeamGameLine(1, 110, datetime(2024, 1, 5, tzinfo=timezone.utc)),
        TeamGameLine(1, 120, datetime(2024, 1, 9, tzinfo=timezone.utc)),
        TeamGameLine(1, 999, datetime(2024, 1, 11, tzinfo=timezone.utc)),  # after cutoff
        TeamGameLine(2, 80, datetime(2024, 1, 8, tzinfo=timezone.utc)),
    ]
    means = rolling_team_points_last_n(lines, cutoff=cutoff, window=2)
    # team 1: last 2 before cutoff = 120, 110 → 115
    assert means[1] == 115.0
    assert means[2] == 80.0
    assert 999 not in {lines[3].points_for} or means[1] != 999
