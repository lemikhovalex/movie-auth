import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from api.v1.user_roles import get_roles
from config.db import REFRESH_TOKEN_EXP
from db.pg import db
from db.redis import ref_tok
from models.sessions import Session
from models.user import UserCredentials
from schemas.user import login_schema
from services.blacklist import (
    ACCESS_REVOKED,
    LOG_OUT_ALL,
    UPD_PAYLOAD,
    AccessForBlackList,
)
from utils.crypto import check_password, cypher_password
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
    if creds_from_storage is None:
        return "invalid login", 404

    if check_password(
        password=login_data["password"], password_encoded=creds_from_storage.password
    ):
        # write login info to relation db
        agent = request.headers.get("User-Agent")
        session_start = Session(user_id=creds_from_storage.id, agent=agent)
        db.session.add(session_start)
        db.session.commit()
        access_token, refresh_token = get_access_and_refresh_jwt(
            user_id=creds_from_storage.id,
            roles_getter=get_roles,
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

    is_valid, payload = check_validity_and_payload(access_token)
    black_list_info = AccessForBlackList.from_dict(**payload)
    if not is_valid:
        return "go log in", 403
    user_id = payload["user_id"]
    if not ACCESS_REVOKED.is_ok(access_token):
        print("revoked")
        return ("revoked", 403)

    if not LOG_OUT_ALL.is_ok(payload=black_list_info):
        ACCESS_REVOKED.add(token=access_token)
        return ("requested logout", 403)

    if not UPD_PAYLOAD.is_ok(payload=black_list_info):
        UPD_PAYLOAD.process_update(user_id=user_id, agent=agent)
        return ("requested payload upd", 403)

    return json.dumps({"payload": payload}), 200


@bp.route("/logout", methods=["POST"])
def log_out():
    access_token = request.headers.get("Authorization") or ""
    _, code = check()
    if code == 200:
        ACCESS_REVOKED.add(access_token)

        return ("", 200)
    else:
        return ("", 403)


@bp.route("/logout_all", methods=["POST"])
def logout_all():
    access_token = request.headers.get("Authorization") or ""
    _, code = check()
    if code == 200:
        _, payload = check_validity_and_payload(access_token)
        black_list_info = AccessForBlackList.from_dict(**payload)
        LOG_OUT_ALL.add(payload=black_list_info)

        return ("", 200)
    else:
        return ("", 403)


@bp.route("/change-password", methods=["POST"])
def change_password():
    new_password = request.json["password"]

    check_response, status = check()
    if status != 200:
        return check_response, status

    payload = json.loads(check_response)["payload"]

    q = UserCredentials.query.filter_by(id=payload["user_id"])
    creds_from_storage = q.first()
    if creds_from_storage is None:
        return "invalid login", 404
    else:
        q.update({"password": cypher_password(new_password)})
        db.session.commit()
        logout_all()
        return "", 200


@bp.route("/change-login", methods=["POST"])
def change_login():
    new_login = request.json["login"]

    check_response, status = check()
    if status != 200:
        return check_response, status

    payload = json.loads(check_response)["payload"]

    q = UserCredentials.query.filter_by(id=payload["user_id"])
    creds_from_storage = q.first()
    if creds_from_storage is None:
        return "invalid login", 404
    else:
        q.update({"login": new_login})
        db.session.commit()
        # logout_all()
        return "", 200
