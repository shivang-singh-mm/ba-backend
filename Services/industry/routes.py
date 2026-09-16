"""
Industry Routes — Flask Blueprint
------------------------------------
Endpoints for industry management.
"""

from flask import Blueprint, request

from .crud import create_industry, update_industry, get_industries
from Core.response import success_response, error_response

industry_bp = Blueprint("industry", __name__)


@industry_bp.route("/", methods=["POST"])
def create():
    """Create a new industry."""
    data = request.get_json(silent=True) or {}

    if not data.get("name"):
        return error_response("Missing required field: name", 400)

    result = create_industry(data)
    return success_response(data=result, message="Industry created successfully", status_code=201)


@industry_bp.route("/<int:industry_id>", methods=["PUT"])
def update(industry_id: int):
    """Update an industry by ID."""
    data = request.get_json(silent=True) or {}
    if not data:
        return error_response("No update data provided", 400)

    result = update_industry(industry_id, data)
    if not result:
        return error_response("Industry not found", 404)

    return success_response(data=result, message="Industry updated successfully")


@industry_bp.route("/", methods=["GET"])
def list_all():
    """Fetch all industries."""
    results = get_industries()
    return success_response(data=results, message="Industries fetched successfully")
