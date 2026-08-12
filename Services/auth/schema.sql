-- =============================================================================
-- Auth Service — PostgreSQL Schema
-- File: Services/auth/schema.sql
-- =============================================================================

-- OTP Codes table
-- Stores SHA-256 hashed OTPs for email-based authentication.
-- The raw OTP is NEVER stored — only its hash.
CREATE TABLE IF NOT EXISTS otp_codes (
    id              SERIAL          PRIMARY KEY,
    user_id         INTEGER         REFERENCES users(id) ON DELETE CASCADE,
    email           VARCHAR(255)    NOT NULL,
    purpose         VARCHAR(20)     NOT NULL DEFAULT 'login',  -- register | login
    otp_hash        CHAR(64)        NOT NULL,                  -- SHA-256 hex digest
    expires_at      TIMESTAMPTZ     NOT NULL,
    attempts        SMALLINT        NOT NULL DEFAULT 0,
    is_used         BOOLEAN         NOT NULL DEFAULT FALSE,
    -- Pending registration data (only populated for purpose = 'register')
    pending_name    VARCHAR(120),
    pending_role    VARCHAR(50)     DEFAULT 'user',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_otp_email_purpose ON otp_codes (email, purpose, is_used);
CREATE INDEX IF NOT EXISTS idx_otp_expires_at    ON otp_codes (expires_at);


-- Token Blocklist table
-- Stores revoked JWT JTIs for logout support.
CREATE TABLE IF NOT EXISTS token_blocklist (
    id          SERIAL          PRIMARY KEY,
    jti         VARCHAR(36)     NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_blocklist_jti ON token_blocklist (jti);

-- Optional: auto-prune old blocklist rows > 30 days
-- (Can be run as a periodic job or pg_cron task)
-- DELETE FROM token_blocklist WHERE created_at < NOW() - INTERVAL '30 days';
