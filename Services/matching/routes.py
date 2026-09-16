"""
Matching Routes — Flask Blueprint
-----------------------------------
HTTP endpoints for generating, ranking, and retrieving campaign provider matches.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import (
    get_all_provider_candidates,
    save_match_results,
    get_saved_matches_for_campaign,
    get_all_matched_providers,
    get_match_by_id,
    update_match_status,
)
from .enum import MATCH_STATUS_ID
from .engine import run_matching_pipeline
from Services.campaigns.crud import get_campaign_by_id
from Core.response import success_response, error_response

matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/campaigns/<int:campaign_id>/run", methods=["POST"])
@jwt_required()
def run_campaign_matching(campaign_id: int):
    """
    Execute the hybrid matching pipeline for a campaign:
    1. Load campaign requirements & matching rules.
    2. Load candidate provider profiles, skills, languages, & experiences.
    3. Apply deterministic hard filters.
    4. Compute structured compatibility scores.
    5. Compute AI semantic experience fit (configurable model e.g. GPT-3.5).
    6. Aggregate weighted scores & rank candidates.
    7. Persist match records and return ranked results.
    """
    user_id = int(get_jwt_identity())

    # Verify campaign exists & user owns it
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    if campaign["user_id"] != user_id:
        return error_response("Forbidden: You do not own this campaign", 403)

    # 1. Fetch all provider candidate profiles
    candidates = get_all_provider_candidates()
    if not candidates:
        return success_response(
            data={"matches": [], "total_candidates_evaluated": 0, "eligible_count": 0},
            message="No active providers available in the system."
        )

    # 2. Extract configuration from Flask app config
    cfg = current_app.config
    weights = {
        "location":      float(cfg.get("MATCH_WEIGHT_LOCATION", 0.20)),
        "language":      float(cfg.get("MATCH_WEIGHT_LANGUAGE", 0.20)),
        "industry":      float(cfg.get("MATCH_WEIGHT_INDUSTRY", 0.15)),
        "skills":        float(cfg.get("MATCH_WEIGHT_SKILLS", 0.20)),
        "ai_experience": float(cfg.get("MATCH_WEIGHT_AI_EXPERIENCE", 0.25)),
    }

    ai_config = {
        "provider":           cfg.get("MATCHING_AI_PROVIDER", "openai"),
        "model":              cfg.get("MATCHING_AI_MODEL", "gpt-3.5-turbo"),
        "openai_api_key":     cfg.get("OPENAI_API_KEY", ""),
        "openrouter_api_key": cfg.get("OPENROUTER_API_KEY", ""),
        "site_url":           cfg.get("OPENROUTER_SITE_URL", "http://localhost:5000"),
        "site_name":          cfg.get("OPENROUTER_SITE_NAME", "BrandActivation"),
    }

    # 3. Execute matching pipeline
    matched_results = run_matching_pipeline(campaign, candidates, weights, ai_config)

    # 4. Save results to database
    saved_records = save_match_results(campaign_id, matched_results)

    return success_response(
        data={
            "campaign_id": campaign_id,
            "total_candidates_evaluated": len(candidates),
            "eligible_matches_count": len(saved_records),
            "matches": saved_records,
        },
        message="Matching pipeline executed successfully",
        status_code=200,
    )


@matching_bp.route("/campaigns/<int:campaign_id>", methods=["GET"])
@jwt_required()
def get_campaign_matches(campaign_id: int):
    """
    Retrieve previously calculated and stored match results for a campaign.
    Optional query param: ?min_score=50.0
    """
    user_id = int(get_jwt_identity())

    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return error_response("Campaign not found", 404)
    if campaign["user_id"] != user_id:
        return error_response("Forbidden", 403)

    min_score = request.args.get("min_score", type=float, default=0.0)
    saved_matches = get_saved_matches_for_campaign(campaign_id, min_score=min_score)

    return success_response(
        data={
            "campaign_id": campaign_id,
            "count": len(saved_matches),
            "matches": saved_matches,
        },
        message="Matches fetched successfully"
    )


@matching_bp.route("/providers", methods=["GET"])
@jwt_required()
def list_matched_providers():
    """
    List matched providers across campaigns with optional query filters:
    - ?campaign_id=12
    - ?provider_id=5
    - ?min_score=60.0
    - ?match_status=matched|shortlisted|contacted|accepted|rejected
    """
    user_id = int(get_jwt_identity())

    campaign_id = request.args.get("campaign_id", type=int)
    provider_id = request.args.get("provider_id", type=int)
    min_score = request.args.get("min_score", type=float, default=0.0)
    match_status = request.args.get("match_status", type=str)

    if campaign_id is not None:
        campaign = get_campaign_by_id(campaign_id)
        if not campaign:
            return error_response("Campaign not found", 404)
        if campaign["user_id"] != user_id:
            return error_response("Forbidden: You do not own this campaign", 403)
        matches = get_saved_matches_for_campaign(campaign_id, min_score=min_score)
        if match_status:
            matches = [m for m in matches if m.get("match_status") == match_status.lower()]
    else:
        matches = get_all_matched_providers(
            user_id=user_id,
            provider_id=provider_id,
            min_score=min_score,
            match_status=match_status,
        )

    return success_response(
        data={
            "count": len(matches),
            "matches": matches,
        },
        message="Matched providers fetched successfully"
    )


@matching_bp.route("/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match_detail(match_id: int):
    """
    Get detailed breakdown of a single campaign-provider match.
    """
    user_id = int(get_jwt_identity())

    match = get_match_by_id(match_id)
    if not match:
        return error_response("Match record not found", 404)

    # Allow campaign owner or the provider user to view
    if match.get("campaign_owner_id") != user_id and match.get("user_id") != user_id:
        return error_response("Forbidden", 403)

    return success_response(
        data=match,
        message="Match details fetched successfully"
    )


@matching_bp.route("/<int:match_id>/status", methods=["PATCH"])
@jwt_required()
def update_provider_match_status(match_id: int):
    """
    Update the status of a matched provider.
    Body: {"match_status": "shortlisted" | "contacted" | "accepted" | "rejected" | "matched"}
    """
    user_id = int(get_jwt_identity())

    match = get_match_by_id(match_id)
    if not match:
        return error_response("Match record not found", 404)

    if match.get("campaign_owner_id") != user_id:
        return error_response("Forbidden: Only campaign owner can update match status", 403)

    body = request.get_json(silent=True) or {}
    new_status = body.get("match_status")
    if not new_status or new_status.lower() not in MATCH_STATUS_ID:
        valid_statuses = list(MATCH_STATUS_ID.keys())
        return error_response(f"Invalid match_status. Allowed values: {valid_statuses}", 400)

    updated_match = update_match_status(match_id, new_status.lower())
    return success_response(
        data=updated_match,
        message=f"Match status updated to '{new_status}' successfully"
    )
