from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, current_user

from app import jwt, blacklist
from users.models import User, Role


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    logged_user = User.query.filter_by(email=identity).first()
    return logged_user


def role_required(roles):
    def role_required_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            logged_user = current_user
            has_permission = False
            if isinstance(roles, Role):
                if logged_user.role == roles:
                    has_permission = True
            elif isinstance(roles, list):
                if logged_user.role in roles:
                    has_permission = True
            if not has_permission:
                return jsonify(msg='User has no permission for action'), 403
            else:
                return fn(*args, **kwargs)

        return wrapper

    return role_required_decorator


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist
