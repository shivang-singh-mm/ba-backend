"""
Campaigns CRUD — Raw psycopg2 Queries
----------------------------------------
All database operations for the campaigns module.
"""

from typing import Optional, List, Dict, Any
from Core.database import fetchone, fetchall, execute_returning, execute
from .models import Campaign, CampaignProduct, CampaignVenue, CampaignAudience, CampaignProps, CampaignMatchingRules
from .enum import STATUS_ID, PROFICIENCY, PROFICIENCY_ID, MATCHING_RULE_ID

# Allowed fields for basic campaign info
_CAMPAIGN_BASICS_PATCHABLE = {
    "title", "description", "city_id", "locality",
    "date", "start_time", "end_time", "total_hours", "status",
}


def get_campaign_types() -> List[Dict[str, Any]]:
    """Return all available campaign types."""
    return fetchall("SELECT id, name, description FROM campaign_types ORDER BY name ASC")


def get_venue_types() -> List[Dict[str, Any]]:
    """Return all available venue types."""
    return fetchall("SELECT id, name, description FROM venue_types ORDER BY name ASC")


def get_all_campaigns(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Return all non-deleted campaigns, optionally filtered by user."""
    if user_id:
        rows = fetchall(
            """
            SELECT c.*, ci.name AS city_name
            FROM campaigns c
            LEFT JOIN cities ci ON c.city_id = ci.id
            WHERE c.user_id = %s AND c.is_deleted = FALSE
            ORDER BY c.created_at DESC
            """,
            (user_id,)
        )
    else:
        rows = fetchall(
            """
            SELECT c.*, ci.name AS city_name
            FROM campaigns c
            LEFT JOIN cities ci ON c.city_id = ci.id
            WHERE c.is_deleted = FALSE
            ORDER BY c.created_at DESC
            """
        )
    return [get_campaign_by_id(r["id"]) for r in rows if r is not None]


def get_campaign_by_id(campaign_id: int) -> Optional[Dict[str, Any]]:
    """Return a single campaign dict by ID with all relations populated, or None."""
    row = fetchone(
        """
        SELECT c.*, ci.name AS city_name
        FROM campaigns c
        LEFT JOIN cities ci ON c.city_id = ci.id
        WHERE c.id = %s AND c.is_deleted = FALSE
        """,
        (campaign_id,)
    )
    if not row:
        return None

    # 1. Products
    product_rows = fetchall(
        "SELECT * FROM campaign_products WHERE campaign_id = %s ORDER BY created_at ASC",
        (campaign_id,)
    )
    products = [CampaignProduct.from_row(p).to_dict() for p in product_rows]

    # 2. Industries
    industry_rows = fetchall(
        """
        SELECT i.id, i.name, ci.is_primary
        FROM campaign_industries ci
        JOIN industries i ON ci.industry_id = i.id
        WHERE ci.campaign_id = %s
        ORDER BY ci.is_primary DESC, i.name ASC
        """,
        (campaign_id,)
    )
    industries = [dict(r) for r in industry_rows]

    # 3. Types
    type_rows = fetchall(
        """
        SELECT ct.id, ct.name, ctm.is_primary
        FROM campaign_type_map ctm
        JOIN campaign_types ct ON ctm.campaign_type_id = ct.id
        WHERE ctm.campaign_id = %s
        ORDER BY ctm.is_primary DESC, ct.name ASC
        """,
        (campaign_id,)
    )
    types = [dict(r) for r in type_rows]

    # 4. Venues
    venue_rows = fetchall(
        """
        SELECT cv.*, vt.name AS venue_type_name
        FROM campaign_venues cv
        LEFT JOIN venue_types vt ON cv.venue_type_id = vt.id
        WHERE cv.campaign_id = %s
        ORDER BY cv.created_at ASC
        """,
        (campaign_id,)
    )
    venues = [CampaignVenue.from_row(v).to_dict() for v in venue_rows]

    # 5. Audience
    audience_row = fetchone(
        "SELECT * FROM campaign_audiences WHERE campaign_id = %s",
        (campaign_id,)
    )
    audience = CampaignAudience.from_row(audience_row).to_dict() if audience_row else None

    # 6. Languages
    language_rows = fetchall(
        """
        SELECT l.id, l.name, cl.proficiency, cl.is_required
        FROM campaign_languages cl
        JOIN languages l ON cl.language_id = l.id
        WHERE cl.campaign_id = %s
        ORDER BY l.name ASC
        """,
        (campaign_id,)
    )
    languages = [
        {
            "id": lr["id"],
            "name": lr["name"],
            "proficiency": PROFICIENCY.get(lr["proficiency"], "conversational"),
            "is_required": lr["is_required"],
        }
        for lr in language_rows
    ]

    # 7. Props
    props_row = fetchone(
        "SELECT * FROM campaign_props WHERE campaign_id = %s",
        (campaign_id,)
    )
    props = CampaignProps.from_row(props_row).to_dict() if props_row else None

    # 8. Matching Rules
    rules_row = fetchone(
        "SELECT * FROM campaign_matching_rules WHERE campaign_id = %s",
        (campaign_id,)
    )
    matching_rules = CampaignMatchingRules.from_row(rules_row).to_dict() if rules_row else None

    return Campaign.from_row(
        row=row,
        products=products,
        industries=industries,
        types=types,
        venues=venues,
        audience=audience,
        languages=languages,
        props=props,
        matching_rules=matching_rules,
    ).to_dict()


def create_campaign(user_id: int, data: dict) -> dict:
    """Insert a new campaign draft with minimal required fields (title)."""
    title = data["title"]
    description = data.get("description")
    city_id = data.get("city_id")
    locality = data.get("locality")
    date_val = data.get("date")

    row = execute_returning(
        """
        INSERT INTO campaigns (user_id, title, description, city_id, locality, date)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, title, description, city_id, locality, date_val)
    )
    campaign_id = row["id"]

    # Initialise default empty campaign_props
    execute(
        "INSERT INTO campaign_props (campaign_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (campaign_id,)
    )

    return get_campaign_by_id(campaign_id)


