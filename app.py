from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env before anything reads os.environ
load_dotenv()

from Config.settings import config
from Core.extensions import jwt, mail
from Core.database import init_pool, close_pool
from Core.error_handlers import register_error_handlers

from Services.user.routes import user_bp
from Services.auth.routes import auth_bp
from Services.payment.routes import payment_bp
from Services.campaigns.routes import campaigns_bp


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)

    # psycopg2 connection pool
    with app.app_context():
        init_pool(app.config["DATABASE_URL"])

    # Teardown: return all connections on app shutdown
    @app.teardown_appcontext
    def shutdown_pool(exception=None):
        pass  # Pool is long-lived; close_pool() called at process exit if needed

    # ── JWT: Token Blocklist (logout) ─────────────────────────────────────────
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from Core.database import fetchone
        jti = jwt_payload["jti"]
        row = fetchone("SELECT id FROM token_blocklist WHERE jti = %s", (jti,))
        return row is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print("[JWT ERROR] Token has been revoked:", jwt_payload)
        return jsonify({"success": False, "message": "Token has been revoked. Please log in again."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("[JWT ERROR] Token has expired:", jwt_payload)
        return jsonify({"success": False, "message": "Token has expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print("[JWT ERROR] Invalid token signature:", error_string)
        return jsonify({"success": False, "message": "Signature verification failed.", "error": error_string}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        print("[JWT ERROR] Missing or malformed authorization header:", error_string)
        return jsonify({"success": False, "message": "Request is missing authorization token.", "error": error_string}), 401

    # ── Error Handlers ────────────────────────────────────────────────────────
    register_error_handlers(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp,      url_prefix="/api/auth")
    app.register_blueprint(user_bp,      url_prefix="/api/users")
    app.register_blueprint(payment_bp,   url_prefix="/api/payments")
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
