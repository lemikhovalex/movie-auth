import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.pg import db


class UserCredentials(db.Model):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User {self.login}>"


class UserData(db.Model):
    __tablename__ = "user_data"
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = db.Column(db.String, nullable=True)
    second_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<User data {self.first_name}, {self.second_name}>"
