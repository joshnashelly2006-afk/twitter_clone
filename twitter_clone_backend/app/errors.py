from flask import jsonify
from flask_limiter.errors import RateLimitExceeded


class APIError(Exception):
    """Base API Exception."""

    def __init__(self, message, status_code=400, errors=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}

    def to_dict(self):
        return {
            'success': False,
            'message': self.message,
            'errors': self.errors
        }


class ValidationError(APIError):
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400, errors=errors)


class UnauthorizedError(APIError):
    def __init__(self, message='Unauthorized access', errors=None):
        super().__init__(message, status_code=401, errors=errors)


class ForbiddenError(APIError):
    def __init__(self, message='Forbidden action', errors=None):
        super().__init__(message, status_code=403, errors=errors)


class NotFoundError(APIError):
    def __init__(self, message='Resource not found', errors=None):
        super().__init__(message, status_code=404, errors=errors)


class ConflictError(APIError):
    def __init__(self, message='Resource already exists', errors=None):
        super().__init__(message, status_code=409, errors=errors)


class PayloadTooLargeError(APIError):
    def __init__(self, message='File size exceeds maximum allowed limit', errors=None):
        super().__init__(message, status_code=413, errors=errors)


class UnsupportedMediaTypeError(APIError):
    def __init__(self, message='Unsupported file format', errors=None):
        super().__init__(message, status_code=415, errors=errors)


def register_error_handlers(app):
    """Register application custom exception and HTTP error handlers."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded. Too many requests.',
            'errors': {
                'limit': str(error.description)
            }
        }), 429

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Bad request',
            'errors': {}
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Unauthorized',
            'errors': {}
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Forbidden',
            'errors': {}
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Resource not found',
            'errors': {}
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed for this endpoint',
            'errors': {}
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Resource conflict',
            'errors': {}
        }), 409

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            'success': False,
            'message': 'File size exceeds maximum allowed limit',
            'errors': {}
        }), 413

    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({
            'success': False,
            'message': 'Unsupported file format',
            'errors': {}
        }), 415

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'message': 'Unprocessable entity payload',
            'errors': {}
        }), 422

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'success': False,
            'message': 'Too many requests',
            'errors': {}
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal Server Error: {error}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected server error occurred',
            'errors': {}
        }), 500
