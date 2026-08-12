"""
Auth Routes
-----------
POST /api/auth/register        → Step 1: name + email + role → send OTP
POST /api/auth/verify-register → Step 2: email + otp → create user + JWT
POST /api/auth/login           → Step 1: email → send OTP
POST /api/auth/verify-login    → Step 2: email + otp → JWT
POST /api/auth/logout          → Revoke current JWT
GET  /api/auth/me              → Authenticated user profile
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from .crud import (
    initiate_register,
    verify_register_otp,
    initiate_login,
    verify_login_otp,
    revoke_token,
)
from Core.response import success_response, error_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Step 1: receive name + email + role, send OTP."""
    data = request.get_json(silent=True) or {}
    result, err = initiate_register(data)
    if err:
        return error_response(err, 400)
    return success_response(
        data=result,
        message="OTP sent to your email. Please verify to complete registration.",
    )


@auth_bp.route("/verify-register", methods=["POST"])
def verify_register():
    """Step 2: verify OTP, create account, return JWT."""
    data = request.get_json(silent=True) or {}
    result, err = verify_register_otp(data)
    if err:
        return error_response(err, 400)
    return success_response(data=result, message="Registration successful.", status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Step 1: receive email, send OTP."""
    data = request.get_json(silent=True) or {}
    result, err = initiate_login(data)
    if err:
        return error_response(err, 400)
    return success_response(data=result, message="OTP sent to your email.")


@auth_bp.route("/verify-login", methods=["POST"])
def verify_login():
    """Step 2: verify OTP, return JWT."""
    data = request.get_json(silent=True) or {}
    result, err = verify_login_otp(data)
    if err:
        return error_response(err, 401)
    return success_response(data=result, message="Login successful.")


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Revoke the current access token."""
    jti = get_jwt()["jti"]
    revoke_token(jti)
    return success_response(message="Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Return the current authenticated user's profile."""
    from Services.user.crud import get_user_by_id
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user)
