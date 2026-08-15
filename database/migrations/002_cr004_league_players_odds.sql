-- Implements: FR-002, FR-017, FR-018, DR-002, DR-004, NFR-005, ADR-012, CR-004
-- Forward-only. Idempotent via IF EXISTS / IF NOT EXISTS.

ALTER TABLE teams ADD COLUMN IF NOT EXISTS sport TEXT NOT NULL DEFAULT 'basketball';
ALTER TABLE teams ADD COLUMN IF NOT EXISTS league TEXT NOT NULL DEFAULT 'nba';
ALTER TABLE games ADD COLUMN IF NOT EXISTS sport TEXT NOT NULL DEFAULT 'basketball';
ALTER TABLE games ADD COLUMN IF NOT EXISTS league TEXT NOT NULL DEFAULT 'nba';
ALTER TABLE players ADD COLUMN IF NOT EXISTS league TEXT NOT NULL DEFAULT 'nba';

ALTER TABLE teams DROP CONSTRAINT IF EXISTS teams_provider_team_id_key;
ALTER TABLE games DROP CONSTRAINT IF EXISTS games_provider_game_id_key;
ALTER TABLE players DROP CONSTRAINT IF EXISTS players_provider_player_id_key;

DROP INDEX IF EXISTS teams_provider_team_id_key;
DROP INDEX IF EXISTS games_provider_game_id_key;
DROP INDEX IF EXISTS players_provider_player_id_key;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'teams_league_provider_uid'
    ) THEN
        ALTER TABLE teams ADD CONSTRAINT teams_league_provider_uid UNIQUE (league, provider_team_id);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'games_league_provider_uid'
    ) THEN
        ALTER TABLE games ADD CONSTRAINT games_league_provider_uid UNIQUE (league, provider_game_id);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'players_league_provider_uid'
    ) THEN
        ALTER TABLE players ADD CONSTRAINT players_league_provider_uid UNIQUE (league, provider_player_id);
    END IF;
END $$;

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

CREATE INDEX IF NOT EXISTS idx_games_league ON games (league);
CREATE INDEX IF NOT EXISTS idx_teams_league ON teams (league);
CREATE INDEX IF NOT EXISTS idx_odds_snapshots_game ON odds_snapshots (game_id);

INSERT INTO schema_migrations (version) VALUES ('002_cr004_league_players_odds')
ON CONFLICT (version) DO NOTHING;
