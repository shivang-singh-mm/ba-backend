-- =============================================================================
-- Location Service — PostgreSQL Schema
-- File: Services/location/schema.sql
-- =============================================================================

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    id            SERIAL        PRIMARY KEY,
    name          VARCHAR(120)  NOT NULL UNIQUE,
    country_code  VARCHAR(10)   NOT NULL UNIQUE,
    phone_code    VARCHAR(10)   NOT NULL,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_countries_country_code ON countries (country_code);

-- Trigger: auto-update updated_at on any UPDATE
DROP TRIGGER IF EXISTS trg_countries_updated_at ON countries;
CREATE TRIGGER trg_countries_updated_at
    BEFORE UPDATE ON countries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- States table
CREATE TABLE IF NOT EXISTS states (
    id          SERIAL        PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    country_id  INTEGER       NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (name, country_id)
);

CREATE INDEX IF NOT EXISTS idx_states_country_id ON states (country_id);

-- Trigger: auto-update updated_at on any UPDATE
DROP TRIGGER IF EXISTS trg_states_updated_at ON states;
CREATE TRIGGER trg_states_updated_at
    BEFORE UPDATE ON states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Cities table
CREATE TABLE IF NOT EXISTS cities (
    id        SERIAL        PRIMARY KEY,
    name      VARCHAR(120)  NOT NULL,
    state_id  INTEGER       NOT NULL REFERENCES states(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (name, state_id)
);

CREATE INDEX IF NOT EXISTS idx_cities_state_id ON cities (state_id);

-- Trigger: auto-update updated_at on any UPDATE
DROP TRIGGER IF EXISTS trg_cities_updated_at ON cities;
CREATE TRIGGER trg_cities_updated_at
    BEFORE UPDATE ON cities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
