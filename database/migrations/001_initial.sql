-- Implements: FR-002, DR-002, DR-003, NFR-005, CON-002, ADR-001, ADR-010
-- AthletIQ migration 001: initial curated schema (ADR-001, ADR-010, NFR-005)
-- Forward-only. Idempotent via IF NOT EXISTS.
-- Reserved player tables: CR-001 (not loaded by pipeline).

CREATE TABLE IF NOT EXISTS schema_migrations (
    version              TEXT PRIMARY KEY,
    applied_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    team_id              BIGSERIAL PRIMARY KEY,
    provider_team_id     TEXT NOT NULL UNIQUE,
    name                 TEXT NOT NULL,
    abbreviation         TEXT,
    conference           TEXT,
    division             TEXT,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS players (
    player_id            BIGSERIAL PRIMARY KEY,
    provider_player_id   TEXT NOT NULL UNIQUE,
    full_name            TEXT NOT NULL,
    team_id              BIGINT REFERENCES teams(team_id),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS games (
    game_id              BIGSERIAL PRIMARY KEY,
    provider_game_id     TEXT NOT NULL UNIQUE,
    season               INT NOT NULL,
    game_start_time      TIMESTAMPTZ NOT NULL,
    home_team_id         BIGINT NOT NULL REFERENCES teams(team_id),
    away_team_id         BIGINT NOT NULL REFERENCES teams(team_id),
    home_score           INT,
    away_score           INT,
    home_win             BOOLEAN,
    status               TEXT NOT NULL DEFAULT 'unknown',
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT games_teams_distinct CHECK (home_team_id <> away_team_id)
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

CREATE TABLE IF NOT EXISTS features (
    game_id              BIGINT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    feature_version      TEXT NOT NULL,
    payload              JSONB NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (game_id, feature_version)
);

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
CREATE INDEX IF NOT EXISTS idx_team_game_stats_team_game ON team_game_stats (team_id, game_id);
CREATE INDEX IF NOT EXISTS idx_player_game_stats_player_game ON player_game_stats (player_id, game_id);
CREATE INDEX IF NOT EXISTS idx_player_game_stats_team_game ON player_game_stats (team_id, game_id);
CREATE INDEX IF NOT EXISTS idx_features_version_game ON features (feature_version, game_id);

INSERT INTO schema_migrations (version)
VALUES ('001_initial')
ON CONFLICT (version) DO NOTHING;
