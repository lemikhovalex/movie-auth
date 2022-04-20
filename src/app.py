from flask import Flask
from flask_marshmallow import Marshmallow

from api import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

ma = Marshmallow(app)
