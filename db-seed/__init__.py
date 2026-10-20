"""
Master Seeder Runner
--------------------
Orchestrates running all seeders in db-seed.
Supports two modes:
  1. Default (create-if-not-exists + upsert/insert)
  2. --recreate (force drops existing tables and recreates from scratch)

Usage:
    python3 db-seed/__init__.py
    python3 db-seed/__init__.py --recreate
"""

import sys
import os
import argparse

# Add db-seed directory to sys.path so direct script execution works
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
for p in [CURRENT_DIR, PROJECT_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from db import get_db_connection
    from seed_cities import seed_cities
    from seed_industries import seed_industries
    from seed_skills import seed_skills
    from seed_languages import seed_languages
    from seed_brands import seed_brands
    from seed_candidates import seed_candidates
    from seed_campaigns import seed_campaigns
except ImportError:
    from .db import get_db_connection
    from .seed_cities import seed_cities
    from .seed_industries import seed_industries
    from .seed_skills import seed_skills
    from .seed_languages import seed_languages
    from .seed_brands import seed_brands
    from .seed_candidates import seed_candidates
    from .seed_campaigns import seed_campaigns


def run_all(recreate: bool = False):
    print("=" * 60)
    mode_text = "FORCE RECREATE (DROP & REBUILD)" if recreate else "SAFE (CREATE IF NOT EXISTS)"
    print(f"Starting Seeding Pipeline — Mode: {mode_text}")
    print("=" * 60)

    conn = get_db_connection()
    try:
        print("\n1. Seeding Cities & Locations...")
        seed_cities(recreate=recreate, conn=conn)

        print("\n2. Seeding Industries...")
        seed_industries(recreate=recreate, conn=conn)

        print("\n3. Seeding Skills...")
        seed_skills(recreate=recreate, conn=conn)

        print("\n4. Seeding Languages...")
        seed_languages(recreate=recreate, conn=conn)

        print("\n5. Seeding 100 Brands & Brand Profiles...")
        seed_brands(recreate=recreate, conn=conn)

        print("\n6. Seeding 300 Candidates & Provider Profiles...")
        seed_candidates(recreate=recreate, conn=conn)

        print("\n7. Seeding 50 Live Campaigns (Oct 25 – Nov 04, 2026)...")
        seed_campaigns(recreate=recreate, conn=conn)

        print("\n" + "=" * 60)
        print("All seeds (Taxonomy, 100 Brands, 300 Candidates, 50 Campaigns) completed successfully!")
        print("=" * 60)
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DB Seeders")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Force delete (DROP CASCADE) and recreate tables before seeding",
    )
    args = parser.parse_args()
    run_all(recreate=args.recreate)
