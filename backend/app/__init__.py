import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, jwt, migrate

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env", override=False)


def create_app(test_config=None):
    app = Flask(__name__)

    environment = os.getenv(
        "APP_ENV", os.getenv("FLASK_ENV", "development")
    ).lower()

    app.config.from_object(
        ProductionConfig if environment == "production" else DevelopmentConfig
    )

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        if environment == "production":
            raise RuntimeError("SECRET_KEY must be configured in production")
        app.config["SECRET_KEY"] = "local-development-only-change-me"

    if not app.config.get("JWT_SECRET_KEY"):
        if environment == "production":
            raise RuntimeError("JWT_SECRET_KEY or SECRET_KEY must be configured in production")
        app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    if app.config.get("TESTING"):
        app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic can discover all mapped tables.
    from app import models  # noqa: F401
    from app.routes.auth import auth_bp
    from app.routes.finance import finance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(finance_bp)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS(
        app,
        resources={r"/api/*": {"origins": [frontend_url]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRF-TOKEN"],
        methods=["GET", "POST", "OPTIONS"],
    )

    @app.get("/api/health")
    def health():
        return jsonify({
            "success": True,
            "service": "ShellFinance API",
            "status": "healthy",
            "version": "0.2.0",
        }), 200

    @app.get("/api/health/database")
    def database_health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"success": True, "database": "connected"}), 200
        except Exception:
            db.session.rollback()
            app.logger.exception("Database health check failed")
            return jsonify({"success": False, "database": "unavailable"}), 503
        finally:
            db.session.remove()

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"success": False, "error": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"success": False, "error": "Invalid authentication token."}), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": "Authentication has expired."}), 401

    return app
