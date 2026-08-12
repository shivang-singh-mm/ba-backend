"""
Auth CRUD / Business Logic — Raw psycopg2
------------------------------------------
OTP-based authentication lifecycle.
All DB tables are defined in Services/auth/schema.sql and Services/user/schema.sql.

Endpoints served:
  initiate_register   → validate email not taken, write OTP, send email
  verify_register_otp → validate OTP, create user, return JWT
  initiate_login      → validate user exists, write OTP, send email
  verify_login_otp    → validate OTP, return JWT
  revoke_token        → insert jti into token_blocklist
"""

from datetime import datetime

from flask import current_app
from flask_jwt_extended import create_access_token

from Core.database import fetchone, execute, execute_returning
from Utils.otp import generate_otp, hash_otp, verify_otp_hash, get_otp_expiry, send_otp_email
from Utils.logger import logger


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _invalidate_old_otps(email: str, purpose: str):
    """Mark all previous unused OTPs for this email+purpose as used."""
    execute(
        "UPDATE otp_codes SET is_used = TRUE WHERE email = %s AND purpose = %s AND is_used = FALSE",
        (email, purpose)
    )


def _insert_otp(email: str, purpose: str, plain_otp: str,
                pending_name: str = None, pending_role: str = None) -> int:
    """
    Hash the OTP and persist the record.
    Returns the new otp_codes.id.
    """
    otp_hash = hash_otp(plain_otp)
    expires_at = get_otp_expiry()

    row = execute_returning(
        """
        INSERT INTO otp_codes
            (email, purpose, otp_hash, expires_at, pending_name, pending_role)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (email, purpose, otp_hash, expires_at, pending_name, pending_role)
    )
    return row["id"]


def _send_and_record_otp(email: str, purpose: str, name: str = "",
                          pending_role: str = None) -> tuple:
    """
    Generate OTP → hash + store → send email.
    Returns (None, error_str) on failure, (plain_otp, None) on success.
    """
    plain_otp = generate_otp()
    _insert_otp(email, purpose, plain_otp, pending_name=name, pending_role=pending_role)

    sent = send_otp_email(to_email=email, otp=plain_otp, purpose=purpose, name=name)
    if not sent:
        return None, "Failed to send OTP email. Please try again."

    logger.info(f"OTP dispatched [email={email}, purpose={purpose}]")
    return plain_otp, None


def _validate_otp(email: str, plain_otp: str, purpose: str) -> tuple:
    """
    Fetch the latest active OTP and verify it against the submitted value.

    Returns:
        (otp_row dict, None)  on success
        (None, error_str)     on failure
    """
    max_attempts = current_app.config.get("OTP_MAX_ATTEMPTS", 3)

    row = fetchone(
        """
        SELECT * FROM otp_codes
        WHERE email = %s AND purpose = %s AND is_used = FALSE
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email, purpose)
    )

    if not row:
        return None, "No active OTP found. Please request a new one."

    if datetime.utcnow() > row["expires_at"].replace(tzinfo=None):
        execute("UPDATE otp_codes SET is_used = TRUE WHERE id = %s", (row["id"],))
        return None, "OTP has expired. Please request a new one."

    if row["attempts"] >= max_attempts:
        execute("UPDATE otp_codes SET is_used = TRUE WHERE id = %s", (row["id"],))
        return None, "Too many failed attempts. Please request a new OTP."

    if not verify_otp_hash(plain_otp, row["otp_hash"]):
        execute(
            "UPDATE otp_codes SET attempts = attempts + 1 WHERE id = %s",
            (row["id"],)
        )
        remaining = max_attempts - (row["attempts"] + 1)
        return None, f"Invalid OTP. {remaining} attempt(s) remaining."

    # Valid — mark as used
    execute("UPDATE otp_codes SET is_used = TRUE WHERE id = %s", (row["id"],))
    return dict(row), None


def _build_jwt(user_row: dict) -> dict:
    """Issue a JWT access token for the given user row."""
    access_token = create_access_token(
        identity=user_row["id"],
        additional_claims={
            "role":  user_row["role"],
            "email": user_row["email"],
            "name":  user_row["name"],
        },
    )
    return {
        "access_token": access_token,
        "token_type":   "Bearer",
        "user": {
            "id":    user_row["id"],
            "name":  user_row["name"],
            "email": user_row["email"],
            "role":  user_row["role"],
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def initiate_register(data: dict) -> tuple:
    """
    Register Step 1 — store OTP and send it via email.
    Returns (result_dict, error_str).
    """
    email = data["email"].lower().strip()
    name  = data.get("name", "").strip()
    role  = data.get("role", "user")

    existing = fetchone(
        "SELECT id FROM users WHERE email = %s AND is_deleted = FALSE", (email,)
    )
    if existing:
        return None, "An account with this email already exists. Please log in."

    _invalidate_old_otps(email, "register")
    _, err = _send_and_record_otp(email, "register", name=name, pending_role=role)
    if err:
        return None, err

    return {"email": email}, None


def verify_register_otp(data: dict) -> tuple:
    """
    Register Step 2 — verify OTP, create user, return JWT.
    Returns (result_dict, error_str).
    """
    email     = data["email"].lower().strip()
    plain_otp = data["otp"].strip()

    otp_row, err = _validate_otp(email, plain_otp, "register")
    if err:
        return None, err

    # Race condition guard
    existing = fetchone(
        "SELECT id FROM users WHERE email = %s AND is_deleted = FALSE", (email,)
    )
    if existing:
        return None, "Account already exists. Please log in."

    name = (otp_row.get("pending_name") or "User").strip()
    role = (otp_row.get("pending_role") or "user").strip()

    user_row = execute_returning(
        """
        INSERT INTO users (name, email, role)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (name, email, role)
    )

    # Link the OTP record to the new user
    execute(
        "UPDATE otp_codes SET user_id = %s WHERE id = %s",
        (user_row["id"], otp_row["id"])
    )

    logger.info(f"New user registered: {email} (role={role})")
    return _build_jwt(dict(user_row)), None


def initiate_login(data: dict) -> tuple:
    """
    Login Step 1 — verify user exists and send OTP.
    Returns (result_dict, error_str).
    """
    email = data["email"].lower().strip()

    user = fetchone(
        "SELECT * FROM users WHERE email = %s AND is_deleted = FALSE", (email,)
    )
    if not user:
        return None, "No account found with this email. Please register first."

    if not user["is_active"]:
        return None, "Your account has been deactivated. Please contact support."

    _invalidate_old_otps(email, "login")
    _, err = _send_and_record_otp(email, "login", name=user["name"])
    if err:
        return None, err

    return {"email": email}, None


def verify_login_otp(data: dict) -> tuple:
    """
    Login Step 2 — verify OTP and return JWT.
    Returns (result_dict, error_str).
    """
    email     = data["email"].lower().strip()
    plain_otp = data["otp"].strip()

    _, err = _validate_otp(email, plain_otp, "login")
    if err:
        return None, err

    user = fetchone(
        "SELECT * FROM users WHERE email = %s AND is_deleted = FALSE", (email,)
    )
    if not user:
        return None, "User not found."
    if not user["is_active"]:
        return None, "Account is deactivated."

    logger.info(f"User logged in: {email}")
    return _build_jwt(dict(user)), None


def revoke_token(jti: str):
    """Add a JWT's unique ID to the blocklist (logout)."""
    execute("INSERT INTO token_blocklist (jti) VALUES (%s) ON CONFLICT DO NOTHING", (jti,))
    logger.info(f"JWT revoked: jti={jti}")
