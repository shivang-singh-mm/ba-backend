from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import get_all_campaigns, get_campaign_by_id, create_campaign, update_campaign, soft_delete_campaign
from Core.response import success_response, error_response

campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.route("/", methods=["GET"])
@jwt_required()
def list_campaigns():
    """List campaigns for the authenticated user."""
    user_id = get_jwt_identity()
    campaigns = get_all_campaigns(user_id=user_id)
    return success_response(data=campaigns, message="Campaigns fetched successfully")


@campaigns_bp.route("/<int:campaign_id>", methods=["GET"])
@jwt_required()
def get_campaign(campaign_id):
    """Get a single campaign by ID."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign)


@campaigns_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign_route():
    """Create a new campaign."""
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    campaign = create_campaign(
        user_id=user_id,
        title=data.get("title"),
        description=data.get("description"),
        budget=data.get("budget"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
    )
    return success_response(data=campaign, message="Campaign created successfully", status_code=201)


@campaigns_bp.route("/<int:campaign_id>", methods=["PUT"])
@jwt_required()
def update_campaign_route(campaign_id):
    """Update a campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign updated successfully")


@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required()
def delete_campaign_route(campaign_id):
    """Soft-delete a campaign."""
    success = soft_delete_campaign(campaign_id)
    if not success:
        return error_response("Campaign not found", 404)
    return success_response(message="Campaign deleted successfully")
