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
from Services.location.routes import location_bp
from Services.industry.routes import industry_bp
from Services.skill.routes import skill_bp
from Services.language.routes import language_bp
from Services.provider.routes import provider_bp
from Services.brand.routes import brand_bp
from Services.matching.routes import matching_bp
from Services.dashboard.routes import dashboard_bp


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    # CORS — allow the configured frontend + both local dev ports
    _origins = [
        app.config.get("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",   # ba-web (Next.js)
        "http://localhost:8081",   # ba-android (Expo web)
        "http://127.0.0.1:8081",
        "http://127.0.0.1:3000",
    ]
    CORS(
        app,
        origins=_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    )
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
    app.register_blueprint(location_bp,  url_prefix="/api/location")
    app.register_blueprint(industry_bp,  url_prefix="/api/industry")
    app.register_blueprint(skill_bp,     url_prefix="/api/skill")
    app.register_blueprint(language_bp,  url_prefix="/api/language")
    app.register_blueprint(provider_bp,  url_prefix="/api/provider")
    app.register_blueprint(brand_bp,     url_prefix="/api/brand")
    app.register_blueprint(matching_bp,  url_prefix="/api/matching")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
