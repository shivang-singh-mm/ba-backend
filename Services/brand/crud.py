"""
Brand CRUD — Raw psycopg2 Queries
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import BrandProfile


def get_all_brands() -> list[dict]:
    rows = fetchall("SELECT * FROM brand_profiles WHERE is_active = TRUE ORDER BY created_at DESC")
    results = []
    for r in rows:
        results.append(get_brand_by_id(r["id"]))
    return [res for res in results if res is not None]


def get_brand_by_id(brand_id: int) -> dict | None:
    row = fetchone("SELECT * FROM brand_profiles WHERE id = %s", (brand_id,))
    if not row:
        return None

    # Fetch relations
    industries = fetchall(
        "SELECT i.id, i.name, bi.is_primary FROM brand_industries bi JOIN industries i ON bi.industry_id = i.id WHERE bi.brand_id = %s",
        (brand_id,)
    )
    
    locations = fetchall(
        "SELECT c.id, c.name, bl.is_primary FROM brand_locations bl JOIN cities c ON bl.city_id = c.id WHERE bl.brand_id = %s",
        (brand_id,)
    )

    return BrandProfile.from_row(row, industries, locations).to_dict()


def get_brand_by_user_id(user_id: int) -> dict | None:
    row = fetchone("SELECT id FROM brand_profiles WHERE user_id = %s", (user_id,))
    if not row:
        return None
    return get_brand_by_id(row["id"])



def create_brand_profile(user_id: int, data: dict) -> dict:
    row = execute_returning(
        """
        INSERT INTO brand_profiles (user_id, brand_name, brand_description, brand_logo_url, brand_website, city_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            user_id,
            data["brand_name"],
            data.get("brand_description"),
            data.get("brand_logo_url"),
            data.get("brand_website"),
            data.get("city_id")
        )
    )
    
    brand_id = row["id"]
    
    if "industries" in data:
        for ind in data["industries"]:
            execute("INSERT INTO brand_industries (brand_id, industry_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (brand_id, ind["id"], ind.get("is_primary", False)))
            
    if "locations" in data:
        for loc in data["locations"]:
            execute("INSERT INTO brand_locations (brand_id, city_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (brand_id, loc["id"], loc.get("is_primary", False)))

    return get_brand_by_id(brand_id)


def update_brand_personal(brand_id: int, data: dict) -> dict | None:
    allowed = {k: v for k, v in data.items() if k in ("brand_name", "brand_description", "brand_logo_url", "brand_website", "city_id")}
    if not allowed:
        return get_brand_by_id(brand_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [brand_id]

    execute(f"UPDATE brand_profiles SET {set_clause} WHERE id = %s", tuple(values))
    return get_brand_by_id(brand_id)


def update_brand_associations(brand_id: int, data: dict) -> dict | None:
    if "industries" in data:
        execute("DELETE FROM brand_industries WHERE brand_id = %s", (brand_id,))
        for ind in data["industries"]:
            execute("INSERT INTO brand_industries (brand_id, industry_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (brand_id, ind["id"], ind.get("is_primary", False)))

    if "locations" in data:
        execute("DELETE FROM brand_locations WHERE brand_id = %s", (brand_id,))
        for loc in data["locations"]:
            execute("INSERT INTO brand_locations (brand_id, city_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (brand_id, loc["id"], loc.get("is_primary", False)))

    return get_brand_by_id(brand_id)
