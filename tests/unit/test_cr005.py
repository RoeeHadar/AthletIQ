# TEST-020 … TEST-028 (CR-005)
"""CR-005 ledger, slate, board, scheduled persist, mapper, fixtures, retrain protocol."""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from api.app.main import create_app
from api.app.state import AppState, InMemoryGameRepo
from fastapi.testclient import TestClient

from athletiq.features import FEATURE_VERSION, TeamGameHistory, build_feature_row
from athletiq.ingest import ingest_raw
from athletiq.ledger.memory import HOUSE_START, MemoryLedger
from athletiq.ledger.settle import settle_finished_on_store
from athletiq.load import load_raw_batch
from athletiq.ml.pipeline import run_train_select_publish
from athletiq.provider.fixture import FixtureProvider
from athletiq.provider.nba_stats import (
    NbaStatsApiProvider,
    to_player_game_stats,
    to_provider_game,
)
from athletiq.validate.parse import GameRecord, parse_game

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "api" / "static"
FIXTURES = ROOT / "tests" / "fixtures" / "provider"
FUTURE = datetime.now(timezone.utc) + timedelta(days=21)
PAST = datetime.now(timezone.utc) - timedelta(hours=1)


def _game(
    game_id: int,
    *,
    status: str = "scheduled",
    league: str = "nba",
    tip: datetime | None = None,
    home_score: int | None = None,
    away_score: int | None = None,
    clock: str | None = None,
) -> dict:
    row = {
        "game_id": game_id,
        "status": status,
        "league": league,
        "game_start_time": tip or FUTURE,
        "home_score": home_score,
        "away_score": away_score,
        "home_team_name": "Boston Celtics" if league == "nba" else "New York Liberty",
        "away_team_name": "Los Angeles Lakers" if league == "nba" else "Las Vegas Aces",
        "home_team_id": 1,
        "away_team_id": 2,
    }
    if clock:
        row["clock"] = clock
    return row


def _client(games: dict[int, dict] | None = None, ledger: MemoryLedger | None = None) -> TestClient:
    state = AppState(
        games=InMemoryGameRepo(games=games or {}),
        ledger=ledger or MemoryLedger(),
        db_ping=lambda: True,
    )
    return TestClient(create_app(state))


def test_scheduled_persist_and_features_from_prior_only(tmp_path: Path) -> None:
    """TEST-020"""
    batch = ingest_raw(
        FixtureProvider(FIXTURES),
        tmp_path / "raw",
        seasons=[2024, 2026],
        batch_id="t020",
    )
    store, _report = load_raw_batch(batch, required_seasons=[2024, 2026])
    scheduled = [g for g in store.iter_games() if g.record.status == "scheduled"]
    finished = [g for g in store.iter_games() if g.record.status == "Finished"]
    assert scheduled
    assert all(g.record.home_score is None and g.record.away_score is None for g in scheduled)
    assert all(g.record.status != "Finished" for g in scheduled)
    assert finished
    history: list[TeamGameHistory] = []
    for g in finished:
        rec = g.record
        history.append(
            TeamGameHistory(
                team_id=g.home_team_id,
                game_start_time=rec.game_start_time,
                won=bool(rec.home_win),
                points_for=int(rec.home_score or 0),
                points_against=int(rec.away_score or 0),
                season=rec.season,
            )
        )
    target = scheduled[0]
    row = build_feature_row(
        game_id=target.game_id,
        tip=target.record.game_start_time,
        season=target.record.season,
        home_team_id=target.home_team_id,
        away_team_id=target.away_team_id,
        history=history,
        label_home_win=None,
    )
    assert row.label_home_win is None
    assert target.game_id not in {h.game_start_time for h in history}


