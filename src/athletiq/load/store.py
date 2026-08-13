# Implements: FR-002, DR-003, CON-002
"""Curated store protocols and in-memory implementation for tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from athletiq.validate.parse import GameRecord, TeamRecord


@dataclass
class StoredTeam:
    team_id: int
    record: TeamRecord


@dataclass
class StoredGame:
    game_id: int
    record: GameRecord
    home_team_id: int
    away_team_id: int


@dataclass
class TeamGameStatKey:
    game_id: int
    team_id: int


class CuratedStore(Protocol):
    def upsert_team(self, team: TeamRecord) -> int:
        """Upsert by provider_team_id; return internal team_id."""

    def upsert_game(self, game: GameRecord, home_team_id: int, away_team_id: int) -> int:
        """Upsert by provider_game_id; return internal game_id."""

    def upsert_team_game_stats(
        self,
        *,
        game_id: int,
        team_id: int,
        is_home: bool,
        points_for: int | None,
        points_against: int | None,
    ) -> None:
        """Upsert grain (game_id, team_id)."""

    def count_teams(self) -> int: ...

    def count_games(self, season: int | None = None) -> int: ...

    def count_team_game_stats(self) -> int: ...

    def iter_games(self) -> list[StoredGame]:
        """Return curated games for feature build (pipeline consumer)."""

    def team_stat(self, game_id: int, team_id: int) -> dict | None:
        """Return team_game_stats grain or None."""


@dataclass
class InMemoryCuratedStore:
    """Deterministic store for TEST-004 without Postgres."""

    _teams_by_provider: dict[str, StoredTeam] = field(default_factory=dict)
    _games_by_provider: dict[str, StoredGame] = field(default_factory=dict)
    _team_stats: dict[tuple[int, int], dict] = field(default_factory=dict)
    _next_team_id: int = 1
    _next_game_id: int = 1

    def upsert_team(self, team: TeamRecord) -> int:
        existing = self._teams_by_provider.get(team.provider_team_id)
        if existing:
            existing.record = team
            return existing.team_id
        tid = self._next_team_id
        self._next_team_id += 1
        self._teams_by_provider[team.provider_team_id] = StoredTeam(tid, team)
        return tid

    def upsert_game(self, game: GameRecord, home_team_id: int, away_team_id: int) -> int:
        existing = self._games_by_provider.get(game.provider_game_id)
        if existing:
            existing.record = game
            existing.home_team_id = home_team_id
            existing.away_team_id = away_team_id
            return existing.game_id
        gid = self._next_game_id
        self._next_game_id += 1
        self._games_by_provider[game.provider_game_id] = StoredGame(
            gid, game, home_team_id, away_team_id
        )
        return gid

    def upsert_team_game_stats(
        self,
        *,
        game_id: int,
        team_id: int,
        is_home: bool,
        points_for: int | None,
        points_against: int | None,
    ) -> None:
        self._team_stats[(game_id, team_id)] = {
            "is_home": is_home,
            "points_for": points_for,
            "points_against": points_against,
        }

    def count_teams(self) -> int:
        return len(self._teams_by_provider)

    def count_games(self, season: int | None = None) -> int:
        if season is None:
            return len(self._games_by_provider)
        return sum(1 for g in self._games_by_provider.values() if g.record.season == season)

    def count_team_game_stats(self) -> int:
        return len(self._team_stats)

    def iter_games(self) -> list[StoredGame]:
        """Return curated games (stable provider-key order)."""
        return [self._games_by_provider[k] for k in sorted(self._games_by_provider)]

    def team_stat(self, game_id: int, team_id: int) -> dict | None:
        return self._team_stats.get((game_id, team_id))
