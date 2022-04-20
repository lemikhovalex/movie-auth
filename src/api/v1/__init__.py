from flask import Blueprint

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")


@v1_bp.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"
