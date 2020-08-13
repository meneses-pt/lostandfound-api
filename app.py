from flask import Flask
from flask.cli import AppGroup
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import MetaData

from utils.handlers import register_handlers

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
auth_cli = AppGroup('auth')

jwt = JWTManager()
blacklist = set()
users_tokens = {}


def create_app(**config_overrides):
    app = Flask(__name__)
    CORS(app)
    app.cli.add_command(auth_cli)

    jwt.init_app(app)

    # Load config
    app.config.from_pyfile('settings.py')

    # apply overrides for tests
    app.config.update(config_overrides)

    db.init_app(app)
    Migrate(app, db, render_as_batch=True)

    from auth.views import auth_app
    from users.views import users_app
    from lostandfound.views import lostandfound_app
    from doc.views import doc_app

    app.register_blueprint(auth_app)
    app.register_blueprint(users_app)
    app.register_blueprint(lostandfound_app)
    app.register_blueprint(doc_app)

    swaggerui_blueprint = get_swaggerui_blueprint(
        '/doc',
        '/doc/spec',
        config={'app_name': 'LostAndFound'},
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix='/doc')

    register_handlers(app)

    return app
