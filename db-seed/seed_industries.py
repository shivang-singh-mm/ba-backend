"""
Seed Script: Industries
-----------------------
Modes:
  - recreate=False (default): Apply Services/industry/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP TABLE IF EXISTS industries CASCADE, apply schema.sql, then INSERT.
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

SCHEMA_FILE = "Services/industry/schema.sql"

INDUSTRIES = [
    "FMCG & Consumer Goods",
    "Beverages & Spirits",
    "Fashion & Apparel",
    "Footwear & Sportswear",
    "Consumer Electronics & Gadgets",
    "Automotive & Electric Vehicles",
    "Beauty & Personal Care",
    "Fintech & Banking",
    "Gaming & Esports",
    "Quick Commerce & E-commerce",
    "Hospitality, Food & Restaurants",
    "Travel & Tourism",
    "Entertainment & Media",
    "Healthcare & Wellness",
    "EdTech & Education",
    "Real Estate & Co-working",
    "Telecom & Internet Services",
    "Luxury & Watches",
    "Fitness & Nutrition",
    "Sustainability & Eco-Products",
]


def seed_industries(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            if recreate:
                print("  [industries] Force deleting existing industries table (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS industries CASCADE;")

            # Load and execute original schema.sql
            execute_schema_file(cur, SCHEMA_FILE)

            for ind in INDUSTRIES:
                cur.execute(
                    """
                    INSERT INTO industries (name, user_id)
                    VALUES (%s, 0)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (ind,),
                )

            cur.execute("SELECT COUNT(*) FROM industries;")
            count = cur.fetchone()[0]

        conn.commit()
        print(f"  [OK] Industries seeded. Total industries in DB: {count}")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed industries")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate table before seeding")
    args = parser.parse_args()
    seed_industries(recreate=args.recreate)
