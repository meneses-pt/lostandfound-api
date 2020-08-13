from flask import Blueprint, jsonify, current_app
from flask_swagger import swagger

doc_app = Blueprint('doc_app', __name__, url_prefix='/doc')


@doc_app.route("/spec")
def spec():
    swag = swagger(current_app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "LostAndFound"
    return jsonify(swag)
