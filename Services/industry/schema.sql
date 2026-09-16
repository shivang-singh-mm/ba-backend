-- =============================================================================
-- Industry Service — PostgreSQL Schema
-- File: Services/industry/schema.sql
-- =============================================================================

-- Industries table
-- user_id defaults to 0 (system-seeded); nullable, no FK constraint.
CREATE TABLE IF NOT EXISTS industries (
    id          SERIAL        PRIMARY KEY,
    name        VARCHAR(150)  NOT NULL UNIQUE,
    user_id     INTEGER       DEFAULT 0,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_industries_name ON industries (name);

-- Trigger: auto-update updated_at on any UPDATE
DROP TRIGGER IF EXISTS trg_industries_updated_at ON industries;
CREATE TRIGGER trg_industries_updated_at
    BEFORE UPDATE ON industries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
