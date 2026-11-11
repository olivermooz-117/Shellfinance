import re

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def error(message, status):
    return jsonify({"success": False, "error": message}), status


def valid_email(value):
    return bool(
        isinstance(value, str)
        and len(value) <= 255
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value.strip())
    )


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not valid_email(email):
        return error("Enter a valid email address.", 400)
    if not isinstance(password, str) or len(password) < 12 or len(password) > 128:
        return error("Password must be between 12 and 128 characters.", 400)

    normalized_email = email.strip().lower()
    if User.query.filter_by(email=normalized_email).first():
        return error("An account with that email already exists.", 409)

    user = User(email=normalized_email)
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("An account with that email already exists.", 409)

    response = jsonify({"success": True, "user": user.to_dict()})
    set_access_cookies(response, create_access_token(identity=str(user.id)))
    return response, 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return error("Email and password are required.", 400)

    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not user.check_password(password):
        return error("Invalid email or password.", 401)

    response = jsonify({"success": True, "user": user.to_dict()})
    set_access_cookies(response, create_access_token(identity=str(user.id)))
    return response, 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    response = jsonify({"success": True, "message": "Logged out."})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return error("User account not found.", 404)
    return jsonify({"success": True, "user": user.to_dict()}), 200
