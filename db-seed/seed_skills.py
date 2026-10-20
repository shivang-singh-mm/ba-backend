"""
Seed Script: Skills
-------------------
Modes:
  - recreate=False (default): Apply Services/skill/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP TABLE IF EXISTS skills CASCADE, apply schema.sql, then INSERT.
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

SCHEMA_FILE = "Services/skill/schema.sql"

SKILLS = [
    # Experiential / On-ground Skills
    "Brand Ambassadorship",
    "Product Sampling & Demonstration",
    "Event Emcee / Hosting",
    "Public Speaking & Crowd Engagement",
    "Lead Generation & Data Capture",
    "Flyer & Merchandise Distribution",
    "Flash Mob & Performance",
    "VIP Guest Handling & Hospitality",
    "Registration Desk Management",
    "Booth & Stall Management",
    # Technical & Creative Skills
    "Live Social Media Coverage",
    "Event Photography & Videography",
    "Audio / Visual Equipment Setup",
    "Stage & Lighting Management",
    "POS & Cash Handling",
    # Specialized / Sales Skills
    "Direct Sales & Pitching",
    "Bilingual Communication",
    "Conflict Resolution & Crowd Control",
    "Product Knowledge Training",
    "Gamification & Interactive Activities",
]


def seed_skills(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            if recreate:
                print("  [skills] Force deleting existing skills table (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS skills CASCADE;")

            # Load and execute original schema.sql
            execute_schema_file(cur, SCHEMA_FILE)

            for skill in SKILLS:
                cur.execute(
                    """
                    INSERT INTO skills (name, user_id)
                    VALUES (%s, 0)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (skill,),
                )

            cur.execute("SELECT COUNT(*) FROM skills;")
            count = cur.fetchone()[0]

        conn.commit()
        print(f"  [OK] Skills seeded. Total skills in DB: {count}")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed skills")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate table before seeding")
    args = parser.parse_args()
    seed_skills(recreate=args.recreate)
