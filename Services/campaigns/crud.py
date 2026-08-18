"""
Campaigns CRUD — Raw psycopg2 Queries
----------------------------------------
All queries run against the `campaigns` and `campaign_props` tables defined in schema.sql.
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import Campaign, CampaignProps
from .enum import STATUS_ID

# Columns that are allowed to be patched on the campaigns table
_CAMPAIGN_PATCHABLE = {
    "title", "description", "total_hours",
    "start_time", "end_time", "date",
    "target", "locality", "status",
}

# Columns that are allowed to be patched on the campaign_props table
_PROPS_PATCHABLE = {"stalls", "tables", "chairs", "led", "banners"}


def get_all_campaigns(user_id: int | None = None) -> list[dict]:
    """Return all non-deleted campaigns, optionally filtered by user."""
    if user_id:
        rows = fetchall(
            "SELECT * FROM campaigns WHERE user_id = %s AND is_deleted = FALSE ORDER BY created_at DESC",
            (user_id,)
        )
    else:
        rows = fetchall(
            "SELECT * FROM campaigns WHERE is_deleted = FALSE ORDER BY created_at DESC"
        )
    return [Campaign.from_row(r).to_dict() for r in rows]


def get_campaign_by_id(campaign_id: int) -> dict | None:
    """Return a single campaign dict by ID, or None if not found."""
    row = fetchone(
        "SELECT * FROM campaigns WHERE id = %s AND is_deleted = FALSE",
        (campaign_id,)
    )
    return Campaign.from_row(row).to_dict() if row else None


def get_campaign_props(campaign_id: int) -> dict | None:
    """Return campaign props for the given campaign_id, or None if not set."""
    row = fetchone(
        "SELECT * FROM campaign_props WHERE campaign_id = %s",
        (campaign_id,)
    )
    return CampaignProps.from_row(row).to_dict() if row else None


def create_campaign(user_id: int, title: str) -> dict:
    """Insert a new campaign with only a title; status defaults to 1 (draft)."""
    row = execute_returning(
        """
        INSERT INTO campaigns (user_id, title)
        VALUES (%s, %s)
        RETURNING *
        """,
        (user_id, title)
    )
    return Campaign.from_row(row).to_dict()


def update_campaign(campaign_id: int, data: dict) -> dict | None:
    """Patch only the supplied campaign fields. Returns updated dict or None."""
    allowed = {k: v for k, v in data.items() if k in _CAMPAIGN_PATCHABLE}

    # Convert status string → integer before writing
    if "status" in allowed:
        allowed["status"] = STATUS_ID.get(allowed["status"], 1)

    if not allowed:
        return get_campaign_by_id(campaign_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [campaign_id]

    row = execute_returning(
        f"UPDATE campaigns SET {set_clause} WHERE id = %s AND is_deleted = FALSE RETURNING *",
        tuple(values)
    )
    return Campaign.from_row(row).to_dict() if row else None


def update_campaign_props(campaign_id: int, data: dict) -> dict | None:
    """Upsert campaign props with only the supplied fields. Returns updated dict or None."""
    allowed = {k: v for k, v in data.items() if k in _PROPS_PATCHABLE}
    if not allowed:
        return get_campaign_props(campaign_id)

    existing = fetchone(
        "SELECT id FROM campaign_props WHERE campaign_id = %s",
        (campaign_id,)
    )

    if existing:
        set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
        values = list(allowed.values()) + [campaign_id]
        row = execute_returning(
            f"UPDATE campaign_props SET {set_clause} WHERE campaign_id = %s RETURNING *",
            tuple(values)
        )
    else:
        # INSERT with defaults for columns not supplied
        cols = ["campaign_id"] + list(allowed.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        values = [campaign_id] + list(allowed.values())
        row = execute_returning(
            f"INSERT INTO campaign_props ({', '.join(cols)}) VALUES ({placeholders}) RETURNING *",
            tuple(values)
        )

    return CampaignProps.from_row(row).to_dict() if row else None


def soft_delete_campaign(campaign_id: int) -> bool:
    """Soft-delete a campaign by setting is_deleted = TRUE. Returns True if a row was affected."""
    affected = execute(
        "UPDATE campaigns SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
        (campaign_id,)
    )
    return affected > 0


# ── AI Session CRUD ───────────────────────────────────────────────────────────

def get_ai_session(user_id: int, campaign_id: int) -> list[dict]:
    """Return the stored conversation messages for this (user, campaign) pair."""
    row = fetchone(
        "SELECT messages FROM campaign_ai_sessions WHERE user_id = %s AND campaign_id = %s",
        (user_id, campaign_id)
    )
    if not row:
        return []
    messages = row["messages"]
    # psycopg2 returns JSONB as a Python object already
    return messages if isinstance(messages, list) else []


def upsert_ai_session(user_id: int, campaign_id: int, messages: list[dict]) -> None:
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

