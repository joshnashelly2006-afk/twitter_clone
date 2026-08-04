from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token
)
from app.extensions import limiter
from app.auth.validators import validate_registration_input, validate_login_input
from app.auth.services import (
    register_user,
    authenticate_user,
    get_current_user_profile,
    revoke_token
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """
    User Registration Endpoint
    ---
    tags:
      - Authentication
    summary: Register a new user account
    description: Creates a new user with username, email, password, and password confirmation.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
            - confirm_password
          properties:
            username:
              type: string
              example: john_doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecretPass123
            confirm_password:
              type: string
              example: SecretPass123
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Conflict error
      429:
        description: Rate limit exceeded (3 requests per minute)
    """
    data = request.get_json()
    validated_data = validate_registration_input(data)
    user_data = register_user(validated_data)

    return jsonify({
        'success': True,
        'message': 'User registered successfully.',
        'data': user_data
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    User Login Endpoint
    ---
    tags:
      - Authentication
    summary: Authenticate user and receive JWT tokens
    description: Authenticates user credentials via email and password, returning JWT access and refresh tokens.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: SecretPass123
    responses:
      200:
        description: Authentication successful
      401:
        description: Invalid credentials
      429:
        description: Rate limit exceeded (5 requests per minute)
    """
    data = request.get_json()
    validated_data = validate_login_input(data)
    auth_data = authenticate_user(validated_data)

    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'data': auth_data
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get Current Logged-in User Endpoint
    ---
    tags:
      - Authentication
    summary: Retrieve profile of authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    profile = get_current_user_profile(current_user_id)

    return jsonify({
        'success': True,
        'message': 'Profile retrieved successfully.',
        'data': profile
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    User Logout Endpoint
    ---
    tags:
      - Authentication
    summary: Logout user and invalidate JWT token
    security:
      - Bearer: []
    responses:
      200:
        description: Token revoked successfully
      401:
        description: Token missing or invalid
    """
    jti = get_jwt()['jti']
    revoke_token(jti)

    return jsonify({
        'success': True,
        'message': 'Successfully logged out.',
        'data': {}
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh Access Token Endpoint
    ---
    tags:
      - Authentication
    summary: Obtain a new access token using refresh token
    security:
      - Bearer: []
    responses:
      200:
        description: New access token issued successfully
      401:
        description: Refresh token invalid or expired
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'success': True,
        'message': 'Access token refreshed successfully.',
        'data': {
            'access_token': new_access_token
        }
    }), 200
