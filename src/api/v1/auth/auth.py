import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from api.v1.auth.tokens import (
    check_validity_and_payload,
    get_access_jwt,
    get_refresh_jwt,
)
from api.v1.crypto import cypher_password
from config.db import REFRESH_TOKEN_EXP
from db.pg import db
from db.redis import ref_tok
from models.sessions import Session
from models.user import UserCredentials
from schemas.user import login_schema
from services.blacklist import ACCESS_ROVEKED, LOG_OUT_ALL, UPD_PAYLOAD

module_auth_bp = Blueprint("login", __name__, url_prefix="")


@module_auth_bp.route("/login", methods=["POST"])
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
        # write login info to relation db
        agent = request.headers.get("User-Agent")
        session_start = Session(user_id=user.id, agent=agent)
        db.session.add(session_start)
        db.session.commit()
        refresh_token = get_access_jwt(str(user.id))
        access_token = get_refresh_jwt(str(user.id))
        # add this refresh token to redis
        ref_tok.setex(
            json.dumps(
                {
                    "user_id": str(user.id),
                    "agent": agent,
                }
            ),
            REFRESH_TOKEN_EXP,
            refresh_token,
        )
        LOG_OUT_ALL.process_update(user_id=user.id, agent=agent)
        UPD_PAYLOAD.process_update(user_id=user.id, agent=agent)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200
    else:
        return "wrong password", 403


@module_auth_bp.route("/check", methods=["POST"])
def check() -> (dict, list, int):
    access_token = request.headers.get("Authorization") or ""
    agent = request.headers.get("User-Agent")
    new_token = access_token

    is_valid, payload = check_validity_and_payload(access_token)
    user_id = payload["user_id"]

    if ACCESS_ROVEKED.check(access_token):
        return ("revoked", 403)

    if LOG_OUT_ALL.check(user_id=user_id, agent=agent):
        ACCESS_ROVEKED.add(access_token)
        return ("requested logout", 403)

    if UPD_PAYLOAD.check(user_id=user_id, agent=agent):
        ACCESS_ROVEKED.add(access_token)
        new_token = get_access_jwt(str(user_id))
        UPD_PAYLOAD.process_update(user_id=user_id, agent=agent)
    return {"new_access_token": new_token, "roles": []}, 204


@module_auth_bp.route("/logout", methods=["POST"])
def log_out():
    access_token = request.headers.get("Authorization") or ""
    _, code = check()
    if code == 204:
        ACCESS_ROVEKED.add(access_token)

        return ("", 204)
    else:
        return ("", 403)
