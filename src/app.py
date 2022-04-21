from flask import Flask
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError

from api import api_bp
from db.pg import db, init_db
from models.user import User

app = Flask(__name__)
app.register_blueprint(api_bp)

# create sql alchemy
init_db(app)
app.app_context().push()
db.create_all()
db.session.commit()

# create admin
try:
    admin = User(login="admin", password="password")
    db.session.add(admin)
    db.session.commit()
except IntegrityError:
    pass

ma = Marshmallow(app)
