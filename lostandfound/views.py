from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from auth.utils import role_required
from lostandfound.models import Category
from lostandfound.schemas import categories_schema, category_schema
from users.models import Role

lostandfound_app = Blueprint('lostandfound_app', __name__)


@lostandfound_app.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Gets a category
    ---
    tags:
        - Categorues
    parameters:
        - in: parameter
          name: category_id
    responses:
        200:
            description: Returns a category instance
    """
    restaurant = Category.query.filter_by(id=category_id, active=True).first()
    if restaurant:
        result = category_schema.dump(restaurant)
        return jsonify(category=result)
    else:
        return jsonify(message="Category does not exist"), 404


@lostandfound_app.route('/categories', methods=['GET'])
def list_categories():
    """
    Gets a list of categories
    ---
    tags:
        - Categories
    responses:
        200:
            description: Returns a list of categories
    """
    reviews_list = Category.query.filter_by(active=True)
    result = categories_schema.dump(reviews_list)
    return jsonify(result)


@lostandfound_app.route('/categories/<category_id>', methods=['PUT'])
@role_required(Role.admin)
def edit_category(category_id):
    """
    Edits a category information
    ---
    tags:
        - Categories
    parameters:
        - in: parameter
          name: category_id
        - in: body
          name: Category
    responses:
        200:
            description: Category edited
    """
    category = Category.query.filter_by(id=category_id, active=True).first()
    if category:
        name = request.json['name']
        parent_category_id = request.json.get('parent_category_id')
        category.name = name
        category.category_id = parent_category_id
        db.session.commit()
        result = category_schema.dump(category)
        return jsonify(result)
    else:
        return jsonify(message="Category does not exist"), 404


@lostandfound_app.route('/categories', methods=['POST'])
@role_required(Role.admin)
def create_category():
    """
    Creates a new category
    ---
    tags:
        - Categories
    parameters:
        - in: body
          name: Category
    responses:
        201:
            description: Category created
    """
    name = request.json['name']
    parent_category_id = request.json.get('parent_category_id')
    category = Category(name=name, parent_category_id=parent_category_id)
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="There already exists a category with that name!"), 409
    result = category_schema.dump(category)
    return jsonify(result), 201


@lostandfound_app.route('/categories/<category_id>', methods=['DELETE'])
@role_required(Role.admin)
def delete_category(category_id):
    """
    Deletes a category
    ---
    tags:
        - Categories
    parameters:
        - in: parameter
          name: category_id
    responses:
        200:
            description: Category deleted
    """
    category = Category.query.filter_by(id=category_id, active=True).first()
    if category:
        category.active = False
        db.session.commit()
        return jsonify(message="Category deleted")
    else:
        return jsonify(message="Category does not exist"), 404
