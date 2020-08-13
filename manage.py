from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from app import create_app, auth_cli, db
from users.models import User, Role

app = create_app()


@auth_cli.command("db_seed")
@with_appcontext
def db_seed():
    user = User(email='andre@meneses.pt',
                name='André Meneses',
                password=generate_password_hash('devpassword'),
                role=Role.admin)
    db.session.add(user)
    db.session.commit()
    print('Admin user seeded!')
