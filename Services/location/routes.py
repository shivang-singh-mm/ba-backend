"""
Location Routes — Flask Blueprint
------------------------------------
Unified endpoints for country, state, and city management.
"""

from flask import Blueprint, request

from .crud import (
    create_country, create_state, create_city,
    update_country, update_state, update_city,
    get_countries, get_states, get_cities,
)
from Core.response import success_response, error_response
from Utils.logger import logger

location_bp = Blueprint("location", __name__)

# Maps the URL entity param to (create_fn, update_fn, get_fn, required_fields_for_create)
_ENTITY_MAP = {
    "country": {
        "create": create_country,
        "update": update_country,
        "get":    get_countries,
        "required": ["name", "country_code", "phone_code"],
    },
    "state": {
        "create": create_state,
        "update": update_state,
        "get":    get_states,
        "required": ["name", "country_id"],
    },
    "city": {
        "create": create_city,
        "update": update_city,
        "get":    get_cities,
        "required": ["name", "state_id"],
    },
}


@location_bp.route("/<entity>", methods=["POST"])
def create_entity(entity: str):
    """Create a country, state, or city based on the URL entity param."""
    config = _ENTITY_MAP.get(entity)
    if not config:
        return error_response(f"Unknown entity: {entity}", 400)

    data = request.get_json(silent=True) or {}

    # Simple presence check for required fields
    missing = [f for f in config["required"] if not data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    result = config["create"](data)
    return success_response(data=result, message=f"{entity.capitalize()} created successfully", status_code=201)


@location_bp.route("/<entity>/<int:entity_id>", methods=["PUT"])
def update_entity(entity: str, entity_id: int):
    """Update a country, state, or city by ID."""
    config = _ENTITY_MAP.get(entity)
    if not config:
        return error_response(f"Unknown entity: {entity}", 400)

    data = request.get_json(silent=True) or {}
    if not data:
        return error_response("No update data provided", 400)

    result = config["update"](entity_id, data)
    if not result:
        return error_response(f"{entity.capitalize()} not found", 404)

    return success_response(data=result, message=f"{entity.capitalize()} updated successfully")


@location_bp.route("/<entity>", methods=["GET"])
def list_entities(entity: str):
    """Fetch a list of countries, states, or cities with optional filters."""
    config = _ENTITY_MAP.get(entity)
    if not config:
        return error_response(f"Unknown entity: {entity}", 400)

    filters = {
        "country_id": request.args.get("country_id"),
        "state_id":   request.args.get("state_id"),
    }

    results = config["get"](filters)
    return success_response(data=results, message=f"{entity.capitalize()} list fetched successfully")
