from sqlalchemy.exc import IntegrityError

from app import app
from db.pg import db
from models.roles import UsersRoles
from models.sessions import Session
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

# give him admin rights

User.query.all()
admin = User.query.filter_by(login="admin").first()
admin_u_id = admin.id

try:
    role = UsersRoles(
        user_id=admin_u_id,
        role_id=0,
    )
    db.session.add(role)
    db.session.commit()
except IntegrityError:
    pass

ses = Session(user_id=admin_u_id, agent="device")
db.session.add(ses)
db.session.commit()
