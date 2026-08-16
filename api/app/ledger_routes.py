# Implements: FR-022, FR-023, FR-024, FR-025, ADR-009, ADR-014, ADR-016, CR-005
"""Slate / board / wallet / stake JSON. Display only — settle is pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Body, Query, Request

from api.app.errors import ApiError
from athletiq.ledger.errors import LedgerError

router = APIRouter(prefix="/v1")

_LEDGER_HTTP = {
    "invalid_request": 400,
    "insufficient_balance": 400,
    "stake_window_closed": 400,
    "user_not_found": 404,
    "duplicate_open_stake": 409,
}


def _state(request: Request):
    return request.app.state.athletiq


def _raise_ledger(exc: LedgerError) -> None:
    raise ApiError(
        _LEDGER_HTTP.get(exc.code, 400),
        exc.code,
        exc.message,
        exc.details,
    ) from exc


def _require_ledger(state) -> Any:
    ledger = getattr(state, "ledger", None)
    if ledger is None:
        raise ApiError(503, "db_unavailable", "database unreachable")
    return ledger


def _as_dt(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    try:
        tip = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    if tip.tzinfo is None:
        tip = tip.replace(tzinfo=timezone.utc)
    return tip


def _jsonish(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        elif key in {"game_id", "stake_id", "user_id", "amount", "home_score", "away_score"} and value is not None:
            out[key] = int(value)
        else:
            out[key] = value
    if "clock" in out and not out["clock"]:
        out.pop("clock", None)
    return out


def _window(game: dict[str, Any]) -> tuple[bool, datetime]:
    scores_null = game.get("home_score") is None and game.get("away_score") is None
    tip = _as_dt(game.get("game_start_time"))
    if tip is None:
        raise ApiError(400, "invalid_request", "game is missing a start time")
    return scores_null, tip


@router.get("/slate")
def get_slate(request: Request, user: Annotated[str, Query()] = "demo-1"):
    state = _state(request)
    ledger = _require_ledger(state)
    try:
        balance = ledger.balance(user)
        open_stakes = ledger.open_stakes(user)
    except LedgerError as exc:
        _raise_ledger(exc)
    upcoming: list[dict[str, Any]] = []
    if state.games is not None:
        upcoming = list(state.games.list_upcoming(limit=20))
    return {
        "user": user,
        "balance": int(balance),
        "upcoming": [_jsonish(dict(g)) for g in upcoming],
        "open_stakes": [_jsonish(dict(s)) for s in open_stakes],
    }


@router.get("/board")
def get_board(request: Request):
    state = _state(request)
    if state.games is None:
        raise ApiError(503, "db_unavailable", "database unreachable")
    rows = list(state.games.list_in_progress())
    games = []
    for row in rows:
        item = _jsonish(dict(row))
        if not item.get("clock"):
            item.pop("clock", None)
        games.append(item)
    return {"games": games}


@router.get("/users/{slug}/wallet")
def get_wallet(request: Request, slug: str):
    ledger = _require_ledger(_state(request))
    try:
        return {"user": slug, "balance": int(ledger.balance(slug))}
    except LedgerError as exc:
        _raise_ledger(exc)


@router.post("/stakes")
def place_stake(request: Request, body: dict[str, Any]):
    state = _state(request)
    ledger = _require_ledger(state)
    if state.games is None:
        raise ApiError(503, "db_unavailable", "database unreachable")
    slug = str(body.get("user") or "")
    side = str(body.get("side") or "")
    replace = bool(body.get("replace") or False)
    try:
        game_id = int(body["game_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiError(400, "invalid_request", "game_id must be an integer") from exc
    amount = body.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ApiError(400, "invalid_request", "amount must be a positive integer")
    game = state.games.get_game(game_id)
    if game is None:
        raise ApiError(404, "game_not_found", "unknown game_id", {"game_id": str(game_id)})
    scores_null, tip = _window(game)
    try:
        stake = ledger.place_or_replace(
            slug=slug,
            game_id=game_id,
            side=side,
            amount=amount,
            replace=replace,
            scores_null=scores_null,
            tip=tip,
        )
    except LedgerError as exc:
        _raise_ledger(exc)
    return _jsonish(dict(stake) | {"user": slug})


@router.post("/stakes/{stake_id}/cancel")
def cancel_stake(
    request: Request,
    stake_id: int,
    body: dict[str, Any] = Body(default_factory=dict),
):
    state = _state(request)
    ledger = _require_ledger(state)
    if state.games is None:
        raise ApiError(503, "db_unavailable", "database unreachable")
    payload = body or {}
    slug = str(payload.get("user") or "")
    try:
        identity = ledger.require_user(slug)
    except LedgerError as exc:
        _raise_ledger(exc)
    user_id = identity["user_id"] if isinstance(identity, dict) else identity
    getter = getattr(ledger, "get_stake", None)
    stake = getter(int(stake_id)) if callable(getter) else None
    if stake is None or int(stake.get("user_id")) != int(user_id):
        raise ApiError(400, "invalid_request", "unknown stake")
    game = state.games.get_game(int(stake["game_id"]))
    if game is None:
        raise ApiError(404, "game_not_found", "unknown game_id", {"game_id": str(stake["game_id"])})
    scores_null, tip = _window(game)
    try:
        canceled = ledger.cancel(
            slug=slug,
            stake_id=int(stake_id),
            scores_null=scores_null,
            tip=tip,
        )
    except LedgerError as exc:
        _raise_ledger(exc)
    return _jsonish(dict(canceled) | {"user": slug})
