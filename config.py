import os
from datetime import timedelta

class Config:
    # Flask secret key
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key')

    # Database (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://realestate_user:StrongPassword123@localhost:5432/realestate_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_USER_CLAIMS = 'user'
    JWT_JSON_KEY = 'identity'


    # Cookie/session security (if you ever use sessions)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # or 'None' if on different subdomains

    # File upload limit
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
