"""
Industry CRUD — Raw psycopg2 Queries
---------------------------------------
All queries run against the industries table.
"""

from Core.database import fetchone, fetchall, execute_returning
from .models import Industry


def create_industry(data: dict) -> dict:
    """Insert a new industry row with user_id hardcoded to 0."""
    row = execute_returning(
        """
        INSERT INTO industries (name, user_id)
        VALUES (%s, 0)
        RETURNING *
        """,
        (data["name"],)
    )
    return Industry.from_row(row).to_dict()


def update_industry(industry_id: int, data: dict) -> dict | None:
    """Update the name of an industry row. user_id is always kept as 0."""
    allowed = {k: v for k, v in data.items() if k in ("name",)}
    if not allowed:
        return _get_industry_by_id(industry_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [industry_id]

    row = execute_returning(
        f"UPDATE industries SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return Industry.from_row(row).to_dict() if row else None


def get_industries() -> list[dict]:
    """Fetch all industries ordered by name."""
    rows = fetchall("SELECT * FROM industries ORDER BY name ASC")
    return [Industry.from_row(r).to_dict() for r in rows]


def _get_industry_by_id(industry_id: int) -> dict | None:
    """Fetch a single industry by primary key."""
    row = fetchone("SELECT * FROM industries WHERE id = %s", (industry_id,))
    return Industry.from_row(row).to_dict() if row else None
