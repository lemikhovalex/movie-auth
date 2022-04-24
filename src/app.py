from flask import Flask
from flask_marshmallow import Marshmallow

from db.pg import db, init_db

app = Flask(__name__)
app.url_map.strict_slashes = False
ma = Marshmallow(app)
init_db(app)

from api import (  # noqa E402; TODO create app and then import blueprint, relid on app
    api_bp,
)

app.app_context().push()
db.create_all()
db.session.commit()

app.register_blueprint(api_bp)
