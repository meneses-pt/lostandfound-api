from enum import Enum

from app import db
from utils.models import BaseModel, slugify_field


class Reason(Enum):
    looking_for = 'Looking For'
    found = 'Found'


class LookingForReason(Enum):
    lost = 'Lost'
    stolen = 'Stolen'
    other = 'Other'


class Category(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(56), nullable=False, unique=True)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    parent_category = db.relationship('Category', backref=db.backref('child_categories', lazy='dynamic'),
                                      remote_side=id)

    def __init__(self, *args, **kwargs):
        slug = slugify_field(kwargs.get('name', ''), 56, Category)
        kwargs['slug'] = slug
        super().__init__(*args, **kwargs)


class Item(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(56), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    reason = db.Column(db.Enum(Reason), nullable=False, index=True)
    looking_for_reason = db.Column(db.Enum(LookingForReason), nullable=True)

    category = db.relationship('Category', backref=db.backref('items', lazy='dynamic'))

    __table_args__ = (db.CheckConstraint('NOT(reason = \'Looking For\' and looking_for_reason IS NULL)',
                                         name='ck_item_looking_for_reason'),)

    def __init__(self, *args, **kwargs):
        slug = slugify_field(kwargs.get('name', ''), 56, Item)
        kwargs['slug'] = slug
        super().__init__(*args, **kwargs)


class ItemImage(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(36))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    item = db.relationship('Item', backref=db.backref('images', lazy='dynamic'))
