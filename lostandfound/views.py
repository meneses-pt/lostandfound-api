from flask import Blueprint, jsonify

from lostandfound.models import Category
from lostandfound.schemas import categories_schema

lostandfound_app = Blueprint('lostandfound_app', __name__)


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
