from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt, get_jwt_identity, create_refresh_token, \
    jwt_refresh_token_required, decode_token
from werkzeug.security import check_password_hash

from app import blacklist, users_tokens, jwt
from users.models import User
from users.schemas import user_schema

auth_app = Blueprint('auth_app', __name__, url_prefix='/auth')


@auth_app.route('/login', methods=['POST'])
def login():
    """
    Performs a user login
    ---
    tags:
        - Auth
    parameters:
        - in: body
          name: User
    responses:
        200:
            description: Login succeeded
    """
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        if email in users_tokens:
            users_tokens[email].extend([{
                "access_token": decode_token(access_token)['jti'],
                "refresh_token": decode_token(refresh_token)['jti']
            }])
        else:
            users_tokens.update({email: [{
                "access_token": decode_token(access_token)['jti'],
                "refresh_token": decode_token(refresh_token)['jti']
            }]})
        user_result = user_schema.dump(user)
        return jsonify(message="Login succeeded",
                       access_token=access_token,
                       refresh_token=refresh_token,
                       user=user_result)
    else:
        return jsonify(message="Invalid email/password combination"), 401


@auth_app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Gets a refreshed access token
    ---
    tags:
        - Auth
    responses:
        200:
            description: Access token refreshed
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)


@auth_app.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    Logs out a user
    ---
    tags:
        - Auth
    responses:
        200:
            description: User logged out
    """
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    current_user = get_jwt_identity()
    if current_user in users_tokens:
        access_token_kv_list = [kv for kv in users_tokens[current_user] if kv['access_token'] == jti]
        access_token_kv = next(iter(access_token_kv_list), None)
        refresh_token = access_token_kv['refresh_token']
        users_tokens[current_user].remove(access_token_kv)
        blacklist.add(refresh_token)
    return jsonify(message='Successfully logged out'), 200
