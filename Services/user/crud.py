"""
User CRUD — Raw psycopg2 Queries
-----------------------------------
All queries run against the `users` table defined in schema.sql.
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import User, UserExperience


def get_all_users() -> list[dict]:
    """Fetch all non-deleted users."""
    rows = fetchall(
        "SELECT * FROM users WHERE is_deleted = FALSE ORDER BY created_at DESC"
    )
    return [User.from_row(r).to_dict() for r in rows]


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch a single user by primary key with experiences."""
    row = fetchone(
        "SELECT * FROM users WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    if not row:
        return None
    experiences = get_user_experiences(user_id)
    return User.from_row(row, experiences).to_dict()


def get_user_by_email(email: str) -> dict | None:
    """Fetch a user by their email address with experiences."""
    row = fetchone(
        "SELECT * FROM users WHERE email = %s AND is_deleted = FALSE",
        (email.lower().strip(),)
    )
    if not row:
        return None
    experiences = get_user_experiences(row["id"])
    return User.from_row(row, experiences).to_dict()


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
    return get_user_by_id(user_id) if row else None


def soft_delete_user(user_id: int) -> bool:
    """Mark a user as deleted without removing the row."""
    affected = execute(
        "UPDATE users SET is_deleted = TRUE WHERE id = %s AND is_deleted = FALSE",
        (user_id,)
    )
    return affected > 0


# ── User Experiences CRUD ─────────────────────────────────────────────────────

def get_user_experiences(user_id: int) -> list[UserExperience]:
    """Retrieve all past campaign experiences for a user."""
    rows = fetchall(
        "SELECT * FROM user_experiences WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    return [UserExperience.from_row(r) for r in rows]


def add_user_experience(user_id: int, data: dict) -> dict:
    """Add a new past campaign experience record."""
    row = execute_returning(
        """
        INSERT INTO user_experiences (user_id, brand_name, role_name, duration, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, data.get("brand_name"), data.get("role_name"), data.get("duration"), data.get("description"))
    )
    return UserExperience.from_row(row).to_dict()


def delete_user_experience(user_id: int, experience_id: int) -> bool:
    """Delete a specific experience record, confirming owner user_id."""
    affected = execute(
        "DELETE FROM user_experiences WHERE id = %s AND user_id = %s",
        (experience_id, user_id)
    )
    return affected > 0

