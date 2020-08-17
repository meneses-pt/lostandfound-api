from flask_jwt_extended import current_user
from slugify import slugify
from sqlalchemy.ext.declarative import declared_attr

from app import db
from utils import get_random_string


class BaseModel(db.Model):
    __abstract__ = True

    active = db.Column(db.Boolean, nullable=False, default=True)
    created_on = db.Column(db.DateTime,
                           default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    @declared_attr
    def created_by_id(self):
        return db.Column(db.Integer,
                         db.ForeignKey('user.id'),
                         nullable=True,
                         default=_current_user_id_or_none)

    @declared_attr
    def updated_by_id(self):
        return db.Column(db.Integer,
                         db.ForeignKey('user.id'),
                         nullable=True,
                         default=_current_user_id_or_none,
                         onupdate=_current_user_id_or_none)

    @declared_attr
    def created_by(self):
        return db.relationship('User',
                               foreign_keys=[self.created_by_id])

    @declared_attr
    def updated_by(self):
        return db.relationship('User',
                               foreign_keys=[self.updated_by_id])


def _current_user_id_or_none():
    logged_user = current_user
    return logged_user.id if logged_user else None


def slugify_field(field, max_length, model):
    max_field_length = max_length - 6
    slug = slugify(field[:max_field_length]) + '-' + get_random_string(5)
    while model.query.filter_by(slug=slug).exists():
        slug = slugify(field[:max_field_length]) + '-' + get_random_string(5)
    return slug
