"""
Payment CRUD — Raw psycopg2 Queries
--------------------------------------
All queries run against the `payments` table defined in schema.sql.
"""

from Core.database import fetchone, fetchall, execute_returning, execute
from .models import Payment


def get_payments_by_user(user_id: int) -> list[dict]:
    rows = fetchall(
        "SELECT * FROM payments WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    return [Payment.from_row(r).to_dict() for r in rows]


def get_payment_by_id(payment_id: int, user_id: int = None) -> dict | None:
    if user_id:
        row = fetchone(
            "SELECT * FROM payments WHERE id = %s AND user_id = %s",
            (payment_id, user_id)
        )
    else:
        row = fetchone("SELECT * FROM payments WHERE id = %s", (payment_id,))
    return Payment.from_row(row).to_dict() if row else None


def create_payment(user_id: int, amount: float, currency: str = "INR",
                   gateway: str = None, description: str = None) -> dict:
    row = execute_returning(
        """
        INSERT INTO payments (user_id, amount, currency, gateway, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, amount, currency, gateway, description)
    )
    return Payment.from_row(row).to_dict()


def update_payment_status(payment_id: int, status: str,
                          gateway_payment_id: str = None) -> dict | None:
    row = execute_returning(
        """
        UPDATE payments
        SET status = %s, gateway_payment_id = %s
        WHERE id = %s
        RETURNING *
        """,
        (status, gateway_payment_id, payment_id)
    )
    return Payment.from_row(row).to_dict() if row else None
