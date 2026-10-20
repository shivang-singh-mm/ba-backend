"""
Seed Script: Brands (100 Authentic Brands)
------------------------------------------
Modes:
  - recreate=False (default): Apply Services/brand/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP tables CASCADE, apply schema.sql, then INSERT.
"""

import sys
import os
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from db import get_db_connection, execute_schema_file
except ImportError:
    from .db import get_db_connection, execute_schema_file

USER_SCHEMA_FILE = "Services/user/schema.sql"
BRAND_SCHEMA_FILE = "Services/brand/schema.sql"

# Curated list of 100 realistic brands across sectors
BRAND_NAMES = [
    # Tech & Electronics
    "Samsung Electronics", "Apple India", "OnePlus", "Sony India", "Xiaomi", 
    "Dell Technologies", "HP India", "Asus ROG", "Boat Lifestyle", "Noise",
    "Realme", "Lenovo", "Logitech", "Nothing Tech", "JBL Audio",
    # FMCG & Food/Beverage
    "Red Bull", "Monster Energy", "Coca-Cola", "PepsiCo", "Nestle India",
    "Mondelez Cadbury", "Britannia Industries", "ITC Limited", "Amul", "Paper Boat",
    "Raw Pressery", "Epigamia", "Blue Tokai Coffee", "Third Wave Coffee", "Starbucks India",
    "Bira 91", "Kingfisher", "Heineken", "Oatly", "Beyond Meat",
    # Fashion, Sportswear & Apparel
    "Nike", "Adidas", "Puma", "Under Armour", "Zara India",
    "H&M", "Levi Strauss", "Fabindia", "Decathlon", "Snitch",
    "Rare Rabbit", "Bata India", "Wildcraft", "Vans", "Converse",
    # Beauty & Personal Care
    "Nykaa", "Sugar Cosmetics", "Mamaearth", "The Derma Co", "L'Oreal Paris",
    "Plum Goodness", "mCaffeine", "Bombay Shaving Company", "Beardo", "Forest Essentials",
    "Kama Ayurveda", "Minimalist", "Maybelline", "Clinique", "Nivea India",
    # Quick Commerce, E-commerce & Delivery
    "Zepto", "Blinkit", "Swiggy Instamart", "Zomato", "Myntra",
    "Flipkart", "Amazon India", "Ajio", "Tata CLiQ", "Urban Company",
    # Automotive & EV
    "Tata Motors", "Ola Electric", "Ather Energy", "Mahindra & Mahindra", "Hyundai India",
    "Maruti Suzuki", "Royal Enfield", "KTM India", "TVS Motor", "BMW India",
    # Fintech & Banking
    "CRED", "Groww", "Zerodha", "PhonePe", "Paytm",
    "HDFC Bank", "ICICI Bank", "Razorpay", "Jupiter Money", "Fi Money",
    # Gaming, Fitness & Lifestyle
    "Razer Gaming", "Krafton India", "Cult.fit", "Gold's Gym", "Anytime Fitness",
    "Lego India", "Hamleys", "Sennheiser", "GoPro", "Ray-Ban",
]

TAGLINES = [
    "Leading experiential activations and high-engagement roadshows.",
    "Innovating campus ambassadorship and experiential youth marketing.",
    "Connecting urban consumers with next-generation product sampling.",
    "Driving festive pop-ups, retail activations, and customer delight.",
    "Pioneering digital-first on-ground launch events and fan experiences.",
    "Delivering immersive retail store takeovers and dynamic brand awareness.",
]


def seed_brands(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            # Ensure users table exists first
            execute_schema_file(cur, USER_SCHEMA_FILE)

            if recreate:
                print("  [brands] Force deleting existing brand tables (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS brand_locations CASCADE;")
                cur.execute("DROP TABLE IF EXISTS brand_industries CASCADE;")
                cur.execute("DROP TABLE IF EXISTS brand_profiles CASCADE;")

            execute_schema_file(cur, BRAND_SCHEMA_FILE)

            # Get available cities and industries
            cur.execute("SELECT id FROM cities;")
            city_ids = [r[0] for r in cur.fetchall()]
            if not city_ids:
                raise ValueError("Cities table is empty! Please run seed_cities first.")

            cur.execute("SELECT id FROM industries;")
            industry_ids = [r[0] for r in cur.fetchall()]
            if not industry_ids:
                raise ValueError("Industries table is empty! Please run seed_industries first.")

            created_count = 0
            for i, brand_name in enumerate(BRAND_NAMES, start=1):
                clean_slug = "".join(c.lower() for c in brand_name if c.isalnum())
                email = f"contact@{clean_slug}.demo"
                phone = f"+9198{i:08d}"

                # 1. Insert or get User (role='brand')
                cur.execute(
                    """
                    INSERT INTO users (name, email, phone, role, is_active)
                    VALUES (%s, %s, %s, 'brand', TRUE)
                    ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                    """,
                    (f"{brand_name} Rep", email, phone),
                )
                user_id = cur.fetchone()[0]

                # 2. Insert or update brand_profile
                h_city = random.choice(city_ids)
                desc = f"{brand_name} - {random.choice(TAGLINES)}"
                logo_url = f"https://api.dicebear.com/7.x/identicon/svg?seed={clean_slug}"
                website = f"https://www.{clean_slug}.demo"

                cur.execute(
                    """
                    INSERT INTO brand_profiles (user_id, brand_name, brand_description, brand_logo_url, brand_website, city_id, is_verified, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE)
                    ON CONFLICT (user_id) DO UPDATE SET
                        brand_name = EXCLUDED.brand_name,
                        brand_description = EXCLUDED.brand_description,
                        brand_logo_url = EXCLUDED.brand_logo_url,
                        brand_website = EXCLUDED.brand_website,
                        city_id = EXCLUDED.city_id
                    RETURNING id;
                    """,
                    (user_id, brand_name, desc, logo_url, website, h_city),
                )
                brand_id = cur.fetchone()[0]

                # 3. Assign 1-2 industries
                cur.execute("DELETE FROM brand_industries WHERE brand_id = %s;", (brand_id,))
                chosen_inds = random.sample(industry_ids, k=min(len(industry_ids), random.randint(1, 2)))
                for idx, ind_id in enumerate(chosen_inds):
                    cur.execute(
                        "INSERT INTO brand_industries (brand_id, industry_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (brand_id, ind_id, idx == 0),
                    )

                # 4. Assign 1-3 operational locations
                cur.execute("DELETE FROM brand_locations WHERE brand_id = %s;", (brand_id,))
                chosen_cities = random.sample(city_ids, k=min(len(city_ids), random.randint(1, 3)))
                if h_city not in chosen_cities:
                    chosen_cities[0] = h_city
                for idx, c_id in enumerate(chosen_cities):
                    cur.execute(
                        "INSERT INTO brand_locations (brand_id, city_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (brand_id, c_id, c_id == h_city),
                    )

                created_count += 1

            conn.commit()
            print(f"  [OK] Successfully seeded {created_count} brand accounts and profiles!")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed brand accounts")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate brand tables before seeding")
    args = parser.parse_args()
    seed_brands(recreate=args.recreate)
