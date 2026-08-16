# Implements: FR-009, FR-014, FR-018, FR-019, FR-020, ADR-008, ADR-003, ADR-012, ADR-013
"""Runtime state: pin, model, feature/game lookups."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

import joblib
import numpy as np

from athletiq.features import FEATURE_VERSION, FeatureRow, preprocess_for_model
from athletiq.ml.train import predict_proba_positive


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class GameRepo(Protocol):
    def get_game(self, game_id: int) -> dict[str, Any] | None: ...

    def resolve_provider_game_id(self, provider_game_id: str) -> int | None: ...


class FeatureRepo(Protocol):
    def get_features(self, game_id: int, feature_version: str) -> FeatureRow | None: ...


@dataclass
class InMemoryGameRepo:
    games: dict[int, dict[str, Any]] = field(default_factory=dict)
    by_provider: dict[str, int] = field(default_factory=dict)
    odds: dict[int, float] = field(default_factory=dict)

    def get_game(self, game_id: int) -> dict[str, Any] | None:
        return self.games.get(game_id)

    def resolve_provider_game_id(self, provider_game_id: str) -> int | None:
        return self.by_provider.get(provider_game_id)

    def latest_synthetic_odds(self, game_id: int) -> float | None:
        if game_id not in self.odds:
            return None
        return float(self.odds[game_id])


@dataclass
class InMemoryFeatureRepo:
    rows: dict[tuple[int, str], FeatureRow] = field(default_factory=dict)

    def get_features(self, game_id: int, feature_version: str) -> FeatureRow | None:
        return self.rows.get((game_id, feature_version))


@dataclass
class LoadedModel:
    model_version: str
    feature_version: str
    dataset_version: str | None
    metadata: dict[str, Any]
    model: Any
    artifact_name: str


@dataclass
class AppState:
    artifacts_dir: Path | None = None
    games: GameRepo | None = None
    features: FeatureRepo | None = None
    db_ping: Callable[[], bool] | None = None
    _loaded: LoadedModel | None = None
    _models: dict[str, LoadedModel] = field(default_factory=dict)
    _default_league: str = "nba"
    _pin_v2: bool = False

    def _load_entry(self, pin: dict[str, Any]) -> LoadedModel | None:
        assert self.artifacts_dir is not None
        meta_name = pin.get("metadata") or f"{pin['model_version']}.json"
        art_name = pin.get("artifact") or f"{pin['model_version']}.joblib"
        meta_path = self.artifacts_dir / meta_name
        art_path = self.artifacts_dir / art_name
        if not meta_path.is_file() or not art_path.is_file():
            return None
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        model = joblib.load(art_path)
        return LoadedModel(
            model_version=str(pin["model_version"]),
            feature_version=str(
                pin.get("feature_version") or metadata.get("feature_version") or FEATURE_VERSION
            ),
            dataset_version=metadata.get("dataset_version"),
            metadata=metadata,
            model=model,
            artifact_name=art_name,
        )

    def load_pin(self) -> LoadedModel | None:
        if self.artifacts_dir is None:
            return None
        pin_path = self.artifacts_dir / "selected_pin.json"
        if not pin_path.is_file():
            return None
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        self._models = {}
        self._pin_v2 = "pins" in pin
        if self._pin_v2:
            self._default_league = str(pin.get("default_league") or "nba")
            for league, entry in pin["pins"].items():
                loaded = self._load_entry(entry)
                if loaded is not None:
                    self._models[str(league)] = loaded
            self._loaded = self._models.get(self._default_league) or next(
                iter(self._models.values()), None
            )
            return self._loaded
        loaded = self._load_entry(pin)
        if loaded is not None:
            self._models["nba"] = loaded
        self._loaded = loaded
        self._default_league = "nba"
        return loaded

    def require_model(self, league: str | None = None) -> LoadedModel:
        from api.app.errors import ApiError

        if not self._models:
            self.load_pin()
        lg = (league or self._default_league or "nba").lower()
        loaded = self._models.get(lg)
        if loaded is None and lg == "nba" and not self._pin_v2:
            loaded = self._loaded
        if loaded is None:
            raise ApiError(
                503,
                "model_unavailable",
                "selected model pin/artifact missing",
                {"league": lg},
            )
        return loaded

    def db_ok(self) -> bool:
        if self.db_ping is None:
            return self.games is not None and self.features is not None
        try:
            return bool(self.db_ping())
        except Exception:
            return False


def predict_home_win(state: AppState, game_id: int) -> dict[str, Any]:
    from api.app.errors import ApiError

    if not state.db_ok():
        raise ApiError(503, "db_unavailable", "database unreachable")

    assert state.games is not None and state.features is not None

    game = state.games.get_game(game_id)
    if game is None:
        raise ApiError(
            404,
            "game_not_found",
            "unknown game_id",
            {"game_id": str(game_id)},
        )

    league = str(game.get("league") or "nba").lower()
    loaded = state.require_model(league)

    row = state.features.get_features(game_id, loaded.feature_version)
    if row is None:
        raise ApiError(
            404,
            "features_not_found",
            "no feature row for pinned feature_version",
            {
                "game_id": str(game_id),
                "feature_version": loaded.feature_version,
            },
        )

    vector = preprocess_for_model(row, feature_version=loaded.feature_version)
    X = np.asarray([vector], dtype=float)
    p = float(predict_proba_positive(loaded.model, X)[0])

    market_p = None
    market_source = None
    lookup = getattr(state.games, "latest_synthetic_odds", None)
    if lookup is not None:
        market_p = lookup(game_id)
        if market_p is not None:
            market_source = "synthetic"

    return {
        "game_id": str(game_id),
        "home_team_id": str(game.get("home_team_id", "")),
        "away_team_id": str(game.get("away_team_id", "")),
        "home_team_name": _optional_text(game.get("home_team_name")),
        "home_team_abbreviation": _optional_text(game.get("home_team_abbreviation")),
        "away_team_name": _optional_text(game.get("away_team_name")),
        "away_team_abbreviation": _optional_text(game.get("away_team_abbreviation")),
        "league": league,
        "home_win_pred": p >= 0.5,
        "p_home_win": p,
        "market_p_home_win": market_p,
        "market_source": market_source,
        "model_version": loaded.model_version,
        "feature_version": loaded.feature_version,
        "dataset_version": loaded.dataset_version,
        "limitations_ref": "/v1/model",
    }
