"""
Seed Script: Candidates (300 Authentic Providers with Experiences)
-------------------------------------------------------------------
Modes:
  - recreate=False (default): Apply Services/provider/schema.sql (IF NOT EXISTS), then INSERT.
  - recreate=True: DROP tables CASCADE, apply schema.sql, then INSERT.
"""

import sys
import os
import random
from datetime import date, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from db import get_db_connection, execute_schema_file
except ImportError:
    from .db import get_db_connection, execute_schema_file

USER_SCHEMA_FILE = "Services/user/schema.sql"
PROVIDER_SCHEMA_FILE = "Services/provider/schema.sql"

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Rohan", "Atharv", "Kabir", "Dhruv", "Aryan", "Aayush", "Rudra", "Dev", "Kavya",
    "Ananya", "Diya", "Isha", "Rhea", "Tara", "Tanvi", "Saanvi", "Pooja", "Simran", "Nisha",
    "Kriti", "Aditi", "Meera", "Avani", "Zoya", "Sara", "Anika", "Sneha", "Payal", "Roshni",
    "Rahul", "Amit", "Vikram", "Gaurav", "Siddharth", "Kunal", "Manish", "Varun", "Abhishek", "Naveen",
    "Priya", "Sunita", "Deepika", "Shreya", "Kritika", "Preeti", "Kavita", "Ritu", "Swati", "Neha"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Malhotra", "Mehta", "Kapoor", "Joshi", "Patel", "Shah", "Reddy",
    "Nair", "Iyer", "Rao", "Choudhury", "Bose", "Das", "Singh", "Bhatia", "Saxena", "Chawla",
    "Bansal", "Mishra", "Pandey", "Agarwal", "Kulkarni", "Deshmukh", "Chauhan", "Yadav", "Tiwari", "Pillai"
]

OCCUPATIONS = [
    "Lead Brand Ambassador",
    "Experiential Marketing Host",
    "Event Emcee & Presenter",
    "Senior Product Demonstrator",
    "Field Marketing Specialist",
    "Promotional Model & Hostess",
    "Flash Mob Choreographer & Dancer",
    "Tech Booth Representative",
    "Campus Ambassador Lead",
    "Sampling Coordinator",
]

PAST_BRANDS = [
    "Red Bull", "Samsung", "OnePlus", "Nike", "Puma", "Zepto", "Zomato", "Boat", "Coca-Cola",
    "CRED", "Decathlon", "Starbucks", "Sugar Cosmetics", "Mamaearth", "Bira 91", "Tata Motors"
]

EXPERIENCE_TEMPLATES = [
    ("Lead Product Specialist", "3 months", "Managed customer interactions, hands-on device trials, and captured 500+ qualified leads during the flagship mall roadshow."),
    ("Brand Ambassador", "1 month", "Drove sampling operations across college campuses, engaging with over 2,000 students and explaining product USPs."),
    ("Stage Emcee & Host", "2 weeks", "Hosted energetic crowd engagements, mini-games, and stage announcements during the high-footfall festive pop-up."),
    ("VIP Hospitality Coordinator", "1 month", "Welcomed corporate guests, media dignitaries, and handled registration desks seamlessly."),
    ("Tech Booth Demonstrator", "2 months", "Demonstrated software and mobile app features, onboarded new active users, and distributed merchandise."),
]


