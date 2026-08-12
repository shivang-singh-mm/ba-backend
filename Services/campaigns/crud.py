"""
Campaigns CRUD — Raw psycopg2 Queries
----------------------------------------
All queries run against the `campaigns` table defined in schema.sql.
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import Campaign


def get_all_campaigns(user_id: int = None) -> list[dict]:
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
    row = fetchone(
        "SELECT * FROM campaigns WHERE id = %s AND is_deleted = FALSE",
        (campaign_id,)
    )
    return Campaign.from_row(row).to_dict() if row else None


def create_campaign(user_id: int, title: str, description: str = None,
                    budget: float = None, start_date=None, end_date=None) -> dict:
    row = execute_returning(
        """
        INSERT INTO campaigns (user_id, title, description, budget, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, title, description, budget, start_date, end_date)
    )
    return Campaign.from_row(row).to_dict()


def update_campaign(campaign_id: int, data: dict) -> dict | None:
    allowed = {k: v for k, v in data.items()
               if k in ("title", "description", "budget", "start_date", "end_date", "status")}
    if not allowed:
        return get_campaign_by_id(campaign_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [campaign_id]

    row = execute_returning(
        f"UPDATE campaigns SET {set_clause} WHERE id = %s AND is_deleted = FALSE RETURNING *",
        tuple(values)
    )
    return Campaign.from_row(row).to_dict() if row else None


def soft_delete_campaign(campaign_id: int) -> bool:
    affected = execute(
        "UPDATE campaigns SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
        (campaign_id,)
    )
    return affected > 0
