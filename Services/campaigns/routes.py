from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import (
    get_all_campaigns,
    get_campaign_by_id,
    get_campaign_props,
    create_campaign,
    update_campaign,
    update_campaign_props,
    soft_delete_campaign,
    get_ai_session,
    upsert_ai_session,
)
from .ai import chat as ai_chat
from Core.response import success_response, error_response

campaigns_bp = Blueprint("campaigns", __name__)


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
    """Get a single campaign by ID."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign)


@campaigns_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign_route():
    """Create a new campaign draft with only a title."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    if not title:
        return error_response("title is required", 400)

    campaign = create_campaign(user_id=user_id, title=title)
    return success_response(data=campaign, message="Campaign created successfully", status_code=201)


@campaigns_bp.route("/<int:campaign_id>", methods=["PATCH"])
@jwt_required()
def patch_campaign_route(campaign_id: int):
    """Patch only the supplied campaign fields."""
    data = request.get_json(silent=True) or {}
    campaign = update_campaign(campaign_id, data)
    if not campaign:
        return error_response("Campaign not found", 404)
    return success_response(data=campaign, message="Campaign updated successfully")


@campaigns_bp.route("/<int:campaign_id>/props", methods=["GET"])
@jwt_required()
def get_campaign_props_route(campaign_id: int):
    """Get props for a campaign."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    props = get_campaign_props(campaign_id)
    return success_response(data=props)


@campaigns_bp.route("/<int:campaign_id>/props", methods=["PATCH"])
@jwt_required()
def patch_campaign_props_route(campaign_id: int):
    """Patch only the supplied campaign props fields."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)

    data = request.get_json(silent=True) or {}
    props = update_campaign_props(campaign_id, data)
    return success_response(data=props, message="Campaign props updated successfully")


@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])
@jwt_required()
def delete_campaign_route(campaign_id: int):
    """Soft-delete a campaign."""
    success = soft_delete_campaign(campaign_id)
    if not success:
        return error_response("Campaign not found", 404)
    return success_response(message="Campaign deleted successfully")


@campaigns_bp.route("/<int:campaign_id>/ai-chat", methods=["POST"])
@jwt_required()
def ai_chat_route(campaign_id: int):
    """
    AI-assisted campaign population.

    Request body: { "message": "<user free-text>" }

    Response:
      - While gathering info: { "reply": "<question>", "done": false }
      - Once populated:       { "reply": "<confirmation>", "done": true,
                                "campaign": {...}, "props": {...} }
    """
    user_id = int(get_jwt_identity())

    # ── Validate campaign ownership ──
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    if campaign["user_id"] != user_id:
        return error_response("Forbidden", 403)

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return error_response("message is required", 400)

    # ── Load config from Flask app ──
    cfg = current_app.config
    api_key   = cfg.get("OPENROUTER_API_KEY", "")
    model     = cfg.get("OPENROUTER_MODEL", "")
    site_url  = cfg.get("OPENROUTER_SITE_URL", "")
    site_name = cfg.get("OPENROUTER_SITE_NAME", "")

    if not api_key:
        return error_response("AI service is not configured", 503)

    # ── Load conversation history from DB ──
    history = get_ai_session(user_id, campaign_id)
    history = history + [{"role": "user", "content": user_message}]

    # ── Call AI ──
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

    # ── Persist updated conversation history ──
    upsert_ai_session(user_id, campaign_id, result["messages"])

    # ── If AI called the populate_campaign tool → write to DB ──
    if result["tool_call"]:
        args = result["tool_call"]

        # Split args into campaign fields vs props fields
        campaign_fields = {
            k: v for k, v in args.items()
            if k in ("description", "total_hours", "start_time",
                     "end_time", "date", "target", "locality")
            and v is not None
        }
        props_fields = {
            k: v for k, v in args.items()
            if k in ("stalls", "tables", "chairs", "led", "banners")
            and v is not None
        }

        updated_campaign = update_campaign(campaign_id, campaign_fields) if campaign_fields else campaign
        updated_props    = update_campaign_props(campaign_id, props_fields) if props_fields else get_campaign_props(campaign_id)

        confirmation = (
            result["reply"]
            or "Campaign populated successfully based on your description."
        )

        return success_response(
            data={
                "done":     True,
                "reply":    confirmation,
                "campaign": updated_campaign,
                "props":    updated_props,
            },
            message="Campaign populated by AI",
        )

    # ── AI is asking a follow-up question ──
    return success_response(
        data={
            "done":  False,
            "reply": result["reply"] or "Could you tell me more about your campaign?",
        },
        message="AI requires more information",
    )
