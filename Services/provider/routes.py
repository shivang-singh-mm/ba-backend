"""
Provider Routes — Flask Blueprint
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .crud import (
    get_all_providers, get_provider_by_id, get_provider_by_user_id, create_provider_profile,
    update_provider_personal, update_provider_professional,
    get_provider_experiences, add_provider_experience, delete_provider_experience,
)
from Core.response import success_response, error_response

provider_bp = Blueprint("provider", __name__)


@provider_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_provider_profile():
    user_id = int(get_jwt_identity())
    result = get_provider_by_user_id(user_id)
    if not result:
        return error_response("Provider profile not found", 404)
    return success_response(data=result)


@provider_bp.route("/", methods=["POST"])
@jwt_required()
def create():

    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    result = create_provider_profile(user_id, data)
    return success_response(data=result, message="Provider profile created successfully", status_code=201)


@provider_bp.route("/", methods=["GET"])
def list_all():
    results = get_all_providers()
    return success_response(data=results, message="Providers fetched successfully")


@provider_bp.route("/<int:provider_id>", methods=["GET"])
def get_by_id(provider_id: int):
    result = get_provider_by_id(provider_id)
    if not result:
        return error_response("Provider profile not found", 404)
    return success_response(data=result)


@provider_bp.route("/<int:provider_id>/profile", methods=["PATCH"])
@jwt_required()
def patch_personal(provider_id: int):
    data = request.get_json(silent=True) or {}
    result = update_provider_personal(provider_id, data)
    if not result:
        return error_response("Provider profile not found", 404)
    return success_response(data=result, message="Personal profile updated successfully")


@provider_bp.route("/<int:provider_id>/professional", methods=["PATCH"])
@jwt_required()
def patch_professional(provider_id: int):
    data = request.get_json(silent=True) or {}
    result = update_provider_professional(provider_id, data)
    if not result:
        return error_response("Provider profile not found", 404)
    return success_response(data=result, message="Professional details updated successfully")


@provider_bp.route("/<int:provider_id>/experience", methods=["GET"])
def get_experiences(provider_id: int):
    results = get_provider_experiences(provider_id)
    return success_response(data=results, message="Experiences fetched successfully")


@provider_bp.route("/<int:provider_id>/experience", methods=["POST"])
@jwt_required()
def add_experience(provider_id: int):
    data = request.get_json(silent=True) or {}
    brand_name = data.get("brand_name")
    role_name = data.get("role_name")
    if not brand_name or not role_name:
        return error_response("brand_name and role_name are required", 400)
    exp = add_provider_experience(provider_id, data)
    return success_response(data=exp, message="Provider experience added successfully", status_code=201)


@provider_bp.route("/<int:provider_id>/experience/<int:exp_id>", methods=["DELETE"])
@jwt_required()
def delete_experience(provider_id: int, exp_id: int):
    success = delete_provider_experience(provider_id, exp_id)
    if not success:
        return error_response("Experience not found or unauthorised", 404)
    return success_response(message="Provider experience deleted successfully")


@provider_bp.route("/me/profile", methods=["PATCH"])
@jwt_required()
def patch_my_personal():
    user_id = int(get_jwt_identity())
    prov = get_provider_by_user_id(user_id)
    if not prov:
        return error_response("Provider profile not found", 404)
    data = request.get_json(silent=True) or {}
    result = update_provider_personal(prov["id"], data)
    return success_response(data=result, message="Personal profile updated successfully")


@provider_bp.route("/me/professional", methods=["PATCH"])
@jwt_required()
def patch_my_professional():
    user_id = int(get_jwt_identity())
    prov = get_provider_by_user_id(user_id)
    if not prov:
        return error_response("Provider profile not found", 404)
    data = request.get_json(silent=True) or {}
    result = update_provider_professional(prov["id"], data)
    return success_response(data=result, message="Professional details updated successfully")


@provider_bp.route("/me/experience", methods=["POST"])
@jwt_required()
def add_my_experience():
    user_id = int(get_jwt_identity())
    prov = get_provider_by_user_id(user_id)
    if not prov:
        return error_response("Provider profile not found", 404)
    data = request.get_json(silent=True) or {}
    brand_name = data.get("brand_name")
    role_name = data.get("role_name")
    if not brand_name or not role_name:
        return error_response("brand_name and role_name are required", 400)
    exp = add_provider_experience(prov["id"], data)
    return success_response(data=exp, message="Experience added successfully", status_code=201)


@provider_bp.route("/me/experience/<int:exp_id>", methods=["DELETE"])
@jwt_required()
def delete_my_experience(exp_id: int):
    user_id = int(get_jwt_identity())
    prov = get_provider_by_user_id(user_id)
    if not prov:
        return error_response("Provider profile not found", 404)
    success = delete_provider_experience(prov["id"], exp_id)
    if not success:
        return error_response("Experience not found or unauthorised", 404)
    return success_response(message="Experience deleted successfully")
