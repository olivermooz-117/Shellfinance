from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import (
    Account,
    Budget,
    FinancialTransaction,
    Goal,
    LedgerEntry,
    Portfolio,
    PortfolioHolding,
)

finance_bp = Blueprint("finance", __name__, url_prefix="/api")


def user_id():
    return int(get_jwt_identity())


def fail(message, status=400):
    return jsonify({"success": False, "error": message}), status


def decimal_value(value, *, positive=False, nonnegative=False):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not amount.is_finite():
        return None
    if positive and amount <= 0:
        return None
    if nonnegative and amount < 0:
        return None
    if abs(amount) >= Decimal("1000000000000000"):
        return None
    return amount


def currency_value(value):
    if not isinstance(value, str):
        return None
    value = value.strip().upper()
    return value if len(value) == 3 and value.isalpha() else None


def account_balance(account):
    total = db.session.query(func.coalesce(func.sum(LedgerEntry.signed_amount), 0)).filter_by(
        user_id=user_id(), account_id=account.id
    ).scalar()
    return Decimal(str(total))


@finance_bp.get("/accounts")
@jwt_required()
def list_accounts():
    accounts = Account.query.filter_by(user_id=user_id()).order_by(Account.id).all()
    return jsonify({
        "success": True,
        "accounts": [a.to_dict(account_balance(a)) for a in accounts],
    })


@finance_bp.post("/accounts")
@jwt_required()
def create_account():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    account_type = data.get("account_type")
    currency = currency_value(data.get("currency", "KES"))
    opening = decimal_value(data.get("opening_balance", "0"), nonnegative=True)

    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return fail("Account name is required (maximum 120 characters).")
    if account_type not in {"cash", "bank", "mobile_money", "credit", "other"}:
        return fail("Unsupported account type.")
    if not currency:
        return fail("Currency must be a three-letter code.")
    if opening is None:
        return fail("Opening balance must be a non-negative decimal.")

    account = Account(
        user_id=user_id(),
        name=name.strip(),
        account_type=account_type,
        currency=currency,
        opening_balance=opening,
    )
    db.session.add(account)
    db.session.flush()

    if opening:
        db.session.add(LedgerEntry(
            user_id=user_id(),
            account_id=account.id,
            entry_type="opening_balance",
            signed_amount=opening,
            currency=currency,
            description="Opening balance",
        ))

    db.session.commit()
    return jsonify({"success": True, "account": account.to_dict(account_balance(account))}), 201


@finance_bp.get("/transactions")
@jwt_required()
def list_transactions():
    rows = FinancialTransaction.query.filter_by(user_id=user_id()).order_by(
        FinancialTransaction.occurred_at.desc(), FinancialTransaction.id.desc()
    ).limit(500).all()
    return jsonify({"success": True, "transactions": [row.to_dict() for row in rows]})


@finance_bp.post("/transactions")
@jwt_required()
def create_transaction():
    data = request.get_json(silent=True) or {}
    account = Account.query.filter_by(
        id=data.get("account_id"), user_id=user_id()
    ).first()
    if not account:
        return fail("Account not found.", 404)

    transaction_type = data.get("transaction_type")
    if transaction_type not in {"income", "expense"}:
        return fail("Transaction type must be income or expense.")

    amount = decimal_value(data.get("amount"), positive=True)
    if amount is None:
        return fail("Amount must be a positive decimal.")

    category = data.get("category")
    if not isinstance(category, str) or not category.strip() or len(category.strip()) > 80:
        return fail("Category is required (maximum 80 characters).")

    description = data.get("description")
    if description is not None and (
        not isinstance(description, str) or len(description) > 500
    ):
        return fail("Description must be 500 characters or fewer.")

    occurred_at = datetime.now(timezone.utc)
    if data.get("occurred_at"):
        try:
            occurred_at = datetime.fromisoformat(
                data["occurred_at"].replace("Z", "+00:00")
            )
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            return fail("occurred_at must be an ISO 8601 date-time.")

    transaction = FinancialTransaction(
        user_id=user_id(),
        account_id=account.id,
        transaction_type=transaction_type,
        amount=amount,
        currency=account.currency,
        category=category.strip(),
        description=description,
        occurred_at=occurred_at,
    )
    db.session.add(transaction)
    db.session.flush()

    signed_amount = amount if transaction_type == "income" else -amount
    db.session.add(LedgerEntry(
        user_id=user_id(),
        account_id=account.id,
        transaction_id=transaction.id,
        entry_type=transaction_type,
        signed_amount=signed_amount,
        currency=account.currency,
        description=description or category.strip(),
    ))
    db.session.commit()
    return jsonify({
        "success": True,
        "transaction": transaction.to_dict(),
        "account_balance": str(account_balance(account)),
    }), 201


@finance_bp.get("/budgets")
@jwt_required()
def list_budgets():
    rows = Budget.query.filter_by(user_id=user_id()).order_by(Budget.id).all()
    return jsonify({"success": True, "budgets": [row.to_dict() for row in rows]})


