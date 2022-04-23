from flask import Flask
from flask_marshmallow import Marshmallow

from db.pg import init_db

app = Flask(__name__)
ma = Marshmallow(app)
init_db(app)

from api import (  # noqa E402; TODO create app and then import blueprint, relid on app
    api_bp,
)

app.register_blueprint(api_bp)
