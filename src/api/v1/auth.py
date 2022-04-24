import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from config.db import REFRESH_TOKEN_EXP
from db.pg import db
from db.redis import ref_tok, revoked_access
from models.sessions import Session
from models.user import UserCredentials
from schemas.user import login_schema
from services.blacklist import ACCESS_REVOKED, LOG_OUT_ALL, UPD_PAYLOAD
from utils.crypto import check_password
from utils.tokens import check_validity_and_payload, get_access_and_refresh_jwt

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["POST"])
def login():
    request_data = request.json
    try:
        # Validate request body against schema data types
        login_data = login_schema.load(request_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    creds_from_storage = UserCredentials.query.filter_by(
        login=login_data["login"]
    ).first()

    if check_password(
        password=login_data["password"], password_encoded=creds_from_storage.password
    ):
        # write login info to relation db
        agent = request.headers.get("User-Agent")
        session_start = Session(user_id=creds_from_storage.id, agent=agent)
        db.session.add(session_start)
        db.session.commit()
        access_token, refresh_token = get_access_and_refresh_jwt(
            user_id=creds_from_storage.id
        )
        # add this refresh token to redis
        ref_tok.setex(
            json.dumps(
                {
                    "user_id": str(creds_from_storage.id),
                    "agent": agent,
                }
            ),
            REFRESH_TOKEN_EXP,
            refresh_token,
        )
        LOG_OUT_ALL.process_update(user_id=creds_from_storage.id, agent=agent)
        UPD_PAYLOAD.process_update(user_id=creds_from_storage.id, agent=agent)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200
    else:
        return "wrong password", 403


@bp.route("/check", methods=["POST"])
def check() -> (dict, list, int):
    access_token = request.headers.get("Authorization") or ""
    agent = request.headers.get("User-Agent")
    new_token = None

    is_valid, payload = check_validity_and_payload(access_token)
    if not is_valid:
        return "go log in", 403
    user_id = payload["user_id"]
    print(revoked_access.get(access_token))
    if not ACCESS_REVOKED.is_ok(access_token):
        return ("revoked", 403)

    if not LOG_OUT_ALL.is_ok(user_id=user_id, agent=agent):
        ACCESS_REVOKED.add(access_token)
        return ("requested logout", 403)

    if not UPD_PAYLOAD.is_ok(user_id=user_id, agent=agent):
        ACCESS_REVOKED.add(access_token)
        new_token, _ = get_access_and_refresh_jwt(user_id)
        UPD_PAYLOAD.process_update(user_id=user_id, agent=agent)
    return jsonify({"new_access_token": new_token, "roles": payload["roles"]}), 200


@bp.route("/logout", methods=["POST"])
def log_out():
    access_token = request.headers.get("Authorization") or ""
    _, code = check()
    if code == 200:
        ACCESS_REVOKED.add(access_token)

        return ("", 200)
    else:
        return ("", 403)
