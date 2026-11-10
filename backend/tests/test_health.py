from app import create_app


def test_api_health():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["service"] == "ShellFinance API"
    assert data["status"] == "healthy"
