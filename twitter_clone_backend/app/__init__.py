import os
import time
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
from app.config import config_by_name
from app.extensions import db, migrate, jwt, bcrypt, swagger, limiter
from app.errors import register_error_handlers
from app.auth.services import is_token_revoked


def create_app(config_name=None):
    """Application Factory for Flask REST API."""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)

    # Record application startup timestamp
    app.config['SERVER_START_TIME'] = time.time()

    # Load configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure upload and log directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], 'profile'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'posts', 'images'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'posts', 'videos'), exist_ok=True)
    os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Setup Logging
    setup_logging(app)

    # Initialize extensions
    init_extensions(app)

    # Register central error handlers
    register_error_handlers(app)

    # Register middleware handlers
    setup_middleware(app)

    # Register blueprints
    register_blueprints(app)

    app.logger.info(f"Server initialized under '{config_name}' environment.")

    return app


def setup_logging(app):
    """Configure rotating file application logger."""

    log_file = os.path.join('logs', 'application.log')
    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


def init_extensions(app):
    """Bind Flask extensions to the application instance."""

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    swagger.init_app(app)
    limiter.init_app(app)

    # Configure JWT Token Revocation / Blocklist Callback
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_header, jwt_payload)


def setup_middleware(app):
    """Register request execution timers, request ID tracking, and security headers."""

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        execution_time = time.time() - getattr(g, 'start_time', time.time())
        request_id = getattr(g, 'request_id', '')

        # Attach custom metadata headers
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time'] = f"{execution_time:.4f}s"

        # Attach Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Log request summary
        app.logger.info(
            f"[{request_id}] {request.remote_addr} - {request.method} {request.path} "
            f"{response.status_code} ({execution_time:.4f}s)"
        )

        return response


def register_blueprints(app):
    """Register application blueprints under API v1 versioning."""

    from app.health import health_bp
    from app.auth.routes import auth_bp
    from app.users.routes import users_bp
    from app.posts.routes import posts_bp
    from app.comments.routes import comments_bp
    from app.likes.routes import likes_bp
    from app.follows.routes import follows_bp
    from app.media.routes import media_bp
    from app.bookmarks.routes import bookmarks_bp
    from app.notifications.routes import notifications_bp
    from app.blocks.routes import blocks_bp
    from app.reports.routes import reports_bp
    from app.settings.routes import settings_bp
    from app.search.routes import search_bp
    from app.admin.routes import admin_bp
    from app.trending.routes import trending_bp
    from app.frontend.routes import frontend_bp

    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(posts_bp, url_prefix='/api/v1')
    app.register_blueprint(likes_bp, url_prefix='/api/v1')
    app.register_blueprint(comments_bp, url_prefix='/api/v1')
    app.register_blueprint(follows_bp, url_prefix='/api/v1')
    app.register_blueprint(media_bp, url_prefix='/api/v1/media')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/v1')
    app.register_blueprint(notifications_bp, url_prefix='/api/v1')
    app.register_blueprint(blocks_bp, url_prefix='/api/v1')
    app.register_blueprint(reports_bp, url_prefix='/api/v1')
    app.register_blueprint(settings_bp, url_prefix='/api/v1')
    app.register_blueprint(search_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1')
    app.register_blueprint(trending_bp, url_prefix='/api/v1')
    app.register_blueprint(frontend_bp)
