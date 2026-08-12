"""
User CRUD — Raw psycopg2 Queries
-----------------------------------
All queries run against the `users` table defined in schema.sql.
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import User


def get_all_users() -> list[dict]:
    """Fetch all non-deleted users."""
    rows = fetchall(
        "SELECT * FROM users WHERE is_deleted = FALSE ORDER BY created_at DESC"
    )
    return [User.from_row(r).to_dict() for r in rows]


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch a single user by primary key."""
    row = fetchone(
        "SELECT * FROM users WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    return User.from_row(row).to_dict() if row else None


def get_user_by_email(email: str) -> dict | None:
    """Fetch a user by their email address."""
    row = fetchone(
        "SELECT * FROM users WHERE email = %s AND is_deleted = FALSE",
        (email.lower().strip(),)
    )
    return User.from_row(row).to_dict() if row else None


def create_user(name: str, email: str, role: str = "user", phone: str = None) -> dict:
    """
    Insert a new user row and return the created record.
    Authentication is OTP-only — no password is stored.
    """
    row = execute_returning(
        """
        INSERT INTO users (name, email, phone, role)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (name, email.lower().strip(), phone, role)
    )
    return User.from_row(row).to_dict()


def update_user(user_id: int, data: dict) -> dict | None:
    """Update allowed fields on a user row."""
    allowed = {k: v for k, v in data.items() if k in ("name", "phone", "role")}
    if not allowed:
        return get_user_by_id(user_id)

    set_clause = ", ".join(f"{col} = %s" for col in allowed.keys())
    values = list(allowed.values()) + [user_id]

    row = execute_returning(
        f"UPDATE users SET {set_clause} WHERE id = %s AND is_deleted = FALSE RETURNING *",
        tuple(values)
    )
    return User.from_row(row).to_dict() if row else None


def soft_delete_user(user_id: int) -> bool:
    """Mark a user as deleted without removing the row."""
    affected = execute(
        "UPDATE users SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    return affected > 0
