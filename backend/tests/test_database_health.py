from app import create_app
from app.extensions import db


def make_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_database_health_connected(monkeypatch):
    client = make_client()
    monkeypatch.setattr(db.session, "execute", lambda *args, **kwargs: None)

    response = client.get("/api/health/database")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "database": "connected"}


def test_database_health_unavailable(monkeypatch):
    client = make_client()

    def fail(*args, **kwargs):
        raise RuntimeError("database down")

    monkeypatch.setattr(db.session, "execute", fail)

    response = client.get("/api/health/database")

    assert response.status_code == 503
    assert response.get_json() == {"success": False, "database": "unavailable"}
