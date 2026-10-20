"""
Brand Routes — Flask Blueprint
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .crud import (
    get_all_brands, get_brand_by_id, get_brand_by_user_id, create_brand_profile,
    update_brand_personal, update_brand_associations
)
from Core.response import success_response, error_response

brand_bp = Blueprint("brand", __name__)


@brand_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_brand_profile():
    user_id = int(get_jwt_identity())
    result = get_brand_by_user_id(user_id)
    if not result:
        return error_response("Brand profile not found", 404)
    return success_response(data=result)


@brand_bp.route("/me/profile", methods=["PATCH"])
@jwt_required()
def patch_my_brand_personal():
    user_id = int(get_jwt_identity())
    brand = get_brand_by_user_id(user_id)
    if not brand:
        return error_response("Brand profile not found", 404)
    data = request.get_json(silent=True) or {}
    result = update_brand_personal(brand["id"], data)
    return success_response(data=result, message="Brand profile updated successfully")


@brand_bp.route("/me/associations", methods=["PATCH"])
@jwt_required()
def patch_my_brand_associations():
    user_id = int(get_jwt_identity())
    brand = get_brand_by_user_id(user_id)
    if not brand:
        return error_response("Brand profile not found", 404)
    data = request.get_json(silent=True) or {}
    result = update_brand_associations(brand["id"], data)
    return success_response(data=result, message="Brand associations updated successfully")


@brand_bp.route("/", methods=["POST"])
@jwt_required()
def create():

    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    if not data.get("brand_name"):
        return error_response("Missing required field: brand_name", 400)
    result = create_brand_profile(user_id, data)
    return success_response(data=result, message="Brand profile created successfully", status_code=201)


@brand_bp.route("/", methods=["GET"])
def list_all():
    results = get_all_brands()
    return success_response(data=results, message="Brands fetched successfully")


@brand_bp.route("/<int:brand_id>", methods=["GET"])
def get_by_id(brand_id: int):
    result = get_brand_by_id(brand_id)
    if not result:
        return error_response("Brand profile not found", 404)
    return success_response(data=result)


@brand_bp.route("/<int:brand_id>/profile", methods=["PATCH"])
@jwt_required()
def patch_personal(brand_id: int):
    data = request.get_json(silent=True) or {}
    result = update_brand_personal(brand_id, data)
    if not result:
        return error_response("Brand profile not found", 404)
    return success_response(data=result, message="Personal profile updated successfully")


@brand_bp.route("/<int:brand_id>/associations", methods=["PATCH"])
@jwt_required()
def patch_associations(brand_id: int):
    data = request.get_json(silent=True) or {}
    result = update_brand_associations(brand_id, data)
    if not result:
        return error_response("Brand profile not found", 404)
    return success_response(data=result, message="Associations details updated successfully")
