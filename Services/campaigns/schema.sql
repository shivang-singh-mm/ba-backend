-- =============================================================================
-- Campaigns Service — PostgreSQL Schema
-- File: Services/campaigns/schema.sql
-- =============================================================================

-- Campaign Types lookup table
CREATE TABLE IF NOT EXISTS campaign_types (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_types_name ON campaign_types(name);

DROP TRIGGER IF EXISTS trg_campaign_types_updated_at ON campaign_types;
CREATE TRIGGER trg_campaign_types_updated_at
    BEFORE UPDATE ON campaign_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Venue Types lookup table
CREATE TABLE IF NOT EXISTS venue_types (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_venue_types_name ON venue_types(name);

DROP TRIGGER IF EXISTS trg_venue_types_updated_at ON venue_types;
CREATE TRIGGER trg_venue_types_updated_at
    BEFORE UPDATE ON venue_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Core Campaigns Table
-- Status: 1=draft, 2=pending, 3=active, 4=completed, 5=deleted
CREATE TABLE IF NOT EXISTS campaigns (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    title               VARCHAR(255)    NOT NULL,
    description         TEXT,

    city_id             INTEGER         REFERENCES cities(id) ON DELETE SET NULL,
    locality            VARCHAR(255),

    date                DATE,
    start_time          TIME,
    end_time            TIME,
    total_hours         NUMERIC(6, 2),

    status              SMALLINT        NOT NULL DEFAULT 1,
    -- 1=draft, 2=pending, 3=active, 4=completed, 5=deleted

    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_city_id ON campaigns(city_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status) WHERE is_deleted = FALSE;

DROP TRIGGER IF EXISTS trg_campaigns_updated_at ON campaigns;
CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign Products
CREATE TABLE IF NOT EXISTS campaign_products (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    product_name        VARCHAR(255)    NOT NULL,
    product_description TEXT,
    product_url         TEXT,
    offer_description   TEXT,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_products_campaign ON campaign_products(campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_products_updated_at ON campaign_products;
CREATE TRIGGER trg_campaign_products_updated_at
    BEFORE UPDATE ON campaign_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign Industries
CREATE TABLE IF NOT EXISTS campaign_industries (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    industry_id         INTEGER         NOT NULL REFERENCES industries(id) ON DELETE CASCADE,

    is_primary          BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, industry_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_industries_campaign ON campaign_industries(campaign_id);


-- Campaign Skills (Required skills for campaign execution)
CREATE TABLE IF NOT EXISTS campaign_skills (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    skill_id            INTEGER         NOT NULL REFERENCES skills(id) ON DELETE CASCADE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_skills_campaign ON campaign_skills(campaign_id);


-- Campaign Type Map (Primary & Secondary Campaign Types)
CREATE TABLE IF NOT EXISTS campaign_type_map (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    campaign_type_id    INTEGER         NOT NULL REFERENCES campaign_types(id) ON DELETE CASCADE,

    is_primary          BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, campaign_type_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_type_map_campaign ON campaign_type_map(campaign_id);


-- Campaign Venues
CREATE TABLE IF NOT EXISTS campaign_venues (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    venue_type_id       INTEGER         REFERENCES venue_types(id) ON DELETE SET NULL,
    venue_name          VARCHAR(255),
    venue_address       TEXT,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_venues_campaign ON campaign_venues(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_venues_type ON campaign_venues(venue_type_id);

DROP TRIGGER IF EXISTS trg_campaign_venues_updated_at ON campaign_venues;
CREATE TRIGGER trg_campaign_venues_updated_at
    BEFORE UPDATE ON campaign_venues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign Audiences
CREATE TABLE IF NOT EXISTS campaign_audiences (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    min_age             SMALLINT,
    max_age             SMALLINT,

    gender              VARCHAR(30),

    income_min          NUMERIC(12, 2),
    income_max          NUMERIC(12, 2),

    occupation          VARCHAR(255),
    education           VARCHAR(255),
    life_stage          VARCHAR(255),

    geography           VARCHAR(255),
    origin              VARCHAR(255),

    interests           TEXT,
    lifestyle           TEXT,
    purchase_behavior   TEXT,

    audience_size       INTEGER,

    description         TEXT,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_audiences_campaign ON campaign_audiences(campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_audiences_updated_at ON campaign_audiences;
CREATE TRIGGER trg_campaign_audiences_updated_at
    BEFORE UPDATE ON campaign_audiences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign Languages
CREATE TABLE IF NOT EXISTS campaign_languages (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    language_id         INTEGER         NOT NULL REFERENCES languages(id) ON DELETE CASCADE,

    proficiency         SMALLINT        NOT NULL DEFAULT 2,
    -- 1=basic, 2=conversational, 3=fluent, 4=native

    is_required         BOOLEAN         NOT NULL DEFAULT TRUE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE(campaign_id, language_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_languages_campaign ON campaign_languages(campaign_id);


-- Campaign Props
CREATE TABLE IF NOT EXISTS campaign_props (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE UNIQUE,

    stalls              INTEGER         NOT NULL DEFAULT 0,
    tables              INTEGER         NOT NULL DEFAULT 0,
    chairs              INTEGER         NOT NULL DEFAULT 0,
    led                 INTEGER         NOT NULL DEFAULT 0,
    banners             INTEGER         NOT NULL DEFAULT 0,

    other_requirements  TEXT,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_props_campaign ON campaign_props(campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_props_updated_at ON campaign_props;
CREATE TRIGGER trg_campaign_props_updated_at
    BEFORE UPDATE ON campaign_props
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- AI Chat Sessions
CREATE TABLE IF NOT EXISTS campaign_ai_sessions (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    messages            JSONB           NOT NULL DEFAULT '[]',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, campaign_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_sessions_campaign ON campaign_ai_sessions(campaign_id);

DROP TRIGGER IF EXISTS trg_ai_sessions_updated_at ON campaign_ai_sessions;
CREATE TRIGGER trg_ai_sessions_updated_at
    BEFORE UPDATE ON campaign_ai_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Campaign Matching Rules
-- Rules: 1=hard, 2=soft, 3=ignore
CREATE TABLE IF NOT EXISTS campaign_matching_rules (
    id                  SERIAL          PRIMARY KEY,
    campaign_id         INTEGER         NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE UNIQUE,

    location_rule       SMALLINT        NOT NULL DEFAULT 2,
    language_rule       SMALLINT        NOT NULL DEFAULT 2,
    industry_rule       SMALLINT        NOT NULL DEFAULT 2,
    experience_rule     SMALLINT        NOT NULL DEFAULT 2,
    output_rule         SMALLINT        NOT NULL DEFAULT 2,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_matching_rules_campaign ON campaign_matching_rules(campaign_id);

DROP TRIGGER IF EXISTS trg_campaign_matching_rules_updated_at ON campaign_matching_rules;
CREATE TRIGGER trg_campaign_matching_rules_updated_at
    BEFORE UPDATE ON campaign_matching_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

