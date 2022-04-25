import json
import uuid

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from api.v1.auth import check
from db.pg import db
from models.roles import UsersRoles
from models.sessions import Session
from models.user import UserCredentials, UserData
from schemas.user import register_schema, user_data_schema
from utils.crypto import cypher_password

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("", methods=["POST"])
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
    print(f"created user with id={new_user_id}")
    return jsonify(data), 201


@bp.route("/<user_id>", methods=["GET"])
def read(user_id):
    user = UserData.query.filter_by(user_id=user_id).first()
    if user is None:
        return "", 404
    else:
        return user_data_schema.dump(user), 200


@bp.route("/<user_id>", methods=["PUT"])
def update(user_id):
    try:
        # Validate request body against schema data types
        user_data = user_data_schema.load(request.json)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    check_response, status = check()

    if status != 200:
        return check_response, status
    payload = json.loads(check_response)["payload"]

    if (payload["user_id"] == user_id) or (0 in payload["roles"]):
        UserData.query.filter_by(user_id=user_id).update(user_data)
        db.session.commit()
        return "", 200

    return "you cant edit this user", 400


@bp.route("/<user_id>", methods=["DELETE"])
def delete(user_id):
    check_response, status = check()

    if status != 200:
        return check_response, status
    payload = json.loads(check_response)["payload"]

    if (payload["user_id"] == user_id) or (0 in payload["roles"]):
        UserData.query.filter_by(user_id=user_id).delete()
        Session.query.filter_by(user_id=user_id).delete()
        UsersRoles.query.filter_by(user_id=user_id).delete()
        UserCredentials.query.filter_by(id=user_id).delete()
        db.session.commit()
        return "", 200
