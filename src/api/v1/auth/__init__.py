from flask import Blueprint

from api.v1.auth.login import login_bp

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_bp.register_blueprint(login_bp)
