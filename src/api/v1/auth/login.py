import json

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from api.v1.auth.tokens import get_access_jwt, get_refresh_jwt
from api.v1.crypto import cypher_password
from config.db import REFRESH_TOKEN_EXP
from db.pg import db
from db.redis import ref_tok
from models.sessions import Session
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
        # write login info to relation db
        agent = "agent"
        session_start = Session(user_id=user.id, agent=agent)
        db.session.add(session_start)
        db.session.commit()
        refresh_token = get_access_jwt("b")
        access_token = get_refresh_jwt("a")
        # add this refresh token to redis
        ref_tok.setex(
            json.dumps(
                {
                    "user_id": str(user.id),
                    "agent": agent,
                    "refresh_token": refresh_token,
                }
            ),
            REFRESH_TOKEN_EXP,
            "",
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200
    else:
        return "wrong password", 403
