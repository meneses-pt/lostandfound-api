import os

SECRET_KEY = os.environ['SECRET_KEY']

DB_FILE = os.environ['DB_FILE']
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'lostandfound.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_BLACKLIST_ENABLED = os.environ['JWT_BLACKLIST_ENABLED']

LOSTANDFOUND_IMAGES_FILE_PATH = os.path.join(basedir, os.environ['LOSTANDFOUND_IMAGES_STATIC_PATH'])
LOSTANDFOUND_IMAGES_STATIC_PATH = os.environ['LOSTANDFOUND_IMAGES_STATIC_PATH']
