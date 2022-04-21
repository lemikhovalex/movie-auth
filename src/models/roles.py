import uuid

from sqlalchemy.dialects.postgresql import UUID

from db.pg import db


class UsersRoles(db.Model):
    __tablename__ = "users_roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        default=uuid.uuid4,
        unique=False,
        nullable=False,
    )
    role_id = db.Column(
        db.Integer,
        default=int,
        unique=False,
        nullable=False,
    )

    def __repr__(self):
        return f"<User {self.login}>"
