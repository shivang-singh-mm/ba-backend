-- =============================================================================
-- User Service — PostgreSQL Schema
-- File: Services/user/schema.sql
-- =============================================================================

-- Users table
-- No password column — authentication is fully OTP-based.
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(120)    NOT NULL,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    phone       VARCHAR(20),
    role        VARCHAR(50)     NOT NULL DEFAULT 'user',   -- user | admin | manager | brand | agency
    is_active   BOOLEAN         NOT NULL DEFAULT TRUE,
    is_deleted  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email     ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role      ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active) WHERE is_deleted = FALSE;

-- Trigger: auto-update updated_at on any UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


