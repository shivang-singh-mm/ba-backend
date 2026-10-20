"""
Seed Script: Cities & Locations (Countries, States, Cities)
-----------------------------------------------------------
Modes:
  - recreate=False (default): Apply Services/location/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP tables CASCADE, apply Services/location/schema.sql, then INSERT.
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

SCHEMA_FILE = "Services/location/schema.sql"

COUNTRIES = [
    {"name": "India", "country_code": "IN", "phone_code": "+91"},
    {"name": "United States", "country_code": "US", "phone_code": "+1"},
    {"name": "United Kingdom", "country_code": "GB", "phone_code": "+44"},
    {"name": "United Arab Emirates", "country_code": "AE", "phone_code": "+971"},
]

STATES = [
    # India
    {"country_code": "IN", "name": "Maharashtra"},
    {"country_code": "IN", "name": "Delhi"},
    {"country_code": "IN", "name": "Karnataka"},
    {"country_code": "IN", "name": "Tamil Nadu"},
    {"country_code": "IN", "name": "Telangana"},
    {"country_code": "IN", "name": "West Bengal"},
    {"country_code": "IN", "name": "Gujarat"},
    {"country_code": "IN", "name": "Rajasthan"},
    {"country_code": "IN", "name": "Uttar Pradesh"},
    {"country_code": "IN", "name": "Goa"},
    # US
    {"country_code": "US", "name": "California"},
    {"country_code": "US", "name": "New York"},
    {"country_code": "US", "name": "Texas"},
    # UAE
    {"country_code": "AE", "name": "Dubai"},
]

CITIES = [
    # Maharashtra
    {"state_name": "Maharashtra", "name": "Mumbai"},
    {"state_name": "Maharashtra", "name": "Pune"},
    {"state_name": "Maharashtra", "name": "Nagpur"},
    # Delhi
    {"state_name": "Delhi", "name": "New Delhi"},
    {"state_name": "Delhi", "name": "Noida"},
    {"state_name": "Delhi", "name": "Gurugram"},
    # Karnataka
    {"state_name": "Karnataka", "name": "Bengaluru"},
    {"state_name": "Karnataka", "name": "Mysuru"},
    # Tamil Nadu
    {"state_name": "Tamil Nadu", "name": "Chennai"},
    {"state_name": "Tamil Nadu", "name": "Coimbatore"},
    # Telangana
    {"state_name": "Telangana", "name": "Hyderabad"},
    # West Bengal
    {"state_name": "West Bengal", "name": "Kolkata"},
    # Gujarat
    {"state_name": "Gujarat", "name": "Ahmedabad"},
    {"state_name": "Gujarat", "name": "Surat"},
    # Rajasthan
    {"state_name": "Rajasthan", "name": "Jaipur"},
    {"state_name": "Rajasthan", "name": "Udaipur"},
    # Uttar Pradesh
    {"state_name": "Uttar Pradesh", "name": "Lucknow"},
    {"state_name": "Uttar Pradesh", "name": "Varanasi"},
    # Goa
    {"state_name": "Goa", "name": "Panaji"},
    # US
    {"state_name": "California", "name": "San Francisco"},
    {"state_name": "California", "name": "Los Angeles"},
    {"state_name": "New York", "name": "New York City"},
    {"state_name": "Texas", "name": "Austin"},
    # UAE
    {"state_name": "Dubai", "name": "Dubai City"},
]


def seed_cities(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            if recreate:
                print("  [cities] Force deleting existing location tables (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS cities CASCADE;")
                cur.execute("DROP TABLE IF EXISTS states CASCADE;")
                cur.execute("DROP TABLE IF EXISTS countries CASCADE;")

            # Load and execute original schema.sql
            execute_schema_file(cur, SCHEMA_FILE)

            # Insert Countries
            for c in COUNTRIES:
                cur.execute(
                    """
                    INSERT INTO countries (name, country_code, phone_code)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO UPDATE 
                    SET country_code = EXCLUDED.country_code, phone_code = EXCLUDED.phone_code;
                    """,
                    (c["name"], c["country_code"], c["phone_code"]),
                )

            # Map country_code -> id
            cur.execute("SELECT country_code, id FROM countries;")
            country_map = {row[0]: row[1] for row in cur.fetchall()}

            # Insert States
            for s in STATES:
                c_id = country_map.get(s["country_code"])
                if c_id:
                    cur.execute(
                        """
                        INSERT INTO states (name, country_id)
                        VALUES (%s, %s)
                        ON CONFLICT (name, country_id) DO NOTHING;
                        """,
                        (s["name"], c_id),
                    )

            # Map state_name -> id
            cur.execute("SELECT name, id FROM states;")
            state_map = {row[0]: row[1] for row in cur.fetchall()}

            # Insert Cities
            for city in CITIES:
                s_id = state_map.get(city["state_name"])
                if s_id:
                    cur.execute(
                        """
                        INSERT INTO cities (name, state_id)
                        VALUES (%s, %s)
                        ON CONFLICT (name, state_id) DO NOTHING;
                        """,
                        (city["name"], s_id),
                    )

            cur.execute("SELECT COUNT(*) FROM cities;")
            count = cur.fetchone()[0]

        conn.commit()
        print(f"  [OK] Location data seeded. Total cities in DB: {count}")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed cities/locations")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate tables before seeding")
    args = parser.parse_args()
    seed_cities(recreate=args.recreate)
