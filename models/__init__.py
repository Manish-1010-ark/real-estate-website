from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from extensions import db, bcrypt

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

__all__ = ['db', 'jwt', 'bcrypt']
