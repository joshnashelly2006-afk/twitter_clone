from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.extensions import limiter
from app.posts.validators import validate_post_creation, validate_post_update
from app.posts.services import (
    create_post,
    get_post_by_id,
    get_my_posts,
    get_user_posts,
    get_personalized_feed,
    get_explore_feed,
    update_post,
    delete_post
)

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('/posts', methods=['POST'])
@jwt_required()
@limiter.limit("120 per minute")
def create_new_post():
    """
    Create Post Endpoint
    ---
    tags:
      - Posts
    summary: Create a new post with optional image or video media attachment
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - in: formData
        name: content
        type: string
        required: false
      - in: formData
        name: media
        type: file
        required: false
    responses:
      201:
        description: Post created successfully
      400:
        description: Content and media both empty
      429:
        description: Rate limit exceeded (20 per minute)
    """
    current_user_id = get_jwt_identity()

    if request.files or request.form:
        content = request.form.get('content')
        file_storage = request.files.get('media')
    else:
        json_data = request.get_json(silent=True) or {}
        content = json_data.get('content')
        file_storage = None

    validated_content = validate_post_creation(content, file_storage)
    new_post = create_post(current_user_id, validated_content, file_storage)

    return jsonify({
        'success': True,
        'message': 'Post created successfully.',
        'data': new_post
    }), 201


@posts_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_user_feed():
    """
    Get Personalized News Feed Endpoint
    ---
    tags:
      - Feed & Explore
    summary: Retrieve personalized news feed for authenticated user
    security:
      - Bearer: []
    parameters:
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
        description: Feed posts retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_personalized_feed(current_user_id, page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Personalized news feed retrieved successfully.',
        'data': result
    }), 200


@posts_bp.route('/explore', methods=['GET'])
def get_global_explore():
    """
    Get Global Explore Feed Endpoint
    ---
    tags:
      - Feed & Explore
    summary: Retrieve global explore feed of latest public posts
    parameters:
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
        description: Explore feed retrieved successfully
    """
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        pass

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_explore_feed(current_user_id=current_user_id, page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Global explore feed retrieved successfully.',
        'data': result
    }), 200


@posts_bp.route('/posts/<string:post_id>', methods=['GET'])
def get_single_post(post_id):
    """
    Get Single Post Endpoint
    ---
    tags:
      - Posts
    summary: Retrieve single post details
    parameters:
      - in: path
        name: post_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Post details retrieved successfully
      404:
        description: Post not found
    """
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        pass

    post_data = get_post_by_id(str(post_id), current_user_id=current_user_id)

    return jsonify({
        'success': True,
        'message': 'Post details retrieved successfully.',
        'data': post_data
    }), 200


@posts_bp.route('/posts/me', methods=['GET'])
@jwt_required()
def get_my_own_posts():
    """
    Get My Posts Endpoint
    ---
    tags:
      - Posts
    summary: Retrieve posts created by logged-in user
    security:
      - Bearer: []
    parameters:
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
        description: User posts retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_my_posts(current_user_id, page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'User posts retrieved successfully.',
        'data': result
    }), 200


@posts_bp.route('/posts/user/<string:user_id>', methods=['GET'])
def get_posts_by_user_id(user_id):
    """
    Get Posts by User Endpoint
    ---
    tags:
      - Posts
    summary: Retrieve public posts by a specific user
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        format: uuid
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
        description: Posts retrieved successfully
    """
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        pass

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_user_posts(str(user_id), current_user_id=current_user_id, page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Posts retrieved successfully.',
        'data': result
    }), 200


@posts_bp.route('/posts/<string:post_id>', methods=['PUT'])
@jwt_required()
def update_existing_post(post_id):
    """
    Update Post Endpoint
    ---
    tags:
      - Posts
    summary: Edit post content or replace/remove media attachment
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Post updated successfully
      403:
        description: Forbidden (not owner)
    """
    current_user_id = get_jwt_identity()

    if request.files or request.form:
        data = request.form.to_dict()
        file_storage = request.files.get('media')
    else:
        data = request.get_json(silent=True) or {}
        file_storage = None

    content_str, remove_media = validate_post_update(data, file_storage)
    updated_post = update_post(str(post_id), current_user_id, content_str, file_storage, remove_media)

    return jsonify({
        'success': True,
        'message': 'Post updated successfully.',
        'data': updated_post
    }), 200


@posts_bp.route('/posts/<string:post_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_post(post_id):
    """
    Delete Post Endpoint
    ---
    tags:
      - Posts
    summary: Delete a post and its media file
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Post deleted successfully
      403:
        description: Forbidden (not owner)
    """
    current_user_id = get_jwt_identity()
    result = delete_post(str(post_id), current_user_id)

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {'id': str(post_id)}
    }), 200
