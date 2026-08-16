# Implements: FR-022, FR-023, DR-005, ADR-014, ADR-015, CR-005
"""In-memory even-money ledger for tests (same rules as Postgres)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from athletiq.ledger.errors import LedgerError

HOUSE_START = 1_000_000_000
USER_START = 1000
DEMO_SLUGS = ("demo-1", "demo-2")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MemoryLedger:
    """Seed demo-1/demo-2 at 1000 and a house wallet. Identity is slug only."""

    users: dict[str, int] = field(default_factory=dict)
    wallets: dict[str, dict[str, Any]] = field(default_factory=dict)
    stakes: dict[int, dict[str, Any]] = field(default_factory=dict)
    ledger: list[dict[str, Any]] = field(default_factory=list)
    _next_user: int = 1
    _next_wallet: int = 1
    _next_stake: int = 1
    _next_entry: int = 1

    def __post_init__(self) -> None:
        if not self.users:
            self.seed()

    def seed(self) -> None:
        for slug in DEMO_SLUGS:
            uid = self._next_user
            self._next_user += 1
            self.users[slug] = uid
            wid = self._next_wallet
            self._next_wallet += 1
            self.wallets[f"user:{uid}"] = {
                "wallet_id": wid,
                "kind": "user",
                "user_id": uid,
                "balance": USER_START,
            }
        hid = self._next_wallet
        self._next_wallet += 1
        self.wallets["house"] = {
            "wallet_id": hid,
            "kind": "house",
            "user_id": None,
            "balance": HOUSE_START,
        }

    def require_user(self, slug: str) -> int:
        if slug == "house" or slug not in self.users:
            raise LedgerError("user_not_found", "unknown demo user", {"user": slug})
        return self.users[slug]

    def wallet_for_user(self, user_id: int) -> dict[str, Any]:
        return self.wallets[f"user:{user_id}"]

    def balance(self, slug: str) -> int:
        uid = self.require_user(slug)
        return int(self.wallet_for_user(uid)["balance"])

    def open_stakes(self, slug: str) -> list[dict[str, Any]]:
        uid = self.require_user(slug)
        return [s for s in self.stakes.values() if s["user_id"] == uid and s["status"] == "open"]

    def get_stake(self, stake_id: int) -> dict[str, Any] | None:
        return self.stakes.get(int(stake_id))

    def _open_for(self, user_id: int, game_id: int) -> dict[str, Any] | None:
        for stake in self.stakes.values():
            if (
                stake["user_id"] == user_id
                and stake["game_id"] == game_id
                and stake["status"] == "open"
            ):
                return stake
        return None

    def _credit(self, wallet: dict[str, Any], amount: int, reason: str, stake_id: int | None) -> None:
        wallet["balance"] = int(wallet["balance"]) + amount
        self.ledger.append(
            {
                "id": self._next_entry,
                "wallet_id": wallet["wallet_id"],
                "amount": amount,
                "reason": reason,
                "stake_id": stake_id,
            }
        )
        self._next_entry += 1

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
        uid = self.require_user(slug)
        wallet = self.wallet_for_user(uid)
        existing = self._open_for(uid, game_id)
        if existing is not None and not replace:
            raise LedgerError(
                "duplicate_open_stake",
                "open stake already exists for this game",
                {"game_id": str(game_id)},
            )
        if existing is not None and replace:
            self._credit(wallet, int(existing["amount"]), "stake_unlock", existing["stake_id"])
            existing["status"] = "canceled"
            existing["updated_at"] = now
        if int(wallet["balance"]) < amount:
            raise LedgerError("insufficient_balance", "stake exceeds unlocked balance")
        self._credit(wallet, -amount, "stake_lock", None)
        sid = self._next_stake
        self._next_stake += 1
        stake = {
            "stake_id": sid,
            "user_id": uid,
            "user": slug,
            "game_id": game_id,
            "side": side,
            "amount": amount,
            "status": "open",
            "created_at": now,
            "updated_at": now,
        }
        self.stakes[sid] = stake
        self.ledger[-1]["stake_id"] = sid
        return stake

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
        uid = self.require_user(slug)
        stake = self.stakes.get(stake_id)
        if stake is None or stake["user_id"] != uid:
            raise LedgerError("invalid_request", "unknown stake")
        if stake["status"] != "open":
            raise LedgerError("invalid_request", "stake is not open")
        wallet = self.wallet_for_user(uid)
        self._credit(wallet, int(stake["amount"]), "stake_unlock", stake_id)
        stake["status"] = "canceled"
        stake["updated_at"] = now
        return stake

    def settle_game(self, *, game_id: int, home_win: bool | None) -> int:
        """Settle open stakes when a game is Finished. Idempotent. Returns settled count."""
        if home_win is None:
            return 0
        winner = "home" if home_win else "away"
        house = self.wallets["house"]
        n = 0
        for stake in self.stakes.values():
            if stake["game_id"] != game_id or stake["status"] != "open":
                continue
            user_wallet = self.wallet_for_user(int(stake["user_id"]))
            amount = int(stake["amount"])
            if stake["side"] == winner:
                self._credit(user_wallet, amount * 2, "settle_win", stake["stake_id"])
                self._credit(house, -amount, "settle_house_pay", stake["stake_id"])
            else:
                self._credit(user_wallet, 0, "settle_lose", stake["stake_id"])
            stake["status"] = "settled"
            n += 1
        return n
