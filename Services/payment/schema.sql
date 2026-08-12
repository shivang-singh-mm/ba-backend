-- =============================================================================
-- Payment Service — PostgreSQL Schema
-- File: Services/payment/schema.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS payments (
    id                  SERIAL          PRIMARY KEY,
    user_id             INTEGER         NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    amount              NUMERIC(12, 2)  NOT NULL CHECK (amount > 0),
    currency            VARCHAR(10)     NOT NULL DEFAULT 'INR',
    status              VARCHAR(50)     NOT NULL DEFAULT 'pending',
    -- status values: pending | success | failed | refunded | cancelled
    gateway             VARCHAR(50),    -- razorpay | stripe | payu | etc.
    gateway_payment_id  VARCHAR(255)    UNIQUE,
    gateway_order_id    VARCHAR(255),
    description         TEXT,
    metadata            JSONB           DEFAULT '{}',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id   ON payments (user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status    ON payments (status);
CREATE INDEX IF NOT EXISTS idx_payments_gateway   ON payments (gateway_payment_id) WHERE gateway_payment_id IS NOT NULL;

DROP TRIGGER IF EXISTS trg_payments_updated_at ON payments;
CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
