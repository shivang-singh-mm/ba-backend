"""
Dashboard Routes — Flask Blueprint
-----------------------------------
GET /api/dashboard/?role=provider|brand
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import get_provider_dashboard, get_brand_dashboard
from Core.response import success_response, error_response
from Core.database import fetchone

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    """
    Returns dashboard payload based on role requested (or user's default role).
    Query parameter: ?role=provider | brand
    """
    user_id = int(get_jwt_identity())
    
    # Check requested role from query param, or fallback to user role in DB
    role_param = (request.args.get("role") or "").lower().strip()
    
    if not role_param:
        user_row = fetchone("SELECT role FROM users WHERE id = %s", (user_id,))
        if user_row:
            role_param = "brand" if user_row["role"] == "brand" else "provider"
        else:
            role_param = "provider"

    if role_param in ("provider", "talent", "user"):
        data = get_provider_dashboard(user_id)
        return success_response(data=data, message="Provider dashboard data fetched successfully")
    elif role_param in ("brand", "agency"):
        data = get_brand_dashboard(user_id)
        return success_response(data=data, message="Brand dashboard data fetched successfully")
    else:
        return error_response(f"Unsupported role: '{role_param}'. Expected 'provider' or 'brand'.", 400)
