from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from users.models import User, Role


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("password",)

    role = EnumField(Role)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
