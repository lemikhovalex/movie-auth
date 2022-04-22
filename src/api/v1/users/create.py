import uuid

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from api.v1.crypto import cypher_password
from db.pg import db
from models.roles import UsersRoles
from models.user import UserCredentials, UserData
from schemas.user import register_schema

create_bp = Blueprint("create", __name__, url_prefix="")


@create_bp.route("", methods=["POST"])
def create():
    request_data = request.json
    try:
        # Validate request body against schema data types
        register_data = register_schema.load(request_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400
    new_user_id = uuid.uuid4()

    u_creds = UserCredentials(id=new_user_id, **register_data["credentials"])
    u_creds.password = cypher_password(u_creds.password)
    try:
        db.session.add(u_creds)
        db.session.commit()
    except IntegrityError as err:
        return str(err), 409

    u_data = UserData(user_id=new_user_id, **register_data["user_data"])
    db.session.add(u_data)

    role = UsersRoles(user_id=new_user_id, role_id=1)
    db.session.add(role)

    db.session.commit()

    data = {"user_id": new_user_id}
    return jsonify(data), 201


@create_bp.route("", methods=["GET"])
def get():
    print("\n\nin route\n\n", flush=True)
    return "get user"
