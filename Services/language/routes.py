"""
Language Routes — Flask Blueprint
"""

from flask import Blueprint, request
from .crud import create_language, update_language, get_languages
from Core.response import success_response, error_response

language_bp = Blueprint("language", __name__)


@language_bp.route("/", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return error_response("Missing required field: name", 400)
    result = create_language(data)
    return success_response(data=result, message="Language created successfully", status_code=201)


@language_bp.route("/<int:language_id>", methods=["PUT"])
def update(language_id: int):
    data = request.get_json(silent=True) or {}
    result = update_language(language_id, data)
    if not result:
        return error_response("Language not found", 404)
    return success_response(data=result, message="Language updated successfully")


@language_bp.route("/", methods=["GET"])
def list_all():
    results = get_languages()
    return success_response(data=results, message="Languages fetched successfully")
