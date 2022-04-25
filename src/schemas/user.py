from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested

from models.user import UserCredentials, UserData


class UserCredentialsSch(SQLAlchemyAutoSchema):
    class Meta:
        model = UserCredentials
        include_relationships = True

    id = auto_field()
    login = auto_field()
    password = auto_field()


class UserDataSch(SQLAlchemyAutoSchema):
    class Meta:
        model = UserData
        include_relationships = True

    user_id = auto_field()
    first_name = auto_field()
    second_name = auto_field()


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
login_schema = UserCredentialsSch(exclude=("id",))
user_data_schema = UserDataSch(exclude=("user_id",))
