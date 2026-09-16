-- =============================================================================
-- Skill Service — PostgreSQL Schema
-- File: Services/skill/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS skills (
    id          SERIAL        PRIMARY KEY,
    name        VARCHAR(150)  NOT NULL UNIQUE,
    user_id     INTEGER       DEFAULT 0,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (name);

DROP TRIGGER IF EXISTS trg_skills_updated_at ON skills;
CREATE TRIGGER trg_skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
