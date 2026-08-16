# Implements: FR-023, DR-003, ADR-015, CR-005
"""Pipeline settle: Finished games credit/debit e-coin wallets (idempotent)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("athletiq.ledger")


def settle_finished_on_store(store: Any) -> int:
    """Settle open stakes for Finished games on a curated store. No-op if unsupported."""
    ledger = getattr(store, "ledger", None)
    if ledger is not None:
        n = 0
        for game in store.iter_games():
            rec = game.record
            if rec.status != "Finished" or rec.home_win is None:
                continue
            n += int(ledger.settle_game(game_id=game.game_id, home_win=bool(rec.home_win)))
        if n:
            logger.info("stage=settle settled=%s", n)
        return n
    conn = getattr(store, "_conn", None)
    if conn is None:
        return 0
    return settle_finished_postgres(conn)


def settle_finished_postgres(conn: Any) -> int:
    """SQL settle. Second run finds no open rows (idempotent)."""
    rows = conn.execute(
        """
        SELECT s.stake_id, s.user_id, s.side, s.amount, g.home_win
        FROM stakes s
        JOIN games g ON g.game_id = s.game_id
        WHERE s.status = 'open' AND g.status = 'Finished' AND g.home_win IS NOT NULL
        """
    ).fetchall()
    settled = 0
    for row in rows:
        stake_id = int(row["stake_id"] if isinstance(row, dict) else row[0])
        user_id = int(row["user_id"] if isinstance(row, dict) else row[1])
        side = str(row["side"] if isinstance(row, dict) else row[2])
        amount = int(row["amount"] if isinstance(row, dict) else row[3])
        home_win = bool(row["home_win"] if isinstance(row, dict) else row[4])
        winner = "home" if home_win else "away"
        user_wallet = conn.execute(
            "SELECT wallet_id, balance FROM wallets WHERE kind = 'user' AND user_id = %s",
            (user_id,),
        ).fetchone()
        house = conn.execute(
            "SELECT wallet_id, balance FROM wallets WHERE kind = 'house' LIMIT 1"
        ).fetchone()
        if user_wallet is None or house is None:
            continue
        uw = user_wallet["wallet_id"] if isinstance(user_wallet, dict) else user_wallet[0]
        hw = house["wallet_id"] if isinstance(house, dict) else house[0]
        if side == winner:
            conn.execute(
                "UPDATE wallets SET balance = balance + %s, updated_at = NOW() WHERE wallet_id = %s",
                (amount * 2, uw),
            )
            conn.execute(
                "UPDATE wallets SET balance = balance - %s, updated_at = NOW() WHERE wallet_id = %s",
                (amount, hw),
            )
            conn.execute(
                """
                INSERT INTO ledger_entries (wallet_id, amount, reason, stake_id)
                VALUES (%s, %s, 'settle_win', %s), (%s, %s, 'settle_house_pay', %s)
                """,
                (uw, amount * 2, stake_id, hw, -amount, stake_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO ledger_entries (wallet_id, amount, reason, stake_id)
                VALUES (%s, 0, 'settle_lose', %s)
                """,
                (uw, stake_id),
            )
        conn.execute(
            "UPDATE stakes SET status = 'settled', updated_at = NOW() WHERE stake_id = %s AND status = 'open'",
            (stake_id,),
        )
        settled += 1
    if settled:
        conn.commit()
        logger.info("stage=settle settled=%s", settled)
    return settled
