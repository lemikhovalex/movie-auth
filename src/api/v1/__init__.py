from flask import Blueprint

from api.v1.auth import bp as auth_bp
from api.v1.users import bp as users_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")

v1_bp.register_blueprint(users_bp)
v1_bp.register_blueprint(auth_bp)
