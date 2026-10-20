-- =============================================================================
-- Matching Service — PostgreSQL Schema
-- File: Services/matching/schema.sql
-- =============================================================================

-- Campaign Provider Matches
-- Match Status: 1=matched, 2=shortlisted, 3=contacted, 4=accepted, 5=rejected
CREATE TABLE IF NOT EXISTS campaign_provider_matches (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    provider_id         INTEGER         NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,

    total_score         NUMERIC(5, 2)   NOT NULL,
    location_score      NUMERIC(5, 2)   NOT NULL DEFAULT 0.00,
    language_score      NUMERIC(5, 2)   NOT NULL DEFAULT 0.00,
    industry_score      NUMERIC(5, 2)   NOT NULL DEFAULT 0.00,
    skills_score        NUMERIC(5, 2)   NOT NULL DEFAULT 0.00,
    ai_experience_score NUMERIC(5, 2)   NOT NULL DEFAULT 0.00,

    ai_reasoning        TEXT,
    is_eligible         BOOLEAN         NOT NULL DEFAULT TRUE,
    match_status        SMALLINT        NOT NULL DEFAULT 1,
    -- 1=matched, 2=shortlisted, 3=contacted, 4=accepted, 5=rejected

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, provider_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_campaign_id ON campaign_provider_matches(campaign_id);
CREATE INDEX IF NOT EXISTS idx_matches_provider_id ON campaign_provider_matches(provider_id);
CREATE INDEX IF NOT EXISTS idx_matches_total_score ON campaign_provider_matches(total_score DESC);

DROP TRIGGER IF EXISTS trg_campaign_provider_matches_updated_at ON campaign_provider_matches;
CREATE TRIGGER trg_campaign_provider_matches_updated_at
    BEFORE UPDATE ON campaign_provider_matches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Alias view so queries referencing campaign_matches work seamlessly
CREATE OR REPLACE VIEW campaign_matches AS
    SELECT * FROM campaign_provider_matches;


-- Campaign Match Weights
CREATE TABLE IF NOT EXISTS campaign_match_weights (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE UNIQUE,

    location_weight     NUMERIC(4, 2)   NOT NULL DEFAULT 0.20,
    language_weight     NUMERIC(4, 2)   NOT NULL DEFAULT 0.20,
    industry_weight     NUMERIC(4, 2)   NOT NULL DEFAULT 0.15,
    skills_weight       NUMERIC(4, 2)   NOT NULL DEFAULT 0.20,
    ai_experience_weight NUMERIC(4, 2)  NOT NULL DEFAULT 0.25,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_match_weights_campaign ON campaign_match_weights(campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_match_weights_updated_at ON campaign_match_weights;
CREATE TRIGGER trg_campaign_match_weights_updated_at
    BEFORE UPDATE ON campaign_match_weights
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

