-- =============================================================================
-- Campaigns Service — PostgreSQL Schema
-- File: Services/campaigns/schema.sql
-- =============================================================================

-- Status: 1=draft, 2=pending, 3=active, 4=completed, 5=deleted
CREATE TABLE IF NOT EXISTS campaigns (
    id              SERIAL          PRIMARY KEY,
    user_id         INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255)    NOT NULL,
    description     TEXT,
    total_hours     NUMERIC(6, 2),
    start_time      TIME,
    end_time        TIME,
    date            DATE,
    target          VARCHAR(255),
    locality        VARCHAR(255),
    status          SMALLINT        NOT NULL DEFAULT 1,  -- 1=draft, 2=pending, 3=active, 4=completed, 5=deleted
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns (user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status  ON campaigns (status) WHERE is_deleted = FALSE;

DROP TRIGGER IF EXISTS trg_campaigns_updated_at ON campaigns;
CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign props — one-to-one with campaigns
CREATE TABLE IF NOT EXISTS campaign_props (
    id          SERIAL      PRIMARY KEY,
    campaign_id INTEGER     NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE UNIQUE,
    stalls      INTEGER     NOT NULL DEFAULT 0,
    tables      INTEGER     NOT NULL DEFAULT 0,
    chairs      INTEGER     NOT NULL DEFAULT 0,
    led         INTEGER     NOT NULL DEFAULT 0,
    banners     INTEGER     NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_props_campaign_id ON campaign_props (campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_props_updated_at ON campaign_props;
CREATE TRIGGER trg_campaign_props_updated_at
    BEFORE UPDATE ON campaign_props
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- AI Chat Sessions — one session per (user, campaign)
-- messages: JSONB array of {role: "user"|"assistant", content: "..."}
CREATE TABLE IF NOT EXISTS campaign_ai_sessions (
    id          SERIAL      PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id INTEGER     NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    messages    JSONB       NOT NULL DEFAULT '[]',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, campaign_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_sessions_campaign ON campaign_ai_sessions (campaign_id);

DROP TRIGGER IF EXISTS trg_ai_sessions_updated_at ON campaign_ai_sessions;
CREATE TRIGGER trg_ai_sessions_updated_at
    BEFORE UPDATE ON campaign_ai_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

