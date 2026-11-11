from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, event
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


class Account(db.Model):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("opening_balance >= 0", name="ck_accounts_opening_balance"),
        CheckConstraint("length(currency) = 3", name="ck_accounts_currency_length"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    opening_balance = db.Column(db.Numeric(20, 4), nullable=False, default=Decimal("0"))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self, balance=None):
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type,
            "currency": self.currency,
            "opening_balance": str(self.opening_balance),
            "balance": str(balance if balance is not None else self.opening_balance),
            "created_at": self.created_at.isoformat(),
        }


class FinancialTransaction(db.Model):
    __tablename__ = "financial_transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "transaction_type IN ('income', 'expense')",
            name="ck_transactions_type",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(20, 4), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(500))
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "currency": self.currency,
            "category": self.category,
            "description": self.description,
            "occurred_at": self.occurred_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class LedgerEntry(db.Model):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("signed_amount != 0", name="ck_ledger_nonzero_amount"),
        CheckConstraint(
            "entry_type IN ('opening_balance', 'income', 'expense')",
            name="ck_ledger_entry_type",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey("financial_transactions.id"),
        nullable=True,
        unique=True,
    )
    entry_type = db.Column(db.String(30), nullable=False)
    signed_amount = db.Column(db.Numeric(20, 4), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "transaction_id": self.transaction_id,
            "entry_type": self.entry_type,
            "signed_amount": str(self.signed_amount),
            "currency": self.currency,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        CheckConstraint(
            "period IN ('weekly', 'monthly', 'yearly')",
            name="ck_budgets_period",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Numeric(20, 4), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    period = db.Column(db.String(20), nullable=False, default="monthly")
    starts_on = db.Column(db.Date, nullable=False)
    ends_on = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "amount": str(self.amount),
            "currency": self.currency,
            "period": self.period,
            "starts_on": self.starts_on.isoformat(),
            "ends_on": self.ends_on.isoformat() if self.ends_on else None,
        }


class Goal(db.Model):
    __tablename__ = "financial_goals"
    __table_args__ = (
        CheckConstraint("target_amount > 0", name="ck_goals_target_positive"),
        CheckConstraint("current_amount >= 0", name="ck_goals_current_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Numeric(20, 4), nullable=False)
    current_amount = db.Column(db.Numeric(20, 4), nullable=False, default=Decimal("0"))
    currency = db.Column(db.String(3), nullable=False, default="KES")
    target_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "target_amount": str(self.target_amount),
            "current_amount": str(self.current_amount),
            "currency": self.currency,
            "target_date": self.target_date.isoformat() if self.target_date else None,
        }


class Portfolio(db.Model):
    __tablename__ = "investment_portfolios"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    base_currency = db.Column(db.String(3), nullable=False, default="KES")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "base_currency": self.base_currency,
            "created_at": self.created_at.isoformat(),
        }


class PortfolioHolding(db.Model):
    __tablename__ = "portfolio_holdings"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_holdings_quantity_positive"),
        CheckConstraint("purchase_price >= 0", name="ck_holdings_price_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(
        db.Integer, db.ForeignKey("investment_portfolios.id"), nullable=False, index=True
    )
    asset_symbol = db.Column(db.String(20), nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Numeric(24, 8), nullable=False)
    purchase_price = db.Column(db.Numeric(20, 4), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    purchased_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "asset_symbol": self.asset_symbol,
            "asset_name": self.asset_name,
            "quantity": str(self.quantity),
            "purchase_price": str(self.purchase_price),
            "currency": self.currency,
            "purchased_at": self.purchased_at.isoformat(),
        }


# Ledger rows are audit records: corrections must be represented by new entries.
@event.listens_for(LedgerEntry, "before_update")
def prevent_ledger_update(mapper, connection, target):
    raise ValueError("Ledger entries are immutable")


@event.listens_for(LedgerEntry, "before_delete")
def prevent_ledger_delete(mapper, connection, target):
    raise ValueError("Ledger entries cannot be deleted")
