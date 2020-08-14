from slugify import slugify

from app import db
from utils import get_random_string
from utils.models import BaseModel


class Category(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    parent_category = db.relationship('Category', backref=db.backref('child_categories', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        slug = slugify(kwargs.get('name', '')) + '-' + get_random_string(5)
        while Category.query.filter_by(slug=slug).exists():
            slug = slugify(kwargs.get('name', '')) + '-' + get_random_string(5)
        kwargs['slug'] = slug
        super().__init__(*args, **kwargs)