def seed_candidates(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            # Ensure users table exists first
            execute_schema_file(cur, USER_SCHEMA_FILE)

            if recreate:
                print("  [candidates] Force deleting existing provider tables (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS provider_experiences CASCADE;")
                cur.execute("DROP TABLE IF EXISTS provider_documents CASCADE;")
                cur.execute("DROP TABLE IF EXISTS provider_languages CASCADE;")
                cur.execute("DROP TABLE IF EXISTS provider_skills CASCADE;")
                cur.execute("DROP TABLE IF EXISTS provider_industries CASCADE;")
                cur.execute("DROP TABLE IF EXISTS provider_profiles CASCADE;")

            execute_schema_file(cur, PROVIDER_SCHEMA_FILE)

            # Retrieve taxonomy IDs
            cur.execute("SELECT id FROM cities;")
            city_ids = [r[0] for r in cur.fetchall()]
            if not city_ids:
                raise ValueError("Cities table is empty! Please run seed_cities first.")

            cur.execute("SELECT id FROM industries;")
            industry_ids = [r[0] for r in cur.fetchall()]
            if not industry_ids:
                raise ValueError("Industries table is empty! Please run seed_industries first.")

            cur.execute("SELECT id FROM skills;")
            skill_ids = [r[0] for r in cur.fetchall()]
            if not skill_ids:
                raise ValueError("Skills table is empty! Please run seed_skills first.")

            cur.execute("SELECT id FROM languages;")
            language_ids = [r[0] for r in cur.fetchall()]
            if not language_ids:
                raise ValueError("Languages table is empty! Please run seed_languages first.")

            created_count = 0
            for i in range(1, 301):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                full_name = f"{first} {last}"
                email = f"{first.lower()}.{last.lower()}.{i}@talent.demo"
                phone = f"+9191{i:08d}"

                # 1. Create or get user
                cur.execute(
                    """
                    INSERT INTO users (name, email, phone, role, is_active)
                    VALUES (%s, %s, %s, 'user', TRUE)
                    ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                    """,
                    (full_name, email, phone),
                )
                user_id = cur.fetchone()[0]

                # 2. Create provider profile
                p_type = random.choices([1, 2, 3], weights=[0.65, 0.10, 0.25])[0] # 1=ind, 2=agency, 3=freelancer
                occ = random.choice(OCCUPATIONS)
                gender = random.choice(["Male", "Female", "Other"])
                birth_year = random.randint(1995, 2004)
                dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))
                city_id = random.choice(city_ids)
                avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={first}{last}{i}"
                desc = (
                    f"Dynamic and charismatic {occ} with extensive experience representing premier brands in retail, "
                    f"campus ambassadorship, and consumer pop-ups."
                )

                cur.execute(
                    """
                    INSERT INTO provider_profiles (
                        user_id, provider_type, description, current_occupation,
                        date_of_birth, gender, profile_image_url, city_id, is_verified, is_active
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, TRUE)
                    ON CONFLICT (user_id) DO UPDATE SET
                        provider_type = EXCLUDED.provider_type,
                        description = EXCLUDED.description,
                        current_occupation = EXCLUDED.current_occupation,
                        city_id = EXCLUDED.city_id
                    RETURNING id;
                    """,
                    (user_id, p_type, desc, occ, dob, gender, avatar, city_id),
                )
                provider_id = cur.fetchone()[0]

                # 3. Associate 1-3 Industries
                cur.execute("DELETE FROM provider_industries WHERE provider_id = %s;", (provider_id,))
                chosen_inds = random.sample(industry_ids, k=min(len(industry_ids), random.randint(1, 3)))
                for ind_id in chosen_inds:
                    cur.execute(
                        "INSERT INTO provider_industries (provider_id, industry_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                        (provider_id, ind_id),
                    )

                # 4. Associate 2-5 Skills
                cur.execute("DELETE FROM provider_skills WHERE provider_id = %s;", (provider_id,))
                chosen_skills = random.sample(skill_ids, k=min(len(skill_ids), random.randint(2, 5)))
                for sk_id in chosen_skills:
                    cur.execute(
                        "INSERT INTO provider_skills (provider_id, skill_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                        (provider_id, sk_id),
                    )

                # 5. Associate 1-3 Languages with proficiency
                cur.execute("DELETE FROM provider_languages WHERE provider_id = %s;", (provider_id,))
                chosen_langs = random.sample(language_ids, k=min(len(language_ids), random.randint(1, 3)))
                for l_id in chosen_langs:
                    prof = random.choice([2, 3, 4]) # 2=conversational, 3=fluent, 4=native
                    cur.execute(
                        "INSERT INTO provider_languages (provider_id, language_id, proficiency) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                        (provider_id, l_id, prof),
                    )

                # 6. Associate 1-3 past experiences in provider_experiences (Critical for AI matching!)
                cur.execute("DELETE FROM provider_experiences WHERE provider_id = %s;", (provider_id,))
                num_exps = random.randint(1, 3)
                for _ in range(num_exps):
                    b_name = random.choice(PAST_BRANDS)
                    role, dur, exp_desc = random.choice(EXPERIENCE_TEMPLATES)
                    cur.execute(
                        """
                        INSERT INTO provider_experiences (provider_id, brand_name, role_name, duration, description)
                        VALUES (%s, %s, %s, %s, %s);
                        """,
                        (provider_id, b_name, role, dur, exp_desc),
                    )

                created_count += 1

            conn.commit()
            print(f"  [OK] Successfully seeded {created_count} candidate accounts and provider profiles!")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed candidate provider accounts")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate provider tables before seeding")
    args = parser.parse_args()
    seed_candidates(recreate=args.recreate)
