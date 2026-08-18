from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .crud import get_payments_by_user, get_payment_by_id, create_payment, update_payment_status
from Core.response import success_response, error_response

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/", methods=["GET"])
@jwt_required()
def list_payments():
    """List all payments for the authenticated user."""
    user_id = int(get_jwt_identity())
    payments = get_payments_by_user(user_id)
    return success_response(data=payments, message="Payments fetched successfully")


@payment_bp.route("/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):
    """Get a single payment by ID."""
    user_id = int(get_jwt_identity())
    payment = get_payment_by_id(payment_id, user_id)
    if not payment:
        return error_response("Payment not found", 404)
    return success_response(data=payment)


@payment_bp.route("/", methods=["POST"])
@jwt_required()
def create_payment_route():
    """Create a new payment record."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    payment = create_payment(
        user_id=user_id,
        amount=data.get("amount"),
        currency=data.get("currency", "INR"),
        gateway=data.get("gateway"),
        description=data.get("description"),
    )
    return success_response(data=payment, message="Payment created successfully", status_code=201)
