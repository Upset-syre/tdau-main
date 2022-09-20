import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
THREADS_PER_PAGE = 2
CSRF_ENABLED     = True
CSRF_SESSION_KEY = "secret"

# SQLALCHEMY_DATABASE_URI = "postgresql://postgres:o030101@127.0.0.1:5434/tdau"
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


SECRET_KEY = "secret"
FLASK_ADMIN_SWATCH = "yeti"
FLASK_ADMIN_FLUID_LAYOUT = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAX_LOGIN_ATTEMPTS = 5