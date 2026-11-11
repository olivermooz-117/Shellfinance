import pytest

from app import create_app
from app.extensions import db
from app.models import LedgerEntry, User


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-for-shellfinance-tests-32-bytes-minimum",
        "JWT_SECRET_KEY": "test-jwt-secret-for-shellfinance-tests-32-bytes-minimum",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, email="person@example.com"):
    return client.post("/api/auth/register", json={
        "email": email,
        "password": "correct-horse-battery-staple",
    })


def test_registration_hashes_password_and_authenticates(client, app):
    response = register(client)
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "person@example.com"

    with app.app_context():
        user = User.query.filter_by(email="person@example.com").one()
        assert user.password_hash != "correct-horse-battery-staple"
        assert user.check_password("correct-horse-battery-staple")

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.get_json()["user"]["email"] == "person@example.com"


def test_registration_rejects_short_password(client):
    response = client.post("/api/auth/register", json={
        "email": "short@example.com",
        "password": "short",
    })
    assert response.status_code == 400


def test_registration_rejects_duplicate_email(client):
    assert register(client).status_code == 201
    response = register(client)
    assert response.status_code == 409


def test_login_rejects_wrong_password(client):
    assert register(client).status_code == 201
    client.post("/api/auth/logout")
    response = client.post("/api/auth/login", json={
        "email": "person@example.com",
        "password": "not-the-correct-password",
    })
    assert response.status_code == 401


def test_login_accepts_correct_password(client):
    register(client)
    client.post("/api/auth/logout")

    response = client.post("/api/auth/login", json={
        "email": "person@example.com",
        "password": "correct-horse-battery-staple",
    })
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_financial_endpoints_require_authentication(client):
    response = client.get("/api/accounts")
    assert response.status_code == 401


def test_account_and_transaction_balance_use_decimal_ledger(client):
    assert register(client).status_code == 201

    account_response = client.post("/api/accounts", json={
        "name": "Main account",
        "account_type": "bank",
        "currency": "KES",
        "opening_balance": "1000.00",
    })
    assert account_response.status_code == 201
    account = account_response.get_json()["account"]
    assert account["balance"] == "1000.0000"

    transaction_response = client.post("/api/transactions", json={
        "account_id": account["id"],
        "transaction_type": "expense",
        "amount": "125.50",
        "category": "Food",
        "description": "Groceries",
    })
    assert transaction_response.status_code == 201
    assert transaction_response.get_json()["account_balance"] == "874.5000"

    ledger_response = client.get("/api/ledger")
    assert ledger_response.status_code == 200
    assert len(ledger_response.get_json()["entries"]) == 2


def test_users_cannot_access_each_others_accounts(client, app):
    register(client, "first@example.com")
    first_account = client.post("/api/accounts", json={
        "name": "Private account",
        "account_type": "bank",
        "currency": "KES",
        "opening_balance": "50",
    }).get_json()["account"]

    client.post("/api/auth/logout")
    register(client, "second@example.com")

    accounts = client.get("/api/accounts")
    assert accounts.status_code == 200
    assert accounts.get_json()["accounts"] == []

    transaction = client.post("/api/transactions", json={
        "account_id": first_account["id"],
        "transaction_type": "expense",
        "amount": "10",
        "category": "Test",
    })
    assert transaction.status_code == 404


def test_budget_goal_and_portfolio_creation(client):
    register(client)

    budget = client.post("/api/budgets", json={
        "category": "Food",
        "amount": "5000",
        "currency": "KES",
        "period": "monthly",
        "starts_on": "2026-11-01",
    })
    assert budget.status_code == 201

    goal = client.post("/api/goals", json={
        "name": "Emergency fund",
        "target_amount": "100000",
        "current_amount": "5000",
        "currency": "KES",
    })
    assert goal.status_code == 201

    portfolio = client.post("/api/portfolios", json={
        "name": "Long-term investments",
        "base_currency": "KES",
    })
    assert portfolio.status_code == 201
    portfolio_id = portfolio.get_json()["portfolio"]["id"]

    holding = client.post(f"/api/portfolios/{portfolio_id}/holdings", json={
        "asset_symbol": "TEST",
        "asset_name": "Test asset",
        "quantity": "2.5",
        "purchase_price": "100",
        "currency": "KES",
    })
    assert holding.status_code == 201


def test_ledger_entries_are_immutable(client, app):
    register(client)
    account = client.post("/api/accounts", json={
        "name": "Savings",
        "account_type": "bank",
        "currency": "KES",
        "opening_balance": "100",
    }).get_json()["account"]

    with app.app_context():
        entry = LedgerEntry.query.filter_by(account_id=account["id"]).one()
        entry.description = "Tampered entry"
        with pytest.raises(ValueError, match="immutable"):
            db.session.commit()
        db.session.rollback()
