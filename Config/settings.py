import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    # ── Flask ──────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30))
    )

    # ── PostgreSQL (psycopg2) ──────────────────────────────────────────────────
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/brandactivation_dev"
    )
    DB_POOL_MIN = int(os.environ.get("DB_POOL_MIN", 2))
    DB_POOL_MAX = int(os.environ.get("DB_POOL_MAX", 10))

    # ── OTP ────────────────────────────────────────────────────────────────────
    OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
    OTP_LENGTH = int(os.environ.get("OTP_LENGTH", 6))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 3))

    # ── Email / SMTP ───────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "BrandActivation <no-reply@brandactivation.com>"
    )

    # ── AI / OpenRouter ────────────────────────────────────────────────────────
    OPENROUTER_API_KEY   = os.environ.get("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL     = os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
    OPENROUTER_SITE_URL  = os.environ.get("OPENROUTER_SITE_URL", "http://localhost:5000")
    OPENROUTER_SITE_NAME = os.environ.get("OPENROUTER_SITE_NAME", "BrandActivation")

    # ── App ────────────────────────────────────────────────────────────────────
    APP_NAME = os.environ.get("APP_NAME", "BrandActivation")

    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/brandactivation_test"
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    DATABASE_URL = os.environ.get("DATABASE_URL")


config = {
    "development":  DevelopmentConfig,
    "testing":      TestingConfig,
    "production":   ProductionConfig,
    "default":      DevelopmentConfig,
}
