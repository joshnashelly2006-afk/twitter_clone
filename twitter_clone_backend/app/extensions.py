"""
Flask Extensions Initialization Module.

Instantiates extensions to be bound to the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
swagger = Swagger()
limiter = Limiter(key_func=get_remote_address)
