"""
Database Initialisation Script
--------------------------------
Runs all schema.sql files in the correct dependency order to create
all tables in your PostgreSQL database.

Usage:
    python scripts/init_db.py

Requires DATABASE_URL to be set in your .env file.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set. Check your .env file.")
    sys.exit(1)

# Schema files must be applied in dependency order:
#   users first (FK target), then auth (FKs to users), then payment, campaigns
SCHEMA_FILES = [
    "Services/user/schema.sql",
    "Services/location/schema.sql",
    "Services/industry/schema.sql",
    "Services/skill/schema.sql",
    "Services/language/schema.sql",
    "Services/provider/schema.sql",
    "Services/brand/schema.sql",
    "Services/auth/schema.sql",
    "Services/payment/schema.sql",
    "Services/campaigns/schema.sql",
    "Services/matching/schema.sql",
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_schema(conn, filepath: str):
    abs_path = os.path.join(BASE_DIR, filepath)
    with open(abs_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"  [OK] Applied: {filepath}")



def main():
    print(f"\nConnecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"ERROR: Could not connect — {e}")
        sys.exit(1)

    print("Running schema migrations...\n")
    try:
        for schema_file in SCHEMA_FILES:
            run_schema(conn, schema_file)
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Failed to apply schema — {e}")
        sys.exit(1)
    finally:
        conn.close()

    print("\nAll schemas applied successfully.")


if __name__ == "__main__":
    main()
