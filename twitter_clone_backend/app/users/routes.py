from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import limiter
from app.users.validators import (
    validate_profile_update_input,
    validate_profile_picture_upload
)
from app.users.services import (
    get_user_profile,
    update_user_profile,
    get_public_user_profile,
    search_users,
    upload_profile_picture,
    delete_profile_picture,
    get_public_user_profile_by_username
)

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """
    Get Logged-in User Profile Endpoint
    ---
    tags:
      - User Profile
    summary: Retrieve profile of logged-in user
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    profile = get_user_profile(current_user_id)

    return jsonify({
        'success': True,
        'message': 'Profile retrieved successfully.',
        'data': profile
    }), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """
    Update Logged-in User Profile Endpoint
    ---
    tags:
      - User Profile
    summary: Update profile information for logged-in user
    security:
      - Bearer: []
    responses:
      200:
        description: Profile updated successfully
      400:
        description: Validation error
      409:
        description: Conflict error
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    validated_data = validate_profile_update_input(data)
    updated_profile = update_user_profile(current_user_id, validated_data)

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully.',
        'data': updated_profile
    }), 200


@users_bp.route('/<string:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    View Public Profile Endpoint
    ---
    tags:
      - User Profile
    summary: Retrieve public user profile with engagement stats
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Public profile retrieved successfully
      404:
        description: User not found
    """
    profile = get_public_user_profile(str(user_id))

    return jsonify({
        'success': True,
        'message': 'Public profile retrieved successfully.',
        'data': profile
    }), 200


@users_bp.route('/username/<string:username>', methods=['GET'])
def get_user_by_username(username):
    """
    View Public Profile by Username Endpoint
    """
    profile = get_public_user_profile_by_username(username)

    return jsonify({
        'success': True,
        'message': 'Public profile retrieved successfully.',
        'data': profile
    }), 200


@users_bp.route('/search', methods=['GET'])
def search():
    """
    Search Users Endpoint
    ---
    tags:
      - User Profile
    summary: Search users by username
    parameters:
      - in: query
        name: q
        required: true
        type: string
      - in: query
        name: page
        required: false
        type: integer
        default: 1
      - in: query
        name: per_page
        required: false
        type: integer
        default: 10
    responses:
      200:
        description: Search results retrieved successfully
    """
    query_string = request.args.get('q', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    results = search_users(query_string, page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'User search results retrieved successfully.',
        'data': results
    }), 200


@users_bp.route('/me/profile-picture', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def upload_my_profile_picture():
    """
    Upload Profile Picture Endpoint
    ---
    tags:
      - User Profile
    summary: Upload or update profile picture
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
    responses:
      200:
        description: Profile picture uploaded successfully
      413:
        description: File size exceeds 5 MB limit
      415:
        description: Unsupported file format
      429:
        description: Rate limit exceeded (10 per minute)
    """
    current_user_id = get_jwt_identity()
    file_storage = request.files.get('file')
    ext = validate_profile_picture_upload(file_storage)
    result = upload_profile_picture(current_user_id, file_storage, ext)

    return jsonify({
        'success': True,
        'message': 'Profile picture uploaded successfully.',
        'data': result
    }), 200


@users_bp.route('/me/profile-picture', methods=['DELETE'])
@jwt_required()
def delete_my_profile_picture():
    """
    Delete Profile Picture Endpoint
    ---
    tags:
      - User Profile
    summary: Remove profile picture
    security:
      - Bearer: []
    responses:
      200:
        description: Profile picture deleted successfully
      404:
        description: User profile not found
    """
    current_user_id = get_jwt_identity()
    result = delete_profile_picture(current_user_id)

    return jsonify({
        'success': True,
        'message': 'Profile picture deleted successfully.',
        'data': result
    }), 200
