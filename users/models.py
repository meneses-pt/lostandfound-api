from enum import Enum

from app import db
from utils.models import BaseModel


class Role(Enum):
    admin = 'admin'
    regular = 'regular'


class User(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(94), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
