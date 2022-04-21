from sqlalchemy.exc import IntegrityError

from app import app
from db.pg import db
from models.user import User

# create sql alchemy
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
