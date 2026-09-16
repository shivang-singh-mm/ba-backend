-- =============================================================================
-- Language Service — PostgreSQL Schema
-- File: Services/language/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS languages (
    id          SERIAL        PRIMARY KEY,
    name        VARCHAR(150)  NOT NULL UNIQUE,
    user_id     INTEGER       DEFAULT 0,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_languages_name ON languages (name);

DROP TRIGGER IF EXISTS trg_languages_updated_at ON languages;
CREATE TRIGGER trg_languages_updated_at
    BEFORE UPDATE ON languages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
