from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Single extension instances used across the app
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
