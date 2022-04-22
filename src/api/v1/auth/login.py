from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from api.v1.auth.tokens import get_access_jwt, get_refresh_jwt
from api.v1.crypto import cypher_password
from models.user import UserCredentials
from schemas.user import login_schema

login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("", methods=["POST"])
def login():
    request_data = request.json
    try:
        # Validate request body against schema data types
        login_data = login_schema.load(request_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    user = UserCredentials.query.filter_by(login=login_data["login"]).first()
    true_password = user.password

    if true_password == cypher_password(login_data["password"]):
        return {
            "access_token": get_access_jwt("a"),
            "refresh_token": get_refresh_jwt("b"),
        }, 200
    else:
        raise KeyError()