def update_campaign_basics(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update core campaign fields (title, date, city, times, locality, status)."""
    allowed = {k: v for k, v in data.items() if k in _CAMPAIGN_BASICS_PATCHABLE}

    if "status" in allowed and isinstance(allowed["status"], str):
        allowed["status"] = STATUS_ID.get(allowed["status"], 1)

    if not allowed:
        return get_campaign_by_id(campaign_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [campaign_id]

    execute(
        f"UPDATE campaigns SET {set_clause} WHERE id = %s AND is_deleted = FALSE",
        tuple(values)
    )
    return get_campaign_by_id(campaign_id)


def update_campaign_products(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update or replace product details for a campaign."""
    products = data.get("products", [])
    execute("DELETE FROM campaign_products WHERE campaign_id = %s", (campaign_id,))

    for p in products:
        if p.get("product_name"):
            execute(
                """
                INSERT INTO campaign_products (campaign_id, product_name, product_description, product_url, offer_description)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    campaign_id,
                    p["product_name"],
                    p.get("product_description"),
                    p.get("product_url"),
                    p.get("offer_description"),
                )
            )

    return get_campaign_by_id(campaign_id)


def update_campaign_associations(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update industry and campaign type tags for a campaign."""
    if "industries" in data:
        execute("DELETE FROM campaign_industries WHERE campaign_id = %s", (campaign_id,))
        for ind in data["industries"]:
            ind_id = ind["id"] if isinstance(ind, dict) else ind
            is_pri = ind.get("is_primary", False) if isinstance(ind, dict) else False
            execute(
                "INSERT INTO campaign_industries (campaign_id, industry_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (campaign_id, ind_id, is_pri)
            )

    if "types" in data:
        execute("DELETE FROM campaign_type_map WHERE campaign_id = %s", (campaign_id,))
        for t in data["types"]:
            type_id = t["id"] if isinstance(t, dict) else t
            is_pri = t.get("is_primary", False) if isinstance(t, dict) else False
            execute(
                "INSERT INTO campaign_type_map (campaign_id, campaign_type_id, is_primary) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (campaign_id, type_id, is_pri)
            )

    return get_campaign_by_id(campaign_id)


def update_campaign_venue(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update venue information for a campaign."""
    venues = data.get("venues", [])
    execute("DELETE FROM campaign_venues WHERE campaign_id = %s", (campaign_id,))

    for v in venues:
        execute(
            """
            INSERT INTO campaign_venues (campaign_id, venue_type_id, venue_name, venue_address)
            VALUES (%s, %s, %s, %s)
            """,
            (
                campaign_id,
                v.get("venue_type_id"),
                v.get("venue_name"),
                v.get("venue_address"),
            )
        )

    return get_campaign_by_id(campaign_id)


def update_campaign_audience(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Upsert audience demographics and targeting details."""
    allowed_cols = {
        "min_age", "max_age", "gender", "income_min", "income_max",
        "occupation", "education", "life_stage", "geography", "origin",
        "interests", "lifestyle", "purchase_behavior", "audience_size", "description",
    }
    filtered = {k: v for k, v in data.items() if k in allowed_cols}

    existing = fetchone("SELECT id FROM campaign_audiences WHERE campaign_id = %s", (campaign_id,))

    if existing:
        if filtered:
            set_clause = ", ".join(f"{col} = %s" for col in filtered.keys())
            values = list(filtered.values()) + [campaign_id]
            execute(f"UPDATE campaign_audiences SET {set_clause} WHERE campaign_id = %s", tuple(values))
    else:
        cols = ["campaign_id"] + list(filtered.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [campaign_id] + list(filtered.values())
        execute(
            f"INSERT INTO campaign_audiences ({', '.join(cols)}) VALUES ({placeholders})",
            tuple(values)
        )

    return get_campaign_by_id(campaign_id)


def update_campaign_languages(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Update required languages and proficiency for a campaign."""
    languages = data.get("languages", [])
    execute("DELETE FROM campaign_languages WHERE campaign_id = %s", (campaign_id,))

    for lang in languages:
        l_id = lang.get("id") if isinstance(lang, dict) else lang
        prof_str = lang.get("proficiency", "conversational") if isinstance(lang, dict) else "conversational"
        prof_id = PROFICIENCY_ID.get(prof_str, 2)
        is_req = lang.get("is_required", True) if isinstance(lang, dict) else True

        if l_id:
            execute(
                """
                INSERT INTO campaign_languages (campaign_id, language_id, proficiency, is_required)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (campaign_id, l_id, prof_id, is_req)
            )

    return get_campaign_by_id(campaign_id)


def update_campaign_props(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Upsert campaign props (stalls, tables, chairs, led, banners, other_requirements)."""
    allowed_cols = {"stalls", "tables", "chairs", "led", "banners", "other_requirements"}
    filtered = {k: v for k, v in data.items() if k in allowed_cols}

    existing = fetchone("SELECT id FROM campaign_props WHERE campaign_id = %s", (campaign_id,))

    if existing:
        if filtered:
            set_clause = ", ".join(f"{col} = %s" for col in filtered.keys())
            values = list(filtered.values()) + [campaign_id]
            execute(f"UPDATE campaign_props SET {set_clause} WHERE campaign_id = %s", tuple(values))
    else:
        cols = ["campaign_id"] + list(filtered.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [campaign_id] + list(filtered.values())
        execute(f"INSERT INTO campaign_props ({', '.join(cols)}) VALUES ({placeholders})", tuple(values))

    return get_campaign_by_id(campaign_id)


def update_campaign_matching_rules(campaign_id: int, data: dict) -> Optional[Dict[str, Any]]:
    """Upsert matching rules for a campaign (location_rule, language_rule, industry_rule, experience_rule, output_rule)."""
    rule_fields = ["location_rule", "language_rule", "industry_rule", "experience_rule", "output_rule"]
    filtered = {}

    for field in rule_fields:
        if field in data:
            val = data[field]
            if isinstance(val, str):
                filtered[field] = MATCHING_RULE_ID.get(val.lower(), 2)
            elif isinstance(val, int):
                filtered[field] = val

    existing = fetchone("SELECT id FROM campaign_matching_rules WHERE campaign_id = %s", (campaign_id,))

    if existing:
        if filtered:
            set_clause = ", ".join(f"{col} = %s" for col in filtered.keys())
            values = list(filtered.values()) + [campaign_id]
            execute(f"UPDATE campaign_matching_rules SET {set_clause} WHERE campaign_id = %s", tuple(values))
    else:
        cols = ["campaign_id"] + list(filtered.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [campaign_id] + list(filtered.values())
        execute(f"INSERT INTO campaign_matching_rules ({', '.join(cols)}) VALUES ({placeholders})", tuple(values))

    return get_campaign_by_id(campaign_id)


def soft_delete_campaign(campaign_id: int) -> bool:

    """Soft-delete a campaign by setting is_deleted = TRUE."""
    affected = execute(
        "UPDATE campaigns SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
        (campaign_id,)
    )
    return affected > 0


# ── AI Session CRUD ───────────────────────────────────────────────────────────

def get_ai_session(user_id: int, campaign_id: int) -> List[Dict[str, Any]]:
    """Return the stored conversation messages for this (user, campaign) pair."""
    row = fetchone(
        "SELECT messages FROM campaign_ai_sessions WHERE user_id = %s AND campaign_id = %s",
        (user_id, campaign_id)
    )
    if not row:
        return []
    messages = row["messages"]
    return messages if isinstance(messages, list) else []


def upsert_ai_session(user_id: int, campaign_id: int, messages: List[Dict[str, Any]]) -> None:
    """Persist the full conversation messages list for this (user, campaign) pair."""
    import json
    execute(
        """
        INSERT INTO campaign_ai_sessions (user_id, campaign_id, messages)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, campaign_id)
        DO UPDATE SET messages = EXCLUDED.messages
        """,
        (user_id, campaign_id, json.dumps(messages))
    )
