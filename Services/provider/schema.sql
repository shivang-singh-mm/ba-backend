-- =============================================================================
-- Provider Service — PostgreSQL Schema
-- File: Services/provider/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS provider_profiles (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    provider_type       SMALLINT        NOT NULL DEFAULT 1,  -- 1=individual, 2=agency, 3=freelancer
    description         TEXT,
    current_occupation  TEXT,
    date_of_birth       DATE,
    gender              VARCHAR(20),
    profile_image_url   TEXT,
    city_id             INTEGER         REFERENCES cities(id) ON DELETE SET NULL,
    is_verified         BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_provider_profiles_user_id ON provider_profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_provider_profiles_city_id ON provider_profiles (city_id);

DROP TRIGGER IF EXISTS trg_provider_profiles_updated_at ON provider_profiles;
CREATE TRIGGER trg_provider_profiles_updated_at
    BEFORE UPDATE ON provider_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Provider Industries
CREATE TABLE IF NOT EXISTS provider_industries (
    id              SERIAL      PRIMARY KEY,
    provider_id     INTEGER     NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,
    industry_id     INTEGER     NOT NULL REFERENCES industries(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, industry_id)
);

CREATE INDEX IF NOT EXISTS idx_provider_industries_provider ON provider_industries (provider_id);

-- Provider Skills
CREATE TABLE IF NOT EXISTS provider_skills (
    id              SERIAL      PRIMARY KEY,
    provider_id     INTEGER     NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,
    skill_id        INTEGER     NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_provider_skills_provider ON provider_skills (provider_id);

-- Provider Languages
CREATE TABLE IF NOT EXISTS provider_languages (
    id              SERIAL      PRIMARY KEY,
    provider_id     INTEGER     NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,
    language_id     INTEGER     NOT NULL REFERENCES languages(id) ON DELETE CASCADE,
    proficiency     SMALLINT    NOT NULL DEFAULT 1, -- 1=basic, 2=conversational, 3=fluent, 4=native
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider_id, language_id)
);

CREATE INDEX IF NOT EXISTS idx_provider_languages_provider ON provider_languages (provider_id);

-- Provider Documents
CREATE TABLE IF NOT EXISTS provider_documents (
    id              SERIAL      PRIMARY KEY,
    provider_id     INTEGER     NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,
    document_type   SMALLINT    NOT NULL DEFAULT 4, -- 1=id_proof, 2=certification, 3=portfolio, 4=other
    url             TEXT        NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_provider_documents_provider ON provider_documents (provider_id);

DROP TRIGGER IF EXISTS trg_provider_documents_updated_at ON provider_documents;
CREATE TRIGGER trg_provider_documents_updated_at
    BEFORE UPDATE ON provider_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Provider Experiences
CREATE TABLE IF NOT EXISTS provider_experiences (
    id          SERIAL          PRIMARY KEY,
    provider_id INTEGER         NOT NULL REFERENCES provider_profiles(id) ON DELETE CASCADE,
    brand_name  VARCHAR(150)    NOT NULL,
    role_name   VARCHAR(100)    NOT NULL,
    duration    VARCHAR(50),
    description TEXT,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_provider_experiences_provider ON provider_experiences (provider_id);

DROP TRIGGER IF EXISTS trg_provider_experiences_updated_at ON provider_experiences;
CREATE TRIGGER trg_provider_experiences_updated_at
    BEFORE UPDATE ON provider_experiences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
