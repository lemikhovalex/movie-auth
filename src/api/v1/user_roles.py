import uuid

from flask import Blueprint, jsonify

from models.roles import UsersRoles

bp = Blueprint("user_roles", __name__, url_prefix="/users")


@bp.route("/<user_id>/roles", methods=["GET"])
def get_roles(user_id: str) -> (str, int):
    user_id = uuid.UUID(user_id)
    roles = UsersRoles.query.filter_by(user_id=user_id).all()
    if len(roles) > 0:
        return jsonify([r.role_id for r in roles]), 200
    else:
        return "", 404
