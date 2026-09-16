"""
Language CRUD — Raw psycopg2 Queries
"""

from Core.database import fetchone, fetchall, execute_returning
from .models import Language


def create_language(data: dict) -> dict:
    row = execute_returning(
        """
        INSERT INTO languages (name, user_id)
        VALUES (%s, 0)
        RETURNING *
        """,
        (data["name"],)
    )
    return Language.from_row(row).to_dict()


def update_language(language_id: int, data: dict) -> dict | None:
    allowed = {k: v for k, v in data.items() if k in ("name",)}
    if not allowed:
        return _get_language_by_id(language_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [language_id]

    row = execute_returning(
        f"UPDATE languages SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values)
    )
    return Language.from_row(row).to_dict() if row else None


def get_languages() -> list[dict]:
    rows = fetchall("SELECT * FROM languages ORDER BY name ASC")
    return [Language.from_row(r).to_dict() for r in rows]


def _get_language_by_id(language_id: int) -> dict | None:
    row = fetchone("SELECT * FROM languages WHERE id = %s", (language_id,))
    return Language.from_row(row).to_dict() if row else None
