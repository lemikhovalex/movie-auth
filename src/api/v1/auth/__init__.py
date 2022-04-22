from flask import Blueprint

from api.v1.auth.auth import module_auth_bp

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_bp.register_blueprint(module_auth_bp)
