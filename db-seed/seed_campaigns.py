"""
Seed Script: Campaigns (50 Realistic On-Ground Campaigns)
--------------------------------------------------------
Populates 50 rich campaigns with dates ranging strictly between
25 October 2026 and 04 November 2026 across major Indian cities,
linked with real seeded brands, products, venues, audiences, and talent needs.
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

CAMPAIGN_SCHEMA_FILE = "Services/campaigns/schema.sql"

# ── Reference Taxonomies ───────────────────────────────────────────────────────

CAMPAIGN_TYPES_SEED = [
    ("Mall Activation", "High-footfall interactive setups in premier shopping centers"),
    ("College Fest / Campus Roadshow", "Targeted youth experiential drives across premier college campuses"),
    ("Corporate Park Demo Day", "Lunch-hour tech and lifestyle trial setups in major IT and business parks"),
    ("Pop-up Store / Kiosk", "High-conversion experiential booths with sampling and instant commerce"),
    ("Product Sampling Drive", "Mass direct-to-consumer product tastings and experiential trials"),
    ("Festival Pop-up Experience", "Diwali and festive holiday experiential brand takeovers"),
    ("Metro Station Transit Booth", "High-velocity commuter sampling and digital couponing"),
    ("Flash Mob & Live Street Action", "High-energy crowd performance and viral on-ground visual stunts"),
]

VENUE_TYPES_SEED = [
    ("Shopping Mall / Retail Atrium", "Air-conditioned premier consumer retail destinations"),
    ("University / College Campus", "Auditoriums, open quads, and campus fest arenas"),
    ("Tech Park / IT Business Hub", "Corporate cafeteria courtyards and central tech park plazas"),
    ("High Street Promenade", "Bustling lifestyle shopping avenues and popular pedestrian plazas"),
    ("Transit Hub / Metro Station", "Concourse and exit areas of tier-1 metro stations"),
    ("Exhibition Ground / Convention Center", "Expo pavilions and large-scale convention centers"),
]

CAMPAIGN_TITLES_AND_PRODUCTS = [
    # Tech
    ("Apple iPhone 18 Pro Showcase & Studio Experience", "iPhone 18 Pro", "Next-gen computational photography and AI demonstration.", "https://apple.com/in", "Free 1-on-1 photography masterclass with Apple pros."),
    ("Samsung Galaxy Z Fold 7 Hands-on Experience Zone", "Galaxy Z Fold 7", "Dual-folding display smartphone with flagship multitasking.", "https://samsung.com/in", "Pre-book voucher worth ₹5,000 + free Buds."),
    ("OnePlus 15 Flagship Fan Pop-up & Gaming Tournament", "OnePlus 15", "Ultra-fast charging smartphone powered by latest flagship chipset.", "https://oneplus.in", "Win exclusive OnePlus merchandise and gaming accessories."),
    ("Nothing Phone (3) Transparent Design Lounge", "Nothing Phone (3)", "Signature glyph interface smartphone with minimalist design.", "https://nothing.tech", "Limited edition Nothing Earbuds discount coupon."),
    ("Asus ROG Strix Mobile Esports Battleground", "ROG Phone 9", "High-performance gaming phone with ultrasonic triggers.", "https://asus.com/in", "Hourly prize pool of ₹10,000 for top scores."),
    ("Boat Lifestyle Rockerz Wireless Audio Experience", "Boat Rockerz Pro", "Spatial audio wireless active noise cancelling headphones.", "https://boat-lifestyle.com", "Buy 1 Get 1 free at the promotional booth."),
    ("Dell Alienware Gaming Arena Takeover", "Alienware M18", "Ultra-tier PC gaming laptops with high-refresh screens.", "https://dell.com/in", "Play against pro esports streamers on stage."),
    ("Sony PlayStation 5 Pro FIFA Street Tournament", "PS5 Pro Console", "4K 120FPS console gaming with DualSense haptics.", "https://sony.co.in", "Winner gets signed football jerseys and game passes."),

    # Beverage & FMCG
    ("Red Bull Dance Your Style Campus Qualifier", "Red Bull Energy Drink", "Vitalizes body and mind for dancers, gamers, and athletes.", "https://redbull.com/in", "Chilled sampling can + VIP passes to the national finals."),
    ("Monster Energy Motocross Virtual VR Experience", "Monster Ultra", "Zero sugar crisp citrus energy drink.", "https://monsterenergy.com", "Free VR racing simulator ride + Monster snapback caps."),
    ("Bira 91 Octoberfest Craft Tasting Pop-up", "Bira 91 White & Gold", "Refreshing artisanal wheat beer.", "https://bira91.com", "Flight of 3 taster pours + custom beer mug."),
    ("Blue Tokai Pour-Over Coffee Brewing Bar", "Specialty Arabica Roasted Beans", "Single-origin pour-over artisanal roasted beans.", "https://bluetokai.com", "Complimentary freshly brewed cup + 15% retail pack discount."),
    ("Third Wave Coffee Nitro Cold Brew Station", "Nitro Cold Brew Can", "Velvety nitrogen-infused cold brew coffee.", "https://thirdwavecoffee.in", "Sample our newest seasonal vanilla blend."),
    ("Starbucks Festive Caramel Macchiato Tasting Booth", "Holiday Blend Macchiato", "Warm festive espresso beverage with caramel drizzle.", "https://starbucks.in", "Free holiday beverage upgrade coupon on the app."),
    ("Coca-Cola Festive Celebration Diner Hub", "Coke Zero & Original", "Chilled refreshing classic cola beverage.", "https://coca-cola.com/in", "Free personalized Coke can with your name printed."),
    ("Epigamia Greek Yogurt Protein Smoothie Bar", "High Protein Greek Yogurt", "Low-fat probiotic rich yogurt smoothies.", "https://epigamia.com", "Free smoothie samples + fitness shaker bottle."),
    ("Raw Pressery Cold Pressed Juice Detox Bar", "Val-Orange Cold-Pressed Juice", "100% pure cold-pressed fruit juices without preservatives.", "https://rawpressery.com", "Complimentary 200ml tasting bottle."),
    ("Paper Boat Festive Thandai & Aamras Sampling", "Paper Boat Aamras", "Nostalgic authentic Indian fruit drinks.", "https://paperboatdrinks.com", "Free traditional festive beverage pouches."),
    ("Cadbury Silk Secret Sweetness Booth", "Dairy Milk Silk Bubbly", "Smooth velvety chocolate crafted with rich cocoa.", "https://cadbury.in", "Personalized festive message wrapper on every bar."),

    # Fashion & Footwear
    ("Nike Air Max Run Club & Gait Analysis Station", "Nike Air Max 2026", "Dynamic air-cushioned running shoes.", "https://nike.com/in", "Free computerized 3D foot strike gait analysis."),
    ("Adidas Ultraboost Energy Bounce Arena", "Ultraboost Light", "High-energy return marathon running footwear.", "https://adidas.co.in", "Test sprint challenge to win Adidas running tees."),
    ("Puma Nitro Speed Challenge & Padel Court", "Puma Deviate Nitro", "Carbon-plated lightweight road racing shoe.", "https://in.puma.com", "Beat the target sprint time and win 50% discount."),
    ("Decathlon Weekend Multisport Festival", "Kiprun Running Range", "Accessible performance sporting apparel and gear.", "https://decathlon.in", "Try 5 sports challenges to win instant sports vouchers."),
    ("Zara Autumn/Winter Streetwear Styling Studio", "Zara Studio Collection", "Contemporary modern cuts and structured outerwear.", "https://zara.com/in", "Free 15-min consultation with celebrity stylists."),
    ("H&M Sustainable Fashion Upcycling Lounge", "Conscious Collection", "Organic and recycled cotton daily streetwear.", "https://hm.com/in", "Bring old clothes for an instant ₹500 shopping voucher."),
    ("Snitch Urban Streetwear Capsule Pop-Up", "Snitch Oversized Tees", "Gen-Z focused oversized printed tees and cargo pants.", "https://snitch.co.in", "Free bucket hat with every on-ground purchase."),

    # Beauty & Personal Care
    ("Nykaa Glamour Festive Makeover Studio", "Nykaa Matte To Last Liquid Lipstick", "Long-lasting transferproof matte lip colours.", "https://nykaa.com", "Complimentary 10-minute festive makeover by pro artists."),
    ("Sugar Cosmetics Bold & Free Lip Masterclass", "Sugar Smudge Me Not", "Vibrant pigment waterproof lipsticks.", "https://sugarcosmetics.com", "Free makeup pouch with any 2 products purchased."),
    ("Mamaearth Plant Goodness Organic Skin Bar", "Vitamin C Face Glow Serum", "Toxin-free, natural skincare made with safe ingredients.", "https://mamaearth.in", "Get a free mini glow serum + plant a tree in your name."),
    ("The Derma Co Science-Backed Skin Assessment", "10% Niacinamide Serum", "Dermatologist-designed formulas for clear radiant skin.", "https://thedermaco.com", "Free AI skin analyzer scan with customized skincare plan."),
    ("Forest Essentials Ayurvedic Luxury Rituals", "Soundarya Radiance Cream", "Traditional Vedic beauty elixirs with 24K gold bhasma.", "https://forestessentialsindia.com", "Mini ayurvedic hand massage & sample trial kit."),
    ("mCaffeine Caffeinated Glow Lounge", "Coffee Body Scrub", "Raw coffee body scrub for de-tanning and exfoliation.", "https://mcaffeine.com", "Try the coffee scrub bar + win customized bath hampers."),
    ("Bombay Shaving Company Grooming Bar", "Precision 6 Shaving Kit", "Ergonomic multi-blade luxury razor.", "https://bombayshavingcompany.com", "Free professional beard trim & styling demo."),

    # Quick Commerce, E-commerce & Delivery
    ("Zepto 10-Minute Instant Festive Treats Pop-up", "Zepto Super Saver App", "Ultra-fast 10-minute grocery and festive delivery.", "https://zeptonow.com", "Spin the wheel for guaranteed grocery vouchers up to ₹500."),
    ("Blinkit Quick Gifting & Sweets Pavilion", "Blinkit Festive Hampers", "Instant delivery of handcrafted sweets, dry fruits, and gifts.", "https://blinkit.com", "Get your gift hamper delivered in 8 minutes flat."),
    ("Swiggy Instamart Gourmet Tasting Corner", "Instamart Artisanal Snacks", "Specialty imports, exotic snacks, and daily essentials.", "https://swiggy.com", "Free tasting of newly launched private label bakery items."),
    ("Zomato Live Foodie Playground & Games", "Zomato Gold Membership", "Unlimited dine-in discounts and free food delivery perks.", "https://zomato.com", "Play the culinary ring-toss game to win free Gold access."),
    ("Myntra Big Fashion Festive Trend Runway", "Myntra Luxe Collection", "Designer festive ethnic and western collections.", "https://myntra.com", "Interactive smart mirror to try on 50+ outfits digitally."),

    # Automotive & EV
    ("Tata Motors Curvv EV Futuristic Test Track", "Tata Curvv EV", "Coupe-SUV electric vehicle with 500km single-charge range.", "https://tatamotors.com", "Priority on-spot test drive around the closed circuit."),
    ("Ola Electric S1 Pro Hyper-Drive Experiential Hub", "Ola S1 Pro Gen 3", "High-speed electric scooter with MoveOS 5 smart features.", "https://olaelectric.com", "Test ride challenge + instant ₹10,000 festive subsidy voucher."),
    ("Ather 450 Apex Speed & Warp Mode Trial", "Ather 450 Apex", "Blistering acceleration electric scooter with Warp+ mode.", "https://atherenergy.com", "Experience 0-40 km/h in 2.9 seconds on our ramp track."),
    ("Royal Enfield Guerrilla 450 Scrambler Playground", "Guerrilla 450", "High-torque roadster designed for pure urban riding thrills.", "https://royalenfield.com", "Free riding gear inspection + test ride with pro road captains."),
    ("Mahindra Thar Roxx 4x4 Obstacle Course", "Thar Roxx 5-Door", "Iconic off-roader with luxury dual screens and panoramic sunroof.", "https://auto.mahindra.com", "Ride along with rally drivers on the 40-degree incline ramp."),

    # Fintech & Lifestyle
    ("CRED Garage Car Care & Luxury Experience Bar", "CRED Garage Service", "Manage vehicle documents, fuel rewards, and maintenance perks.", "https://cred.club", "Free premium car perfume + vehicle health diagnostics."),
    ("Zerodha Financial Independence & Wealth Cafe", "Kite Trading App", "Zero-brokerage sleek investment platform for modern India.", "https://zerodha.com", "Free 1-on-1 financial health checkup with certified advisors."),
    ("Groww Investment Pop-Up & SIP Calculator Hub", "Groww Mutual Funds", "Simple transparent investing in stocks, mutual funds, and gold.", "https://groww.in", "Get ₹100 starting SIP credited on new account verification."),
    ("Cult.fit HIIT Fitness Challenge & Energy Arena", "Cultpass Elite", "Unlimited access to cult group workouts, gyms, and sports.", "https://cult.fit", "Take the 2-minute plank challenge to win free gym memberships."),
    ("Anytime Fitness Health & Wellness Assessment", "Anytime Fitness Gym Pass", "24/7 global gym access with certified personal trainers.", "https://anytimefitness.co.in", "Complimentary InBody body composition scan and diet advice."),
]

LOCALITY_POOL = [
    "High Street Phoenix Atrium", "Bandra Kurla Complex (BKC)", "Cyber Hub Promenade",
    "Indiranagar 100ft Road", "Koramangala 5th Block", "Connaught Place Inner Circle",
    "Jubilee Hills Road No. 36", "Phoenix Marketcity Courtyard", "Viman Nagar Square",
    "Salt Lake Sector V", "DLF Mall of India Main Atrium", "Select Citywalk Courtyard",
    "Orion Mall Lakeside Plaza", "Inorbit Mall Central Hall", "Worldmark Aerocity",
]


def seed_campaigns(recreate: bool = False, conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db_connection()
        close_at_end = True

    try:
        with conn.cursor() as cur:
            # 1. Ensure campaign tables exist
            if recreate:
                print("  [campaigns] Force deleting existing campaign tables (CASCADE)...")
                cur.execute("DROP TABLE IF EXISTS campaign_ai_sessions CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_matching_rules CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_props CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_languages CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_audiences CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_venues CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_type_map CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_skills CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_industries CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_products CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaigns CASCADE;")
                cur.execute("DROP TABLE IF EXISTS venue_types CASCADE;")
                cur.execute("DROP TABLE IF EXISTS campaign_types CASCADE;")

            execute_schema_file(cur, CAMPAIGN_SCHEMA_FILE)

            # 2. Seed campaign_types lookup
            for c_name, c_desc in CAMPAIGN_TYPES_SEED:
                cur.execute(
                    """
                    INSERT INTO campaign_types (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (c_name, c_desc),
                )

            # 3. Seed venue_types lookup
            for v_name, v_desc in VENUE_TYPES_SEED:
                cur.execute(
                    """
                    INSERT INTO venue_types (name, description)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (v_name, v_desc),
                )

            # 4. Fetch available reference data
            cur.execute("SELECT id FROM campaign_types;")
            campaign_type_ids = [r[0] for r in cur.fetchall()]

            cur.execute("SELECT id FROM venue_types;")
            venue_type_ids = [r[0] for r in cur.fetchall()]

            cur.execute("SELECT id, name FROM cities;")
            cities_data = cur.fetchall()
            city_ids = [r[0] for r in cities_data]

            cur.execute("SELECT id FROM industries;")
            industry_ids = [r[0] for r in cur.fetchall()]

            cur.execute("SELECT id FROM skills;")
            skill_ids = [r[0] for r in cur.fetchall()]

            cur.execute("SELECT id FROM languages;")
            language_ids = [r[0] for r in cur.fetchall()]

            # Fetch brand users
            cur.execute("SELECT id FROM users WHERE role = 'brand' AND is_deleted = FALSE;")
            brand_user_ids = [r[0] for r in cur.fetchall()]
            if not brand_user_ids:
                # Fallback to any user
                cur.execute("SELECT id FROM users LIMIT 10;")
                brand_user_ids = [r[0] for r in cur.fetchall()]

            if not brand_user_ids:
                raise ValueError("No brand users found in the system. Run seed_brands first!")

            # 5. Seed 50 Campaigns (Date range strictly 25-Oct-2026 to 04-Nov-2026)
            START_DATE = date(2026, 10, 25)
            END_DATE = date(2026, 11, 4)
            day_range = (END_DATE - START_DATE).days  # 10 days

            # Clean existing campaigns if recreate was requested
            if recreate:
                cur.execute("DELETE FROM campaigns;")

            print(f"  [campaigns] Seeding 50 realistic campaigns ({START_DATE} to {END_DATE})...")

            created_count = 0
            for i in range(50):
                camp_meta = CAMPAIGN_TITLES_AND_PRODUCTS[i % len(CAMPAIGN_TITLES_AND_PRODUCTS)]
                title, prod_name, prod_desc, prod_url, offer_desc = camp_meta

                user_id = random.choice(brand_user_ids)
                city_id = random.choice(city_ids)
                locality = random.choice(LOCALITY_POOL)

                # Date strictly between Oct 25 and Nov 04, 2026
                camp_date = START_DATE + timedelta(days=random.randint(0, day_range))
                start_h = random.choice([9, 10, 11, 12])
                end_h = start_h + random.choice([7, 8, 9])
                total_hours = end_h - start_h

                desc = (
                    f"{title}. High-impact on-ground activation engaging direct consumers. "
                    f"Team will handle product demonstration, interactive games, lead capture, and instant sampling."
                )

                # 1. Insert Campaign (status: 3 = active, 2 = pending)
                status_val = 3 if i < 42 else 2

                cur.execute(
                    """
                    INSERT INTO campaigns (user_id, title, description, city_id, locality, date, start_time, end_time, total_hours, status, is_deleted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                    RETURNING id;
                    """,
                    (
                        user_id,
                        title,
                        desc,
                        city_id,
                        locality,
                        camp_date,
                        f"{start_h:02d}:00:00",
                        f"{end_h:02d}:00:00",
                        total_hours,
                        status_val,
                    ),
                )
                cid = cur.fetchone()[0]

                # 2. Insert Campaign Product
                cur.execute(
                    """
                    INSERT INTO campaign_products (campaign_id, product_name, product_description, product_url, offer_description)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (cid, prod_name, prod_desc, prod_url, offer_desc),
                )

                # 3. Insert Campaign Industries (1-2)
                chosen_inds = random.sample(industry_ids, k=min(len(industry_ids), random.randint(1, 2)))
                for idx, ind_id in enumerate(chosen_inds):
                    cur.execute(
                        """
                        INSERT INTO campaign_industries (campaign_id, industry_id, is_primary)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                        """,
                        (cid, ind_id, idx == 0),
                    )

                # 4. Insert Campaign Type (1)
                chosen_type = random.choice(campaign_type_ids)
                cur.execute(
                    """
                    INSERT INTO campaign_type_map (campaign_id, campaign_type_id, is_primary)
                    VALUES (%s, %s, TRUE)
                    ON CONFLICT DO NOTHING;
                    """,
                    (cid, chosen_type),
                )

                # 5. Insert Campaign Venue (1)
                chosen_venue_type = random.choice(venue_type_ids)
                cur.execute(
                    """
                    INSERT INTO campaign_venues (campaign_id, venue_type_id, venue_name, venue_address)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (
                        cid,
                        chosen_venue_type,
                        f"{locality} Main Promenade",
                        f"{locality}, City Center Hub",
                    ),
                )

                # 6. Insert Campaign Audience Demographics
                cur.execute(
                    """
                    INSERT INTO campaign_audiences (
                        campaign_id, min_age, max_age, gender, income_min, income_max,
                        occupation, audience_size, interests, description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        cid,
                        18,
                        36,
                        random.choice(["All", "All", "All", "Female", "Male"]),
                        25000.0,
                        150000.0,
                        random.choice(["College Students & Young Professionals", "Corporate Executives", "Fitness & Lifestyle Seekers"]),
                        random.randint(1500, 8000),
                        "Experiential events, music fests, sports, premium beverages, gadgets",
                        "Urban consumers looking for hands-on trials and authentic brand engagement.",
                    ),
                )

                # 7. Insert Campaign Skills (2-4 required skills)
                chosen_skills = random.sample(skill_ids, k=min(len(skill_ids), random.randint(2, 4)))
                for s_id in chosen_skills:
                    cur.execute(
                        """
                        INSERT INTO campaign_skills (campaign_id, skill_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                        """,
                        (cid, s_id),
                    )

                # 8. Insert Campaign Languages (1-2 languages)
                chosen_langs = random.sample(language_ids, k=min(len(language_ids), random.randint(1, 2)))
                for l_id in chosen_langs:
                    cur.execute(
                        """
                        INSERT INTO campaign_languages (campaign_id, language_id, proficiency, is_required)
                        VALUES (%s, %s, %s, TRUE)
                        ON CONFLICT DO NOTHING;
                        """,
                        (cid, l_id, random.choice([2, 3])),  # 2=conversational, 3=fluent
                    )

                # 9. Insert Campaign Props
                cur.execute(
                    """
                    INSERT INTO campaign_props (campaign_id, stalls, tables, chairs, led, banners, other_requirements)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (
                        cid,
                        random.randint(1, 4),
                        random.randint(2, 6),
                        random.randint(4, 12),
                        random.randint(1, 2),
                        random.randint(2, 8),
                        "Sound system with 2 cordless mics, 5G Wi-Fi hotspot, branded t-shirts and lanyards for crew.",
                    ),
                )

                # 10. Insert Campaign Matching Rules
                cur.execute(
                    """
                    INSERT INTO campaign_matching_rules (
                        campaign_id, location_rule, language_rule, industry_rule, experience_rule, output_rule
                    )
                    VALUES (%s, 2, 2, 2, 2, 2)
                    ON CONFLICT DO NOTHING;
                    """,
                    (cid,),
                )

                created_count += 1

            conn.commit()
            print(f"  [OK] Successfully seeded {created_count} rich campaigns with full relations!")
    finally:
        if close_at_end:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed Campaigns")
    parser.add_argument("--recreate", action="store_true", help="Force drop and recreate campaign tables before seeding")
    args = parser.parse_args()
    seed_campaigns(recreate=args.recreate)
