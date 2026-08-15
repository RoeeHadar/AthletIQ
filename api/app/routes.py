# Implements: FR-009, FR-010, FR-014, FR-018, FR-019, CON-004, ADR-009, NFR-002, NFR-004
"""HTTP routes under /v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request

from api.app.errors import ApiError
from api.app.methodology import MODEL_CARD_REF, model_disclosure
from api.app.state import predict_home_win

router = APIRouter(prefix="/v1")


def _state(request: Request):
    return request.app.state.athletiq


@router.get("/health")
def health(request: Request):
    state = _state(request)
    if not state.db_ok():
        raise ApiError(503, "db_unavailable", "database unreachable")
    try:
        state.require_model()
    except ApiError:
        raise ApiError(503, "model_unavailable", "selected model pin/artifact missing")
    return {"status": "ok"}


@router.get("/model")
def model_info(request: Request, league: Annotated[str | None, Query()] = None):
    state = _state(request)
    loaded = state.require_model(league)
    body = model_disclosure(
        model_version=loaded.model_version,
        feature_version=loaded.feature_version,
        dataset_version=loaded.dataset_version,
        metrics=loaded.metadata.get("metrics"),
    )
    body["league"] = (league or getattr(state, "_default_league", None) or "nba")
    return body


@router.get("/predict")
def predict(
    request: Request,
    game_id: Annotated[str | None, Query()] = None,
    provider_game_id: Annotated[str | None, Query()] = None,
):
    state = _state(request)
    if game_id is None and provider_game_id is None:
        raise ApiError(400, "invalid_request", "game_id or provider_game_id required")

    resolved: int | None = None
    if game_id is not None:
        try:
            resolved = int(game_id)
        except ValueError as exc:
            raise ApiError(
                400,
                "invalid_request",
                "game_id must be an integer string",
                {"game_id": game_id},
            ) from exc
    elif provider_game_id is not None:
        if state.games is None:
            raise ApiError(503, "db_unavailable", "database unreachable")
        resolved = state.games.resolve_provider_game_id(provider_game_id)
        if resolved is None:
            raise ApiError(
                404,
                "game_not_found",
                "unknown provider_game_id",
                {"provider_game_id": provider_game_id},
            )

    assert resolved is not None
    result = predict_home_win(state, resolved)
    # FR-010: predictions point at methodology disclosure.
    result["limitations_ref"] = result.get("limitations_ref") or "/v1/model"
    result.setdefault("model_card_ref", MODEL_CARD_REF)
    return result
