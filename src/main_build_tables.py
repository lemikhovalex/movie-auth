from api.v1.crypto import cypher_password
from app import app
from db.pg import db
from models.roles import UsersRoles
from models.sessions import Session
from models.user import UserCredentials, UserData

# create sql alchemy
app.app_context().push()
db.create_all()
db.session.commit()

# create admin
admin = UserCredentials(login="admin", password=cypher_password("password"))
db.session.add(admin)


# give him admin rights

UserCredentials.query.all()
admin = UserCredentials.query.filter_by(login="admin").first()
admin_u_id = admin.id

# set some admin data
u_data = UserData(user_id=admin_u_id, first_name="A", second_name="Dmin")
db.session.add(u_data)

# give him role
role = UsersRoles(
    user_id=admin_u_id,
    role_id=0,
)
db.session.add(role)

# and add session
ses = Session(user_id=admin_u_id, agent="device")
db.session.add(ses)
db.session.commit()
