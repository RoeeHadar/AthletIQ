-- Implements: FR-002, FR-021, FR-022, DR-002, DR-005, DR-006, NFR-005, CON-002, ADR-010, ADR-014, ADR-015, CR-005
-- Forward-only. Idempotent via IF NOT EXISTS / ON CONFLICT.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'games_status_known'
    ) THEN
        ALTER TABLE games ADD CONSTRAINT games_status_known
            CHECK (status IN ('scheduled', 'in_progress', 'Finished', 'unknown'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_games_status_start ON games (status, game_start_time);

CREATE TABLE IF NOT EXISTS users (
    user_id              BIGSERIAL PRIMARY KEY,
    slug                 TEXT NOT NULL UNIQUE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wallets (
    wallet_id            BIGSERIAL PRIMARY KEY,
    kind                 TEXT NOT NULL CHECK (kind IN ('user', 'house')),
    user_id              BIGINT REFERENCES users(user_id),
    balance              INT NOT NULL CHECK (balance >= 0),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT wallets_user_kind CHECK (
        (kind = 'user' AND user_id IS NOT NULL)
        OR (kind = 'house' AND user_id IS NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_wallets_user ON wallets (user_id) WHERE kind = 'user';
CREATE UNIQUE INDEX IF NOT EXISTS idx_wallets_one_house ON wallets ((kind)) WHERE kind = 'house';

CREATE TABLE IF NOT EXISTS stakes (
    stake_id             BIGSERIAL PRIMARY KEY,
    user_id              BIGINT NOT NULL REFERENCES users(user_id),
    game_id              BIGINT NOT NULL REFERENCES games(game_id),
    side                 TEXT NOT NULL CHECK (side IN ('home', 'away')),
    amount               INT NOT NULL CHECK (amount >= 1),
    status               TEXT NOT NULL CHECK (status IN ('open', 'settled', 'canceled')),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stakes_one_open ON stakes (user_id, game_id) WHERE status = 'open';

CREATE TABLE IF NOT EXISTS ledger_entries (
    ledger_entry_id      BIGSERIAL PRIMARY KEY,
    wallet_id            BIGINT NOT NULL REFERENCES wallets(wallet_id),
    amount               INT NOT NULL,
    reason               TEXT NOT NULL,
    stake_id             BIGINT REFERENCES stakes(stake_id),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ledger_wallet_created ON ledger_entries (wallet_id, created_at);
CREATE INDEX IF NOT EXISTS idx_users_slug ON users (slug);

INSERT INTO users (slug) VALUES ('demo-1'), ('demo-2')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO wallets (kind, user_id, balance)
SELECT 'user', u.user_id, 1000
FROM users u
WHERE u.slug IN ('demo-1', 'demo-2')
  AND NOT EXISTS (
      SELECT 1 FROM wallets w WHERE w.kind = 'user' AND w.user_id = u.user_id
  );

INSERT INTO wallets (kind, user_id, balance)
SELECT 'house', NULL, 1000000000
WHERE NOT EXISTS (SELECT 1 FROM wallets WHERE kind = 'house');

INSERT INTO schema_migrations (version) VALUES ('003_cr005_ledger_game_lifecycle')
ON CONFLICT (version) DO NOTHING;
