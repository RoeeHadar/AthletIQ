# Implements: FR-002, FR-017, FR-018, DR-003, CON-002, CR-004
"""Curated store protocols and in-memory implementation for tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from athletiq.validate.parse import (
    GameRecord,
    OddsSnapshotRecord,
    PlayerGameStatRecord,
    PlayerRecord,
    TeamRecord,
)


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
class StoredPlayer:
    player_id: int
    record: PlayerRecord
    team_id: int | None


def _team_key(team: TeamRecord) -> tuple[str, str]:
    return (team.league, team.provider_team_id)


def _game_key(game: GameRecord) -> tuple[str, str]:
    return (game.league, game.provider_game_id)


def _player_key(player: PlayerRecord) -> tuple[str, str]:
    return (player.league, player.provider_player_id)


class CuratedStore(Protocol):
    def upsert_team(self, team: TeamRecord) -> int:
        """Upsert by (league, provider_team_id); return internal team_id."""

    def upsert_game(self, game: GameRecord, home_team_id: int, away_team_id: int) -> int:
        """Upsert by (league, provider_game_id); return internal game_id."""

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

    def upsert_player(self, player: PlayerRecord, team_id: int | None) -> int: ...

    def upsert_player_game_stats(
        self,
        *,
        game_id: int,
        player_id: int,
        team_id: int,
        stat: PlayerGameStatRecord,
    ) -> None: ...

    def upsert_odds_snapshot(self, game_id: int, snap: OddsSnapshotRecord) -> None: ...

    def count_teams(self) -> int: ...

    def count_games(self, season: int | None = None) -> int: ...

    def count_team_game_stats(self) -> int: ...

    def iter_games(self) -> list[StoredGame]:
        """Return curated games for feature build (pipeline consumer)."""

    def team_stat(self, game_id: int, team_id: int) -> dict | None:
        """Return team_game_stats grain or None."""

    def iter_player_game_stats(self) -> list[dict]:
        """Player box-score rows with internal ids + tip via game join in caller."""


@dataclass
class InMemoryCuratedStore:
    """Deterministic store for TEST-004 without Postgres."""

    _teams_by_provider: dict[tuple[str, str], StoredTeam] = field(default_factory=dict)
    _games_by_provider: dict[tuple[str, str], StoredGame] = field(default_factory=dict)
    _players_by_provider: dict[tuple[str, str], StoredPlayer] = field(default_factory=dict)
    _team_stats: dict[tuple[int, int], dict] = field(default_factory=dict)
    _player_stats: dict[tuple[int, int], dict] = field(default_factory=dict)
    _odds: dict[tuple[int, str, str], dict] = field(default_factory=dict)
    _next_team_id: int = 1
    _next_game_id: int = 1
    _next_player_id: int = 1

    def upsert_team(self, team: TeamRecord) -> int:
        key = _team_key(team)
        existing = self._teams_by_provider.get(key)
        if existing:
            existing.record = team
            return existing.team_id
        tid = self._next_team_id
        self._next_team_id += 1
        self._teams_by_provider[key] = StoredTeam(tid, team)
        return tid

    def upsert_game(self, game: GameRecord, home_team_id: int, away_team_id: int) -> int:
        key = _game_key(game)
        existing = self._games_by_provider.get(key)
        if existing:
            existing.record = game
            existing.home_team_id = home_team_id
            existing.away_team_id = away_team_id
            return existing.game_id
        gid = self._next_game_id
        self._next_game_id += 1
        self._games_by_provider[key] = StoredGame(gid, game, home_team_id, away_team_id)
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

    def upsert_player(self, player: PlayerRecord, team_id: int | None) -> int:
        key = _player_key(player)
        existing = self._players_by_provider.get(key)
        if existing:
            existing.record = player
            existing.team_id = team_id
            return existing.player_id
        pid = self._next_player_id
        self._next_player_id += 1
        self._players_by_provider[key] = StoredPlayer(pid, player, team_id)
        return pid

    def upsert_player_game_stats(
        self,
        *,
        game_id: int,
        player_id: int,
        team_id: int,
        stat: PlayerGameStatRecord,
    ) -> None:
        self._player_stats[(game_id, player_id)] = {
            "game_id": game_id,
            "player_id": player_id,
            "team_id": team_id,
            "minutes": stat.minutes,
            "points": stat.points,
        }

    def upsert_odds_snapshot(self, game_id: int, snap: OddsSnapshotRecord) -> None:
        key = (game_id, snap.source, snap.captured_at.isoformat())
        self._odds[key] = {
            "game_id": game_id,
            "source": snap.source,
            "captured_at": snap.captured_at,
            "implied_p_home_win": snap.implied_p_home_win,
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
        return [self._games_by_provider[k] for k in sorted(self._games_by_provider)]

    def team_stat(self, game_id: int, team_id: int) -> dict | None:
        return self._team_stats.get((game_id, team_id))

    def iter_player_game_stats(self) -> list[dict]:
        return list(self._player_stats.values())

    def latest_synthetic_odds(self, game_id: int) -> float | None:
        rows = [v for v in self._odds.values() if v["game_id"] == game_id and v["source"] == "synthetic"]
        if not rows:
            return None
        rows.sort(key=lambda r: r["captured_at"])
        return float(rows[-1]["implied_p_home_win"])

    def get_team_internal(self, league: str, provider_team_id: str) -> int | None:
        stored = self._teams_by_provider.get((league, provider_team_id))
        return stored.team_id if stored else None

    def get_game_internal(self, league: str, provider_game_id: str) -> int | None:
        stored = self._games_by_provider.get((league, provider_game_id))
        return stored.game_id if stored else None

    def get_player_internal(self, league: str, provider_player_id: str) -> int | None:
        stored = self._players_by_provider.get((league, provider_player_id))
        return stored.player_id if stored else None
