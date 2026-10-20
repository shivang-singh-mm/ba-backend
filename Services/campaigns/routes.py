"""
Campaigns Routes — Flask Blueprint
------------------------------------
All HTTP endpoints for campaign creation, sectioned updates, retrieval, and AI interaction.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import (
    get_all_campaigns,
    get_campaign_by_id,
    create_campaign,
    update_campaign_basics,
    update_campaign_products,
    update_campaign_associations,
    update_campaign_venue,
    update_campaign_audience,
    update_campaign_languages,
    update_campaign_skills,
    update_campaign_props,
    update_campaign_matching_rules,
    soft_delete_campaign,
    get_campaign_types,
    get_venue_types,
    get_ai_session,
    upsert_ai_session,
)
from .ai import chat as ai_chat
from Core.response import success_response, error_response

campaigns_bp = Blueprint("campaigns", __name__)


# ── Metadata / Types ─────────────────────────────────────────────────────────

@campaigns_bp.route("/meta/types", methods=["GET"])
def get_types_meta():
    """Fetch campaign types and venue types."""
    c_types = get_campaign_types()
    v_types = get_venue_types()
    return success_response(
        data={"campaign_types": c_types, "venue_types": v_types},
        message="Campaign meta fetched successfully"
    )


# ── Core Campaign CRUD ───────────────────────────────────────────────────────

@campaigns_bp.route("/", methods=["GET"])
@jwt_required()
def list_campaigns():
    """List all campaigns for the authenticated user."""
    user_id = int(get_jwt_identity())
    campaigns = get_all_campaigns(user_id=user_id)
    return success_response(data=campaigns, message="Campaigns fetched successfully")


@campaigns_bp.route("/<int:campaign_id>", methods=["GET"])
@jwt_required()
def get_campaign(campaign_id: int):
    """Get a single campaign by ID with all relations."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign)


@campaigns_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign_route():
    """Create a new campaign draft with minimum required fields (title)."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    if not title:
        return error_response("Missing required field: title", 400)

    campaign = create_campaign(user_id=user_id, data=data)
    return success_response(data=campaign, message="Campaign created successfully", status_code=201)


@campaigns_bp.route("/<int:campaign_id>/basics", methods=["PATCH"])
@jwt_required()
def patch_campaign_basics(campaign_id: int):
    """Patch core campaign fields (title, date, city, timings, locality, status, etc.)."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_basics(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign basics updated successfully")


@campaigns_bp.route("/<int:campaign_id>/products", methods=["PATCH"])
@jwt_required()
def patch_campaign_products(campaign_id: int):
    """Patch products associated with the campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_products(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign products updated successfully")


@campaigns_bp.route("/<int:campaign_id>/associations", methods=["PATCH"])
@jwt_required()
def patch_campaign_associations(campaign_id: int):
    """Patch industries and campaign types."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_associations(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign associations updated successfully")


@campaigns_bp.route("/<int:campaign_id>/venue", methods=["PATCH"])
@jwt_required()
def patch_campaign_venue(campaign_id: int):
    """Patch venues for the campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_venue(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign venue updated successfully")


@campaigns_bp.route("/<int:campaign_id>/audience", methods=["PATCH"])
@jwt_required()
def patch_campaign_audience(campaign_id: int):
    """Patch audience targeting and demographics."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_audience(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign audience updated successfully")


@campaigns_bp.route("/<int:campaign_id>/languages", methods=["PATCH"])
@jwt_required()
def patch_campaign_languages(campaign_id: int):
    """Patch language requirements for the campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_languages(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign languages updated successfully")


@campaigns_bp.route("/<int:campaign_id>/skills", methods=["PATCH"])
@jwt_required()
def patch_campaign_skills(campaign_id: int):
    """Patch required skills for the campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_skills(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign skills updated successfully")


@campaigns_bp.route("/<int:campaign_id>/props", methods=["PATCH"])
@jwt_required()
def patch_campaign_props(campaign_id: int):
    """Patch equipment & props requirements."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_props(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign props updated successfully")


@campaigns_bp.route("/<int:campaign_id>/matching-rules", methods=["POST", "PATCH"])
@jwt_required()
def set_campaign_matching_rules(campaign_id: int):
    """Set or update candidate matching rules for the campaign."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign_matching_rules(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign matching rules updated successfully")


@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])

@jwt_required()
def delete_campaign_route(campaign_id: int):
    """Soft-delete a campaign."""
    success = soft_delete_campaign(campaign_id)
    if not success:
        return error_response("Campaign not found", 404)
    return success_response(message="Campaign deleted successfully")


# ── AI Assisted Planning ────────────────────────────────────────────────────

@campaigns_bp.route("/<int:campaign_id>/ai-chat", methods=["POST"])
@jwt_required()
def ai_chat_route(campaign_id: int):
    """AI-assisted campaign planning and auto-population."""
    user_id = int(get_jwt_identity())

    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    if campaign["user_id"] != user_id:
        return error_response("Forbidden", 403)

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return error_response("message is required", 400)

    cfg = current_app.config
    api_key   = cfg.get("OPENROUTER_API_KEY", "")
    model     = cfg.get("OPENROUTER_MODEL", "")
    site_url  = cfg.get("OPENROUTER_SITE_URL", "")
    site_name = cfg.get("OPENROUTER_SITE_NAME", "")

    if not api_key:
        return error_response("AI service is not configured", 503)

    history = get_ai_session(user_id, campaign_id)
    history = history + [{"role": "user", "content": user_message}]

    try:
        result = ai_chat(
            messages=history,
            api_key=api_key,
            model=model,
            site_url=site_url,
            site_name=site_name,
        )
    except RuntimeError as exc:
        return error_response(str(exc), 503)

    upsert_ai_session(user_id, campaign_id, result["messages"])

    if result["tool_call"]:
        args = result["tool_call"]

        campaign_fields = {
            k: v for k, v in args.items()
            if k in ("description", "total_hours", "start_time", "end_time", "date", "locality", "city_id")
            and v is not None
        }
        props_fields = {
            k: v for k, v in args.items()
            if k in ("stalls", "tables", "chairs", "led", "banners", "other_requirements")
            and v is not None
        }

        if campaign_fields:
            update_campaign_basics(campaign_id, campaign_fields)
        if props_fields:
            update_campaign_props(campaign_id, props_fields)

        full_campaign = get_campaign_by_id(campaign_id)
        confirmation = (
            result["reply"]
            or "Campaign details populated successfully."
        )

        return success_response(
            data={
                "done":     True,
                "reply":    confirmation,
                "campaign": full_campaign,
            },
            message="Campaign populated by AI",
        )

    return success_response(
        data={
            "done":  False,
            "reply": result["reply"] or "Could you tell me more about your campaign requirements?",
        },
        message="AI requires more information",
    )
