from unittest.mock import patch

from app import create_app


def create_test_app():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })


def test_api_health():
    app = create_test_app()

    response = app.test_client().get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["service"] == "ShellFinance API"
    assert data["status"] == "healthy"


def test_database_health_with_working_database():
    app = create_test_app()

    response = app.test_client().get("/api/health/database")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["database"] == "connected"


def test_database_health_when_database_is_unavailable():
    app = create_test_app()

    with patch(
        "app.db.session.execute",
        side_effect=RuntimeError("Database unavailable"),
    ):
        response = app.test_client().get("/api/health/database")

    assert response.status_code == 503

    data = response.get_json()

    assert data["success"] is False
    assert data["database"] == "unavailable"


def test_production_requires_secret_key():
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False):
        with patch.dict(os.environ, {"SECRET_KEY": ""}):
            try:
                create_app({
                    "TESTING": True,
                    "SECRET_KEY": "",
                })
            except RuntimeError as error:
                assert "SECRET_KEY" in str(error)
            else:
                raise AssertionError(
                    "Production should refuse to start without SECRET_KEY"
                )
