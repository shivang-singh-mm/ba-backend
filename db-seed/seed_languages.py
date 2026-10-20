"""
Seed Script: Languages
----------------------
Modes:
  - recreate=False (default): Apply Services/language/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP TABLE IF EXISTS languages CASCADE, apply schema.sql, then INSERT.
"""

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from db import get_db_connection, execute_schema_file
except ImportError:
    from .db import get_db_connection, execute_schema_file

SCHEMA_FILE = "Services/language/schema.sql"

LANGUAGES = [
    "English",
    "Hindi",
    "Marathi",
    "Kannada",
    "Tamil",
    "Telugu",
    "Bengali",
    "Gujarati",
    "Punjabi",
    "Malayalam",
    "Odia",
    "Spanish",
    "French",
    "German",
    "Arabic",
]


def seed_languages(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            if recreate:
                print("  [languages] Force deleting existing languages table (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS languages CASCADE;")

            # Load and execute original schema.sql
            execute_schema_file(cur, SCHEMA_FILE)

            for lang in LANGUAGES:
                cur.execute(
                    """
                    INSERT INTO languages (name, user_id)
                    VALUES (%s, 0)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (lang,),
                )

            cur.execute("SELECT COUNT(*) FROM languages;")
            count = cur.fetchone()[0]

        conn.commit()
        print(f"  [OK] Languages seeded. Total languages in DB: {count}")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed languages")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate table before seeding")
    args = parser.parse_args()
    seed_languages(recreate=args.recreate)
