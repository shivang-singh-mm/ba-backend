-- =============================================================================
-- Campaigns Service — PostgreSQL Schema
-- File: Services/campaigns/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS campaigns (
    id          SERIAL          PRIMARY KEY,
    user_id     INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255)    NOT NULL,
    description TEXT,
    status      VARCHAR(50)     NOT NULL DEFAULT 'draft',
    -- status values: draft | active | paused | completed | archived
    budget      NUMERIC(14, 2)  CHECK (budget >= 0),
    start_date  TIMESTAMPTZ,
    end_date    TIMESTAMPTZ,
    tags        TEXT[]          DEFAULT '{}',
    metadata    JSONB           DEFAULT '{}',
    is_deleted  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_campaign_dates CHECK (end_date IS NULL OR end_date > start_date)
);

CREATE INDEX IF NOT EXISTS idx_campaigns_user_id    ON campaigns (user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status     ON campaigns (status) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_campaigns_tags       ON campaigns USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_campaigns_metadata   ON campaigns USING GIN (metadata);

DROP TRIGGER IF EXISTS trg_campaigns_updated_at ON campaigns;
CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
