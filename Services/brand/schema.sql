-- =============================================================================
-- Brand Service — PostgreSQL Schema
-- File: Services/brand/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS brand_profiles (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    brand_name          VARCHAR(200)    NOT NULL,
    brand_description   TEXT,
    brand_logo_url      TEXT,
    brand_website       TEXT,
    city_id             INTEGER         REFERENCES cities(id) ON DELETE SET NULL,
    is_verified         BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brand_profiles_user_id ON brand_profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_brand_profiles_city_id ON brand_profiles (city_id);

DROP TRIGGER IF EXISTS trg_brand_profiles_updated_at ON brand_profiles;
CREATE TRIGGER trg_brand_profiles_updated_at
    BEFORE UPDATE ON brand_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Brand Industries
CREATE TABLE IF NOT EXISTS brand_industries (
    id              SERIAL      PRIMARY KEY,
    brand_id        INTEGER     NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    industry_id     INTEGER     NOT NULL REFERENCES industries(id) ON DELETE CASCADE,
    is_primary      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(brand_id, industry_id)
);

CREATE INDEX IF NOT EXISTS idx_brand_industries_brand ON brand_industries (brand_id);

-- Brand Locations
CREATE TABLE IF NOT EXISTS brand_locations (
    id              SERIAL      PRIMARY KEY,
    brand_id        INTEGER     NOT NULL REFERENCES brand_profiles(id) ON DELETE CASCADE,
    city_id         INTEGER     NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    is_primary      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(brand_id, city_id)
);

CREATE INDEX IF NOT EXISTS idx_brand_locations_brand ON brand_locations (brand_id);
