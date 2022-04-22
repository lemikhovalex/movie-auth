import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from db.pg import db


class Session(db.Model):
    __tablename__ = "sessions"

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
    agent = db.Column(
        db.String,
        unique=False,
        nullable=False,
    )

    auth_time = db.Column(
        db.DateTime, unique=False, nullable=False, default=datetime.now
    )

    def __repr__(self):
        return f"<User {self.login} came at {self.auth_time} from {self.agent}>"
