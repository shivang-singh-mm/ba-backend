"""
Seed Database Script
--------------------
Inserts default countries, states, and major cities (including Gurugram, Delhi, Mumbai, Bengaluru, etc.),
along with common industries, skills, and languages.

Usage:
    python scripts/seed_db.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set. Check your .env file.")
    sys.exit(1)


def seed():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check if user_id column exists on skills / languages / industries, else add if missing
        cur.execute("ALTER TABLE skills ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT 0;")
        cur.execute("ALTER TABLE languages ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT 0;")
        cur.execute("ALTER TABLE industries ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT 0;")
        
        # Ensure campaigns table columns exist
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS city_id INTEGER REFERENCES cities(id) ON DELETE SET NULL;")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS locality VARCHAR(255);")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS date DATE;")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS start_time TIME;")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS end_time TIME;")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS total_hours NUMERIC(6, 2);")
        cur.execute("ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;")
        conn.commit()

        print("Seeding locations...")
        # 1. Country: India
        cur.execute("""
            INSERT INTO countries (name, country_code, phone_code)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET country_code = EXCLUDED.country_code
            RETURNING id;
        """, ("India", "IN", "+91"))
        country_id = cur.fetchone()["id"]

        # 2. States
        states_data = [
            "Haryana",
            "Delhi",
            "Maharashtra",
            "Karnataka",
            "Tamil Nadu",
            "Telangana",
            "Uttar Pradesh",
            "West Bengal",
        ]
        state_ids = {}
        for state_name in states_data:
            cur.execute("""
                INSERT INTO states (name, country_id)
                VALUES (%s, %s)
                ON CONFLICT (name, country_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id;
            """, (state_name, country_id))
            state_ids[state_name] = cur.fetchone()["id"]

        # 3. Cities (including Gurugram)
        cities_data = [
            ("Gurugram", state_ids["Haryana"]),
            ("Faridabad", state_ids["Haryana"]),
            ("New Delhi", state_ids["Delhi"]),
            ("Delhi", state_ids["Delhi"]),
            ("Noida", state_ids["Uttar Pradesh"]),
            ("Greater Noida", state_ids["Uttar Pradesh"]),
            ("Ghaziabad", state_ids["Uttar Pradesh"]),
            ("Mumbai", state_ids["Maharashtra"]),
            ("Pune", state_ids["Maharashtra"]),
            ("Bengaluru", state_ids["Karnataka"]),
            ("Hyderabad", state_ids["Telangana"]),
            ("Chennai", state_ids["Tamil Nadu"]),
            ("Kolkata", state_ids["West Bengal"]),
        ]

        for city_name, state_id in cities_data:
            cur.execute("""
                INSERT INTO cities (name, state_id)
                VALUES (%s, %s)
                ON CONFLICT (name, state_id) DO NOTHING;
            """, (city_name, state_id))

        print("Seeding industries...")
        industries = [
            "FMCG / Food & Beverage",
            "Fashion & Apparel",
            "Consumer Electronics & Tech",
            "Automotive",
            "Events & Entertainment",
            "Retail & E-commerce",
            "Healthcare & Fitness",
            "Education & EdTech",
            "Real Estate & Hospitality",
            "Gaming & Esports",
        ]
        for ind in industries:
            cur.execute("""
                INSERT INTO industries (name, user_id)
                VALUES (%s, 0)
                ON CONFLICT (name) DO NOTHING;
            """, (ind,))

        print("Seeding skills...")
        skills = [
            "Product Demonstrator",
            "Flyer Distribution",
            "Event Anchor / Host",
            "Crowd Engagement",
            "Sampling & Tasting",
            "Lead Generation",
            "Booth Setup & Management",
            "Retail Merchandising",
            "Photography & Media",
            "Sales Promotion",
        ]
        for skill in skills:
            cur.execute("""
                INSERT INTO skills (name, user_id)
                VALUES (%s, 0)
                ON CONFLICT (name) DO NOTHING;
            """, (skill,))

        print("Seeding languages...")
        languages = [
            "English",
            "Hindi",
            "Punjabi",
            "Kannada",
            "Tamil",
            "Telugu",
            "Marathi",
            "Bengali",
            "Gujarati",
        ]
        for lang_name in languages:
            cur.execute("""
                INSERT INTO languages (name, user_id)
                VALUES (%s, 0)
                ON CONFLICT (name) DO NOTHING;
            """, (lang_name,))

        conn.commit()
        print("\nDatabase seeded successfully with Gurugram and metadata!")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    seed()
