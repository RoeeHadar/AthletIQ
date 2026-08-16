-- Implements: FR-002, FR-021, FR-022, DR-002, DR-003, DR-004, DR-005, DR-006, NFR-005, CON-002, ADR-001, ADR-010, ADR-012, ADR-014, ADR-015, CR-004, CR-005
-- AthletIQ curated schema contract (PostgreSQL)
-- Design: docs/06-design/database-design.md
-- Status: Approved contract aligned to Gate 4 design + ADR-010 (BIGINT) + CR-004

CREATE TABLE IF NOT EXISTS schema_migrations (
    version              TEXT PRIMARY KEY,
    applied_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    team_id              BIGSERIAL PRIMARY KEY,
    provider_team_id     TEXT NOT NULL,
    name                 TEXT NOT NULL,
    abbreviation         TEXT,
    conference           TEXT,
    division             TEXT,
    sport                TEXT NOT NULL DEFAULT 'basketball',
    league               TEXT NOT NULL DEFAULT 'nba',
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT teams_league_provider_uid UNIQUE (league, provider_team_id)
);

CREATE TABLE IF NOT EXISTS players (
    player_id            BIGSERIAL PRIMARY KEY,
    provider_player_id   TEXT NOT NULL,
    full_name            TEXT NOT NULL,
    team_id              BIGINT REFERENCES teams(team_id),
    league               TEXT NOT NULL DEFAULT 'nba',
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT players_league_provider_uid UNIQUE (league, provider_player_id)
);

CREATE TABLE IF NOT EXISTS games (
    game_id              BIGSERIAL PRIMARY KEY,
    provider_game_id     TEXT NOT NULL,
    season               INT NOT NULL,
    game_start_time      TIMESTAMPTZ NOT NULL,
    home_team_id         BIGINT NOT NULL REFERENCES teams(team_id),
    away_team_id         BIGINT NOT NULL REFERENCES teams(team_id),
    home_score           INT,
    away_score           INT,
    home_win             BOOLEAN,
    status               TEXT NOT NULL DEFAULT 'unknown',
    sport                TEXT NOT NULL DEFAULT 'basketball',
    league               TEXT NOT NULL DEFAULT 'nba',
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT games_teams_distinct CHECK (home_team_id <> away_team_id),
    CONSTRAINT games_league_provider_uid UNIQUE (league, provider_game_id),
    CONSTRAINT games_status_known CHECK (status IN ('scheduled', 'in_progress', 'Finished', 'unknown'))
);

CREATE TABLE IF NOT EXISTS player_game_stats (
    game_id              BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    player_id            BIGINT NOT NULL REFERENCES players(player_id),
    team_id              BIGINT NOT NULL REFERENCES teams(team_id),
    minutes              NUMERIC,
    points               INT,
    rebounds             INT,
    assists              INT,
    steals               INT,
    blocks               INT,
    turnovers            INT,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (game_id, player_id)
);

CREATE TABLE IF NOT EXISTS team_game_stats (
    game_id              BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    team_id              BIGINT NOT NULL REFERENCES teams(team_id),
    is_home              BOOLEAN NOT NULL,
    points_for           INT,
    points_against       INT,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (game_id, team_id)
);

-- payload JSONB envelope: {values, label_home_win, used_cold_start_home, used_cold_start_away}
CREATE TABLE IF NOT EXISTS features (
    game_id              BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    feature_version      TEXT NOT NULL,
    payload              JSONB NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (game_id, feature_version)
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    snapshot_id          BIGSERIAL PRIMARY KEY,
    game_id              BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    captured_at          TIMESTAMPTZ NOT NULL,
    source               TEXT NOT NULL,
    implied_p_home_win   DOUBLE PRECISION NOT NULL,
    payload              JSONB,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (game_id, source, captured_at)
);

-- Optional mirror of artifact metadata (JSON files remain canonical for serving)
CREATE TABLE IF NOT EXISTS model_registry (
    model_version        TEXT PRIMARY KEY,
    feature_version      TEXT NOT NULL,
    dataset_version      TEXT NOT NULL,
    code_commit          TEXT,
    artifact_path        TEXT NOT NULL,
    metrics              JSONB,
    training_config      JSONB,
    is_selected          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_games_start ON games (game_start_time);
CREATE INDEX IF NOT EXISTS idx_games_season ON games (season);
CREATE INDEX IF NOT EXISTS idx_games_league ON games (league);
CREATE INDEX IF NOT EXISTS idx_teams_league ON teams (league);
CREATE INDEX IF NOT EXISTS idx_team_game_stats_team_game ON team_game_stats (team_id, game_id);
CREATE INDEX IF NOT EXISTS idx_player_game_stats_player_game ON player_game_stats (player_id, game_id);
CREATE INDEX IF NOT EXISTS idx_player_game_stats_team_game ON player_game_stats (team_id, game_id);
CREATE INDEX IF NOT EXISTS idx_features_version_game ON features (feature_version, game_id);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_game ON odds_snapshots (game_id);
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
