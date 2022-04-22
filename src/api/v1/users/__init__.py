from flask import Blueprint

from api.v1.users.create import create_bp

users_bp = Blueprint("users", __name__, url_prefix="/users")
users_bp.register_blueprint(create_bp)
