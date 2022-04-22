from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from app import ma
from models.user import UserCredentials, UserData


class UserCredentialsSch(SQLAlchemyAutoSchema):
    class Meta:
        model = UserCredentials
        include_relationships = True

    id = ma.auto_field()
    login = ma.auto_field()
    password = ma.auto_field()


class UserDataSch(SQLAlchemyAutoSchema):
    class Meta:
        model = UserData
        include_relationships = True

    user_id = ma.auto_field()
    first_name = ma.auto_field()
    second_name = ma.auto_field()


class RegisterSchema(SQLAlchemyAutoSchema):
    credentials = Nested(
        UserCredentialsSch(
            exclude=("id",),
        ),
    )
    user_data = Nested(
        UserDataSch(
            exclude=("user_id",),
        ),
    )


register_schema = RegisterSchema()