def test_even_money_settle_cancel_replace() -> None:
    """TEST-021"""
    ledger = MemoryLedger()
    tip = FUTURE
    assert ledger.balance("demo-1") == 1000
    stake = ledger.place_or_replace(
        slug="demo-1",
        game_id=7,
        side="home",
        amount=10,
        replace=False,
        scores_null=True,
        tip=tip,
    )
    assert ledger.balance("demo-1") == 990
    ledger.cancel(slug="demo-1", stake_id=stake["stake_id"], scores_null=True, tip=tip)
    assert ledger.balance("demo-1") == 1000

    ledger.place_or_replace(
        slug="demo-1",
        game_id=7,
        side="home",
        amount=10,
        replace=False,
        scores_null=True,
        tip=tip,
    )
    replaced = ledger.place_or_replace(
        slug="demo-1",
        game_id=7,
        side="home",
        amount=20,
        replace=True,
        scores_null=True,
        tip=tip,
    )
    assert ledger.balance("demo-1") == 980
    assert len(ledger.open_stakes("demo-1")) == 1
    assert replaced["amount"] == 20

    rec = GameRecord(
        provider_game_id="7",
        season=2026,
        game_start_time=tip,
        home_provider_team_id="1",
        away_provider_team_id="2",
        home_score=110,
        away_score=100,
        home_win=True,
        status="Finished",
    )
    store = SimpleNamespace(
        ledger=ledger,
        iter_games=lambda: [SimpleNamespace(game_id=7, record=rec)],
    )
    house_before = int(ledger.wallets["house"]["balance"])
    assert settle_finished_on_store(store) == 1
    assert ledger.balance("demo-1") == 1020
    assert int(ledger.wallets["house"]["balance"]) == house_before - 20
    assert settle_finished_on_store(store) == 0
    assert ledger.balance("demo-1") == 1020

    ledger.place_or_replace(
        slug="demo-2",
        game_id=8,
        side="home",
        amount=10,
        replace=False,
        scores_null=True,
        tip=tip,
    )
    lose = GameRecord(
        provider_game_id="8",
        season=2026,
        game_start_time=tip,
        home_provider_team_id="1",
        away_provider_team_id="2",
        home_score=90,
        away_score=100,
        home_win=False,
        status="Finished",
    )
    house_mid = int(ledger.wallets["house"]["balance"])
    store2 = SimpleNamespace(
        ledger=ledger,
        iter_games=lambda: [SimpleNamespace(game_id=8, record=lose)],
    )
    assert settle_finished_on_store(store2) == 1
    assert ledger.balance("demo-2") == 990
    assert int(ledger.wallets["house"]["balance"]) == house_mid

    games = {9: _game(9, tip=PAST)}
    client = _client(games, MemoryLedger())
    closed = client.post(
        "/v1/stakes",
        json={"user": "demo-1", "game_id": 9, "side": "home", "amount": 10},
    )
    assert closed.status_code == 400
    assert closed.json()["error"]["code"] == "stake_window_closed"

    display = _client({7: _game(7)}, MemoryLedger())
    first = display.get("/v1/slate", params={"user": "demo-1"}).json()
    second = display.get("/v1/slate", params={"user": "demo-1"}).json()
    assert first["balance"] == second["balance"] == 1000
    lowered = (closed.json()["error"]["message"]).lower()
    assert "odds" not in lowered and "juice" not in lowered and "moneyline" not in lowered


def test_integer_bounds_and_one_open_stake() -> None:
    """TEST-022"""
    ledger = MemoryLedger()
    assert ledger.balance("demo-1") == 1000
    assert ledger.balance("demo-2") == 1000
    assert int(ledger.wallets["house"]["balance"]) == HOUSE_START
    client = _client({1: _game(1)}, ledger)
    zero = client.post(
        "/v1/stakes",
        json={"user": "demo-1", "game_id": 1, "side": "home", "amount": 0},
    )
    assert zero.status_code == 400
    assert zero.json()["error"]["code"] in {"invalid_request", "insufficient_balance"}
    over = client.post(
        "/v1/stakes",
        json={"user": "demo-1", "game_id": 1, "side": "home", "amount": 1001},
    )
    assert over.status_code == 400
    assert over.json()["error"]["code"] == "insufficient_balance"
    ok = client.post(
        "/v1/stakes",
        json={"user": "demo-1", "game_id": 1, "side": "home", "amount": 10, "replace": False},
    )
    assert ok.status_code == 200
    dup = client.post(
        "/v1/stakes",
        json={"user": "demo-1", "game_id": 1, "side": "away", "amount": 5, "replace": False},
    )
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "duplicate_open_stake"
    house = client.get("/v1/users/house/wallet")
    assert house.status_code == 404
    assert house.json()["error"]["code"] == "user_not_found"
    unknown = client.get("/v1/users/demo-9/wallet")
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "user_not_found"


def test_slate_next_twenty_and_user_query() -> None:
    """TEST-023"""
    games = {}
    for i in range(1, 22):
        games[i] = _game(i, league="nba" if i % 2 else "wnba", tip=FUTURE + timedelta(hours=i))
    games[99] = _game(99, status="Finished", home_score=100, away_score=90, tip=PAST)
    ledger = MemoryLedger()
    ledger.place_or_replace(
        slug="demo-1",
        game_id=1,
        side="home",
        amount=15,
        replace=False,
        scores_null=True,
        tip=FUTURE + timedelta(hours=1),
    )
    client = _client(games, ledger)
    html = client.get("/slate", params={"user": "demo-1"})
    assert html.status_code == 200
    assert "text/html" in html.headers.get("content-type", "")
    assert "/slate?user=demo-2" in html.text
    body = client.get("/v1/slate", params={"user": "demo-1"}).json()
    assert len(body["upcoming"]) == 20
    assert 99 not in {row["game_id"] for row in body["upcoming"]}
    assert body["balance"] == 985
    assert len(body["open_stakes"]) == 1
    other = client.get("/v1/slate", params={"user": "demo-2"}).json()
    assert other["balance"] == 1000
    assert other["open_stakes"] == []