@finance_bp.post("/budgets")
@jwt_required()
def create_budget():
    data = request.get_json(silent=True) or {}
    amount = decimal_value(data.get("amount"), positive=True)
    category = data.get("category")
    period = data.get("period", "monthly")
    currency = currency_value(data.get("currency", "KES"))

    if amount is None:
        return fail("Budget amount must be positive.")
    if not isinstance(category, str) or not category.strip() or len(category.strip()) > 80:
        return fail("Budget category is required.")
    if period not in {"weekly", "monthly", "yearly"}:
        return fail("Period must be weekly, monthly or yearly.")
    if not currency:
        return fail("Currency must be a three-letter code.")
    try:
        starts_on = date.fromisoformat(data["starts_on"])
        ends_on = date.fromisoformat(data["ends_on"]) if data.get("ends_on") else None
    except (KeyError, ValueError, TypeError):
        return fail("starts_on is required and dates must use YYYY-MM-DD.")
    if ends_on and ends_on < starts_on:
        return fail("ends_on cannot be before starts_on.")

    row = Budget(
        user_id=user_id(), category=category.strip(), amount=amount,
        currency=currency, period=period, starts_on=starts_on, ends_on=ends_on,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({"success": True, "budget": row.to_dict()}), 201


@finance_bp.get("/goals")
@jwt_required()
def list_goals():
    rows = Goal.query.filter_by(user_id=user_id()).order_by(Goal.id).all()
    return jsonify({"success": True, "goals": [row.to_dict() for row in rows]})


@finance_bp.post("/goals")
@jwt_required()
def create_goal():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    target = decimal_value(data.get("target_amount"), positive=True)
    current = decimal_value(data.get("current_amount", "0"), nonnegative=True)
    currency = currency_value(data.get("currency", "KES"))

    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return fail("Goal name is required.")
    if target is None or current is None:
        return fail("Goal amounts must be valid decimals; target must be positive.")
    if current > target:
        return fail("Current amount cannot exceed target amount.")
    if not currency:
        return fail("Currency must be a three-letter code.")
    try:
        target_date = date.fromisoformat(data["target_date"]) if data.get("target_date") else None
    except (ValueError, TypeError):
        return fail("target_date must use YYYY-MM-DD.")

    row = Goal(
        user_id=user_id(), name=name.strip(), target_amount=target,
        current_amount=current, currency=currency, target_date=target_date,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({"success": True, "goal": row.to_dict()}), 201


@finance_bp.get("/portfolios")
@jwt_required()
def list_portfolios():
    rows = Portfolio.query.filter_by(user_id=user_id()).order_by(Portfolio.id).all()
    return jsonify({"success": True, "portfolios": [row.to_dict() for row in rows]})


@finance_bp.post("/portfolios")
@jwt_required()
def create_portfolio():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    currency = currency_value(data.get("base_currency", "KES"))
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return fail("Portfolio name is required.")
    if not currency:
        return fail("Base currency must be a three-letter code.")
    row = Portfolio(user_id=user_id(), name=name.strip(), base_currency=currency)
    db.session.add(row)
    db.session.commit()
    return jsonify({"success": True, "portfolio": row.to_dict()}), 201


@finance_bp.get("/portfolios/<int:portfolio_id>/holdings")
@jwt_required()
def list_holdings(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id()).first()
    if not portfolio:
        return fail("Portfolio not found.", 404)
    rows = PortfolioHolding.query.filter_by(portfolio_id=portfolio.id).order_by(
        PortfolioHolding.id
    ).all()
    return jsonify({"success": True, "holdings": [row.to_dict() for row in rows]})


@finance_bp.post("/portfolios/<int:portfolio_id>/holdings")
@jwt_required()
def create_holding(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id()).first()
    if not portfolio:
        return fail("Portfolio not found.", 404)

    data = request.get_json(silent=True) or {}
    symbol = data.get("asset_symbol")
    name = data.get("asset_name")
    quantity = decimal_value(data.get("quantity"), positive=True)
    price = decimal_value(data.get("purchase_price"), nonnegative=True)
    currency = currency_value(data.get("currency", portfolio.base_currency))

    if not isinstance(symbol, str) or not symbol.strip() or len(symbol.strip()) > 20:
        return fail("Asset symbol is required.")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        return fail("Asset name is required.")
    if quantity is None or price is None:
        return fail("Quantity must be positive and purchase price non-negative.")
    if not currency:
        return fail("Currency must be a three-letter code.")

    row = PortfolioHolding(
        portfolio_id=portfolio.id, asset_symbol=symbol.strip().upper(),
        asset_name=name.strip(), quantity=quantity, purchase_price=price,
        currency=currency,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({"success": True, "holding": row.to_dict()}), 201


@finance_bp.get("/ledger")
@jwt_required()
def list_ledger():
    rows = LedgerEntry.query.filter_by(user_id=user_id()).order_by(
        LedgerEntry.id.desc()
    ).limit(500).all()
    return jsonify({"success": True, "entries": [row.to_dict() for row in rows]})
