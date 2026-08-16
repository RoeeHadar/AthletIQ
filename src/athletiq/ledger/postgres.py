# Implements: FR-023, DR-005, ADR-014, ADR-015, CR-005
"""Postgres even-money stake/cancel/replace (same semantics as MemoryLedger)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from athletiq.ledger.errors import LedgerError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PostgresLedger:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def require_user(self, slug: str) -> dict[str, Any]:
        if slug == "house":
            raise LedgerError("user_not_found", "unknown demo user", {"user": slug})
        row = self._conn.execute(
            """
            SELECT u.user_id, u.slug, w.wallet_id, w.balance
            FROM users u
            JOIN wallets w ON w.user_id = u.user_id AND w.kind = 'user'
            WHERE u.slug = %s
            """,
            (slug,),
        ).fetchone()
        if row is None:
            raise LedgerError("user_not_found", "unknown demo user", {"user": slug})
        return dict(row)

    def balance(self, slug: str) -> int:
        return int(self.require_user(slug)["balance"])

    def open_stakes(self, slug: str) -> list[dict[str, Any]]:
        user = self.require_user(slug)
        rows = self._conn.execute(
            """
            SELECT stake_id, user_id, game_id, side, amount, status
            FROM stakes
            WHERE user_id = %s AND status = 'open'
            ORDER BY created_at
            """,
            (user["user_id"],),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stake(self, stake_id: int) -> dict[str, Any] | None:
        row = self._conn.execute(
            """
            SELECT stake_id, user_id, game_id, side, amount, status
            FROM stakes WHERE stake_id = %s
            """,
            (stake_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def place_or_replace(
        self,
        *,
        slug: str,
        game_id: int,
        side: str,
        amount: int,
        replace: bool = False,
        scores_null: bool,
        tip: datetime,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        now = now or _utcnow()
        if tip.tzinfo is None:
            tip = tip.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        if side not in {"home", "away"}:
            raise LedgerError("invalid_request", "side must be home or away")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 1:
            raise LedgerError("invalid_request", "amount must be a positive integer")
        if (not scores_null) or tip <= now:
            raise LedgerError("stake_window_closed", "new stakes only before tip with null scores")
        user = self.require_user(slug)
        existing = self._conn.execute(
            """
            SELECT stake_id, amount FROM stakes
            WHERE user_id = %s AND game_id = %s AND status = 'open'
            """,
            (user["user_id"], game_id),
        ).fetchone()
        with self._conn.transaction():
            if existing is not None and not replace:
                raise LedgerError(
                    "duplicate_open_stake",
                    "open stake already exists for this game",
                    {"game_id": str(game_id)},
                )
            if existing is not None and replace:
                old_id = int(existing["stake_id"])
                old_amt = int(existing["amount"])
                self._conn.execute(
                    "UPDATE wallets SET balance = balance + %s, updated_at = NOW() WHERE wallet_id = %s",
                    (old_amt, user["wallet_id"]),
                )
                self._conn.execute(
                    """
                    INSERT INTO ledger_entries (wallet_id, amount, reason, stake_id)
                    VALUES (%s, %s, 'stake_unlock', %s)
                    """,
                    (user["wallet_id"], old_amt, old_id),
                )
                self._conn.execute(
                    "UPDATE stakes SET status = 'canceled', updated_at = NOW() WHERE stake_id = %s",
                    (old_id,),
                )
                user = self.require_user(slug)
            if int(user["balance"]) < amount:
                raise LedgerError("insufficient_balance", "stake exceeds unlocked balance")
            self._conn.execute(
                "UPDATE wallets SET balance = balance - %s, updated_at = NOW() WHERE wallet_id = %s",
                (amount, user["wallet_id"]),
            )
            row = self._conn.execute(
                """
                INSERT INTO stakes (user_id, game_id, side, amount, status)
                VALUES (%s, %s, %s, %s, 'open')
                RETURNING stake_id, user_id, game_id, side, amount, status
                """,
                (user["user_id"], game_id, side, amount),
            ).fetchone()
            assert row is not None
            stake_id = int(row["stake_id"])
            self._conn.execute(
                """
                INSERT INTO ledger_entries (wallet_id, amount, reason, stake_id)
                VALUES (%s, %s, 'stake_lock', %s)
                """,
                (user["wallet_id"], -amount, stake_id),
            )
        return dict(row)

    def cancel(
        self,
        *,
        slug: str,
        stake_id: int,
        scores_null: bool,
        tip: datetime,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        now = now or _utcnow()
        if tip.tzinfo is None:
            tip = tip.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        if (not scores_null) or tip <= now:
            raise LedgerError("stake_window_closed", "cancel only before tip")
        user = self.require_user(slug)
        stake = self._conn.execute(
            """
            SELECT stake_id, user_id, game_id, side, amount, status
            FROM stakes WHERE stake_id = %s
            """,
            (stake_id,),
        ).fetchone()
        if stake is None or int(stake["user_id"]) != int(user["user_id"]):
            raise LedgerError("invalid_request", "unknown stake")
        if stake["status"] != "open":
            raise LedgerError("invalid_request", "stake is not open")
        with self._conn.transaction():
            self._conn.execute(
                "UPDATE wallets SET balance = balance + %s, updated_at = NOW() WHERE wallet_id = %s",
                (int(stake["amount"]), user["wallet_id"]),
            )
            self._conn.execute(
                """
                INSERT INTO ledger_entries (wallet_id, amount, reason, stake_id)
                VALUES (%s, %s, 'stake_unlock', %s)
                """,
                (user["wallet_id"], int(stake["amount"]), stake_id),
            )
            self._conn.execute(
                "UPDATE stakes SET status = 'canceled', updated_at = NOW() WHERE stake_id = %s",
                (stake_id,),
            )
        return dict(stake) | {"status": "canceled"}
