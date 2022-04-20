from app import ma


class UserSchema(ma.Schema):
    class Meta:
        fields = ("login", "password")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
