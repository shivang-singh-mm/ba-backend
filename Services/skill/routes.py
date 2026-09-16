"""
Skill Routes — Flask Blueprint
"""

from flask import Blueprint, request
from .crud import create_skill, update_skill, get_skills
from Core.response import success_response, error_response

skill_bp = Blueprint("skill", __name__)


@skill_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return error_response("Missing required field: name", 400)
    result = create_skill(data)
    return success_response(data=result, message="Skill created successfully", status_code=201)


@skill_bp.route("/<int:skill_id>", methods=["PUT"])
def update(skill_id: int):
    data = request.get_json(silent=True) or {}
    result = update_skill(skill_id, data)
    if not result:
        return error_response("Skill not found", 404)
    return success_response(data=result, message="Skill updated successfully")


@skill_bp.route("/", methods=["GET"])
def list_all():
    results = get_skills()
    return success_response(data=results, message="Skills fetched successfully")
