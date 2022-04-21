from flask import Flask
from flask_marshmallow import Marshmallow

from api import api_bp
from db.pg import init_db

app = Flask(__name__)
app.register_blueprint(api_bp)
init_db(app)

ma = Marshmallow(app)
