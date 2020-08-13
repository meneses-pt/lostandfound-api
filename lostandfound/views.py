import base64
import os
import uuid
from pathlib import Path

import dateutil
from dateutil.parser import parser
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, and_, func
from sqlalchemy.exc import IntegrityError

from app import db
from auth.utils import role_required
from settings import LOSTANDFOUND_IMAGES_FILE_PATH
from users.models import Role, User

lostandfound_app = Blueprint('lostandfound_app', __name__)
