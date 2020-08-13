from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, blacklist, users_tokens
from auth.utils import role_required
from users.models import User, Role
from users.schemas import users_schema, user_schema

users_app = Blueprint('users_app', __name__, url_prefix='/users')


@users_app.route('/data', methods=['GET'])
@role_required(Role.admin)
def get_data():
    """
    Returns the count of active users
    ---
    tags:
        - Users
    responses:
        200:
            description: Returns a list of restaurants
    """
    users = User.query.filter_by(active=True).count()
    return jsonify(users=users)


@users_app.route('', methods=['GET'])
@role_required(Role.admin)
def list_users():
    """
    Gets a list of users
    ---
    tags:
        - Users
    responses:
        200:
            description: Returns a list of users
    """
    page = int(request.args.get('page', 1))
    users_list = User.query.filter_by(active=True).order_by(User.name).paginate(page=page, per_page=10, error_out=False)
    result = users_schema.dump(users_list.items)
    return jsonify(result)


@users_app.route('/<int:user_id>', methods=['GET'])
@role_required(Role.admin)
def get_user(user_id):
    """
    Gets a user
    ---
    tags:
        - Users
    parameters:
        - in: parameter
          name: user_id
    responses:
        200:
            description: Returns an user instance
    """
    user = User.query.filter_by(id=user_id, active=True).first()
    if user:
        result = user_schema.dump(user)
        return jsonify(result)
    else:
        return jsonify(message="User does not exist"), 404


@users_app.route('/<int:user_id>', methods=['PUT'])
@role_required(Role.admin)
def edit_user(user_id):
    """
    Edits user information
    ---
    tags:
        - Users
    parameters:
        - in: parameter
          name: user_id
        - in: body
          name: User
    responses:
        200:
            description: User edited
    """
    user = User.query.filter_by(id=user_id, active=True).first()
    if user:
        # Only allow to change name and e-mail
        user.name = request.json.get('name')
        old_email = user.email
        user.email = request.json.get('email')
        password = request.json.get('password')
        if password and len(password) > 0:
            user.password = generate_password_hash(password)
            access_tokens = [kv['access_token'] for kv in users_tokens[old_email]]
            refresh_tokens = [kv['refresh_token'] for kv in users_tokens[old_email]]
            blacklist.update(access_tokens)
            blacklist.update(refresh_tokens)
            users_tokens[old_email] = []
        db.session.commit()
        result = user_schema.dump(user)
        return jsonify(result)
    else:
        return jsonify(message="User does not exist"), 404


@users_app.route('/<int:user_id>/change-password', methods=['PUT'])
@jwt_required
def change_password(user_id):
    """
    Changes user password
    ---
    tags:
        - Users
    parameters:
        - in: parameter
          name: user_id
        - in: body
          name: User
    responses:
        200:
            description: Password changed
    """
    logged_user = current_user
    logged_email = logged_user.email
    user = User.query.filter_by(id=user_id, active=True).first()
    if user:
        if user_id != logged_user.id:
            return jsonify(message="You can only change your own password"), 403
        password = request.json['password']
        new_password = request.json['new_password']
        if not check_password_hash(user.password, password):
            return jsonify(message="The current password is not correct"), 403
        user.password = generate_password_hash(new_password)
        db.session.commit()
        result = user_schema.dump(user)
        if logged_email in users_tokens:
            access_tokens = [kv['access_token'] for kv in users_tokens[logged_email]]
            refresh_tokens = [kv['refresh_token'] for kv in users_tokens[logged_email]]
            blacklist.update(access_tokens)
            blacklist.update(refresh_tokens)
            users_tokens[logged_email] = []
        return jsonify(result)
    else:
        return jsonify(message="User does not exist"), 404


@users_app.route('', methods=['POST'])
@jwt_optional
def register():
    """
    Registers a new user
    ---
    tags:
        - Users
    parameters:
        - in: body
          name: User
    responses:
        201:
            description: User created
    """
    email = request.json['email']
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify(message='That email already exists.'), 409
    else:
        name = request.json['name']
        password = request.json['password']
        role = request.json['role']
        if role not in set(item.value for item in Role):
            return jsonify(message='The role provided does not exist'), 422
        role_obj = Role(role)
        if role_obj == Role.admin:
            logged_user = current_user
            if not logged_user or logged_user.role != Role.admin:
                return jsonify(message='Only admin users can create other admin users'), 403
        user = User(name=name, email=email, password=generate_password_hash(password), role=role_obj)
        db.session.add(user)
        db.session.commit()
        result = user_schema.dump(user)
        return jsonify(result), 201


@users_app.route('/<int:user_id>', methods=['DELETE'])
@role_required(Role.admin)
def delete_user(user_id):
    """
    Deletes a user
    ---
    tags:
        - Users
    parameters:
        - in: parameter
          name: user_id
    responses:
        200:
            description: User deleted
    """
    user = User.query.filter_by(id=user_id, active=True).first()
    logged_email = get_jwt_identity()
    if user:
        if user.email == logged_email:
            return jsonify(message="User can't delete himself"), 403
        user.active = False
        db.session.commit()
        return jsonify(message="User deleted")
    else:
        return jsonify(message="User does not exist"), 404
