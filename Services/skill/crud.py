"""
Skill CRUD — Raw psycopg2 Queries
"""

from Core.database import fetchone, fetchall, execute_returning
from .models import Skill


def create_skill(data: dict) -> dict:
    row = execute_returning(
        """
        INSERT INTO skills (name, user_id)
        VALUES (%s, 0)
        RETURNING *
        """,
        (data["name"],)
    )
    return Skill.from_row(row).to_dict()


def update_skill(skill_id: int, data: dict) -> dict | None:
    allowed = {k: v for k, v in data.items() if k in ("name",)}
    if not allowed:
        return _get_skill_by_id(skill_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [skill_id]

    row = execute_returning(
        f"UPDATE skills SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return Skill.from_row(row).to_dict() if row else None


def get_skills() -> list[dict]:
    rows = fetchall("SELECT * FROM skills ORDER BY name ASC")
    return [Skill.from_row(r).to_dict() for r in rows]


def _get_skill_by_id(skill_id: int) -> dict | None:
    row = fetchone("SELECT * FROM skills WHERE id = %s", (skill_id,))
    return Skill.from_row(row).to_dict() if row else None
