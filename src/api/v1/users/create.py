import uuid

from flask import Blueprint, request

from db.pg import db
from models.user import UserCredentials, UserData

create_bp = Blueprint("create", __name__, url_prefix="")


@create_bp.route("", methods=["POST"])
def create():
    print("\n\n post \n route", flush=True)

    new_user_id = uuid.uuid4()
    u_creds = UserCredentials(id=new_user_id, **request.json["credentials"])

    u_data = UserData(user_id=new_user_id, **request.json["user_data"])

    db.session.add(u_creds)
    db.session.add(u_data)

    db.session.commit()
    return "ok"


@create_bp.route("", methods=["GET"])
def get():
    print("\n\nin route\n\n", flush=True)
    return "get user"
