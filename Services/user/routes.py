from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import (
    get_all_users,
    get_user_by_id,
    update_user,
    soft_delete_user,
)
from Core.response import success_response, error_response
from Core.middleware import admin_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    """Get authenticated user's profile."""
    user_id = int(get_jwt_identity())
    user = get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user)


@user_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    """Update profile parameters for the current user."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    # Ensure role cannot be updated directly by user
    data.pop("role", None)
    user = update_user(user_id, data)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user, message="Profile updated successfully")


@user_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    """Get all users (admin only)."""
    users = get_all_users()
    return success_response(data=users, message="Users fetched successfully")


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get a single user by ID."""
    user = get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user_route(user_id):
    """Update a user's name, phone or role."""
    data = request.get_json(silent=True) or {}
    user = update_user(user_id, data)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user, message="User updated successfully")


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user_route(user_id):
    """Soft-delete a user (admin only)."""
    success = soft_delete_user(user_id)
    if not success:
        return error_response("User not found", 404)
    return success_response(message="User deleted successfully")

