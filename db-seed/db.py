import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

COMMON_TRIGGER_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment or .env file.")
    return psycopg2.connect(DATABASE_URL)


def ensure_common_functions(cur):
    """
    Ensures shared utility functions (like update_updated_at_column) exist
    before any service trigger tries to reference them.
    """
    cur.execute(COMMON_TRIGGER_FUNCTION_SQL)


def execute_schema_file(cur, relative_schema_path: str):
    """
    Reads and executes an existing service schema SQL file.
    Ensures prerequisite DB functions exist first.
    Example: execute_schema_file(cur, "Services/location/schema.sql")
    """
    ensure_common_functions(cur)

    abs_path = os.path.join(PROJECT_ROOT, relative_schema_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Schema file not found at: {abs_path}")
    with open(abs_path, "r", encoding="utf-8") as f:
        sql = f.read()
    cur.execute(sql)
