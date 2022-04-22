from flask import Blueprint

from api.v1.auth import auth_bp
from api.v1.users import users_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")

v1_bp.register_blueprint(users_bp)
v1_bp.register_blueprint(auth_bp)


@v1_bp.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"