def test_board_in_progress_gamecast_has_no_clock() -> None:
    """TEST-024"""
    client = _client(
        {
            1: _game(1, status="in_progress", home_score=22, away_score=18, clock="Q2 4:11"),
            2: _game(2, status="scheduled"),
        }
    )
    html = client.get("/board")
    assert html.status_code == 200
    assert "text/html" in html.headers.get("content-type", "")
    board = client.get("/v1/board").json()
    assert len(board["games"]) == 1
    assert board["games"][0]["home_score"] == 22
    assert board["games"][0]["clock"] == "Q2 4:11"
    empty = _client({2: _game(2, status="scheduled")})
    assert empty.get("/v1/board").json()["games"] == []
    gamecast = (STATIC / "index.html").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert 'id="clock"' not in gamecast
    assert "quarter" not in (gamecast + js).lower()
    assert "clock" not in js.lower()


def test_nba_stats_injected_null_in_progress_boxes_and_newest_pages() -> None:
    """TEST-025"""
    scheduled = to_provider_game(
        {
            "gameId": "202610220BOS",
            "date": "2026-10-22T23:00:00.000Z",
            "homeTeam": "BOS",
            "visitorTeam": "LAL",
            "homePts": None,
            "visitorPts": None,
        }
    )
    assert scheduled is not None
    parsed = parse_game(scheduled)
    assert not isinstance(parsed, str)
    assert parsed.home_score is None
    assert parsed.status != "Finished"
    live = to_provider_game(
        {
            "gameId": "202610220NYK",
            "date": "2026-10-22T23:00:00.000Z",
            "homeTeam": "NYK",
            "visitorTeam": "BOS",
            "homePts": 33,
            "visitorPts": 29,
            "gameStatusText": "Q2 3:12",
            "playerGameBasicStats": [
                {
                    "playerId": 99,
                    "playerName": "Jayson Tatum",
                    "teamTricode": "BOS",
                    "pts": 12,
                    "min": "12:00",
                }
            ],
        }
    )
    assert live is not None
    assert live["status"] == "in_progress"
    boxes = to_player_game_stats(live)
    assert boxes and boxes[0]["points"] == 12
    calls: list[str] = []

    def get_json(url: str) -> dict:
        calls.append(url)
        return {
            "data": [
                {
                    "gameId": "202610220BOS",
                    "date": "2026-10-22T23:00:00.000Z",
                    "homeTeam": "BOS",
                    "visitorTeam": "LAL",
                    "homePts": None,
                    "visitorPts": None,
                }
            ],
            "pagination": {"page": 1, "pages": 50},
        }

    provider = NbaStatsApiProvider(get_json=get_json, pause_seconds=0)
    mapped = provider.fetch_newest_pages(pages=1)
    assert len(mapped) == 1
    assert len(calls) == 1
    assert "include=playerGameBasicStats" in calls[0]


def test_wnba_fixture_window_2021_to_2026() -> None:
    """TEST-026"""
    provider = FixtureProvider(FIXTURES)
    assert provider.available_seasons("wnba") == [2021, 2022, 2023, 2024, 2025, 2026]
    for year in (2021, 2022, 2023, 2024, 2025):
        games = provider.fetch_games(year, league="wnba")
        assert games
        assert all(g.get("status") == "Finished" for g in games)
    scheduled = provider.fetch_games(2026, league="wnba")
    assert scheduled
    assert all(g.get("status") == "scheduled" for g in scheduled)
    assert all(g["scores"]["home"]["total"] is None for g in scheduled)
    nba_sched = provider.fetch_games(2026, league="nba")
    assert nba_sched
    assert all(g.get("status") == "scheduled" for g in nba_sched)


def test_retrain_protocol_ci_pin_unchanged() -> None:
    """TEST-027"""
    assert FEATURE_VERSION == "team_l5_l10_player_agg_v1"
    source = inspect.getsource(run_train_select_publish)
    assert "selection_used_test = False" in source
    assert "val_scores" in source
    assert "0.623" not in source


def test_producer_bar_three_way_links_and_copy() -> None:
    """TEST-028"""
    client = TestClient(create_app(AppState()))
    home = client.get("/").text
    slate = client.get("/slate").text
    board = client.get("/board").text
    assert 'href="/slate"' in home and 'href="/board"' in home
    assert 'href="/"' in slate and 'href="/board"' in slate
    assert 'href="/"' in board and 'href="/slate"' in board
    for blob, allow_stake in ((home, False), (slate, True), (board, False)):
        lowered = blob.lower()
        for word in ("odds", "juice", "moneyline", "payout", "wager"):
            assert word not in lowered
        if allow_stake:
            assert "stake" in lowered
        else:
            if blob is home:
                assert "stake" not in lowered
    js = (STATIC / "app.js").read_text(encoding="utf-8").lower()
    assert "stake" not in js
