import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base Configuration Class."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(BASE_DIR, '..', 'uploads'))
    IMAGE_UPLOAD_FOLDER = os.getenv('IMAGE_UPLOAD_FOLDER', os.path.join(BASE_DIR, '..', 'uploads', 'images'))
    VIDEO_UPLOAD_FOLDER = os.getenv('VIDEO_UPLOAD_FOLDER', os.path.join(BASE_DIR, '..', 'uploads', 'videos'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50 MB

    # Flasgger / Swagger UI Config
    SWAGGER = {
        'title': 'Twitter Clone Backend REST API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'Production-ready REST API for Twitter/X clone backend built with Flask & PostgreSQL',
        'specs_route': '/apidocs/'
    }


class DevelopmentConfig(Config):
    """Development Environment Configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/twitter_clone_db'
    )


class TestingConfig(Config):
    """Testing Environment Configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production Environment Configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
