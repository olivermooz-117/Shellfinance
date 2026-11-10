import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db


def create_app(test_config=None):
    # Load the repository-root .env without overriding real environment variables.
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env", override=False)

    app = Flask(__name__)

    environment = os.getenv(
        "APP_ENV",
        os.getenv("FLASK_ENV", "development"),
    ).lower()

    if environment == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        if environment == "production":
            raise RuntimeError("SECRET_KEY must be configured in production")
        app.config["SECRET_KEY"] = "local-development-only-change-me"

    db.init_app(app)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [frontend_url],
            }
        },
    )

    @app.get("/api/health")
    def health():
        return jsonify({
            "success": True,
            "service": "ShellFinance API",
            "status": "healthy",
            "version": "0.1.0",
        }), 200

    @app.get("/api/health/database")
    def database_health():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify({
                "success": True,
                "database": "connected",
            }), 200

        except Exception:
            db.session.rollback()
            app.logger.exception("Database health check failed")

            return jsonify({
                "success": False,
                "database": "unavailable",
            }), 503

        finally:
            db.session.remove()

    return app
