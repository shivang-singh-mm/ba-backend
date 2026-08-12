"""
OTP Utility
-----------
Handles OTP generation, SHA-256 hashing, and email delivery.
The raw OTP is NEVER persisted — only its hash is stored in the database.
"""

import os
import random
import string
import hashlib
from datetime import datetime, timedelta

from flask import current_app
from flask_mail import Message

from Core.extensions import mail
from Utils.logger import logger


def generate_otp() -> str:
    """
    Generate a random numeric OTP of configured length.

    Returns:
        Plain-text OTP string (e.g. "483920").
    """
    length = int(os.environ.get("OTP_LENGTH", 6))
    return "".join(random.choices(string.digits, k=length))


def hash_otp(otp: str) -> str:
    """
    Hash an OTP using SHA-256.

    Args:
        otp: Plain-text OTP string.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def verify_otp_hash(plain_otp: str, stored_hash: str) -> bool:
    """
    Verify a plain-text OTP against its stored SHA-256 hash.

    Args:
        plain_otp: OTP submitted by the user.
        stored_hash: SHA-256 hash stored in the database.

    Returns:
        True if they match, False otherwise.
    """
    return hash_otp(plain_otp) == stored_hash


def get_otp_expiry() -> datetime:
    """Return a UTC datetime representing when the OTP expires."""
    minutes = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
    return datetime.utcnow() + timedelta(minutes=minutes)


def send_otp_email(to_email: str, otp: str, purpose: str = "login", name: str = "") -> bool:
    """
    Send an OTP to the given email address.

    Args:
        to_email: Recipient email address.
        otp: Plain-text OTP (generated before hashing).
        purpose: 'register' or 'login'.
        name: Recipient's name for personalisation.

    Returns:
        True on success, False on failure.
    """
    app_name = current_app.config.get("APP_NAME", "BrandActivation")
    expiry_mins = current_app.config.get("OTP_EXPIRY_MINUTES", 10)

    subject_map = {
        "register": f"Welcome to {app_name} — Verify your email",
        "login": f"Your {app_name} login OTP",
    }

    greeting = f"Hi {name}," if name else "Hi,"

    body = f"""
{greeting}

{"Here is your verification code to complete registration:" if purpose == "register" else "Here is your one-time login code:"}

    ┌─────────────┐
    │  {otp}  │
    └─────────────┘

This code expires in {expiry_mins} minutes. Do not share it with anyone.

If you did not request this, please ignore this email.

— The {app_name} Team
"""

    try:
        msg = Message(
            subject=subject_map.get(purpose, f"Your {app_name} OTP"),
            recipients=[to_email],
            body=body.strip(),
        )
        mail.send(msg)
        logger.info(f"OTP email sent to {to_email} [purpose={purpose}]")
        return True
    except Exception as exc:
        logger.error(f"Failed to send OTP email to {to_email}: {exc}")
        return False
