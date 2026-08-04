from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.likes.services import (
    like_post,
    unlike_post,
    get_post_likes,
    check_user_liked_post
)

likes_bp = Blueprint('likes', __name__)


@likes_bp.route('/posts/<uuid:post_id>/like', methods=['POST'])
@jwt_required()
def like_a_post(post_id):
    """
    Like Post Endpoint
    ---
    tags:
      - Likes
    summary: Like a post
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
        description: Post liked successfully
      409:
        description: Conflict (already liked)
    """
    current_user_id = get_jwt_identity()
    result = like_post(current_user_id, str(post_id))

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {
            'likes_count': result['likes_count'],
            'liked': result['liked']
        }
    }), 200


@likes_bp.route('/posts/<uuid:post_id>/like', methods=['DELETE'])
@jwt_required()
def unlike_a_post(post_id):
    """
    Unlike Post Endpoint
    ---
    tags:
      - Likes
    summary: Unlike a post
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
        description: Post unliked successfully
    """
    current_user_id = get_jwt_identity()
    result = unlike_post(current_user_id, str(post_id))

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {
            'likes_count': result['likes_count'],
            'liked': result['liked']
        }
    }), 200


@likes_bp.route('/posts/<uuid:post_id>/likes', methods=['GET'])
def get_post_likers(post_id):
    """
    List Users Who Liked Post Endpoint
    ---
    tags:
      - Likes
    summary: Get users who liked a post
    parameters:
      - in: path
        name: post_id
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
        description: Likers list retrieved successfully
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_post_likes(str(post_id), page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Post likers retrieved successfully.',
        'data': result
    }), 200


@likes_bp.route('/posts/<uuid:post_id>/liked', methods=['GET'])
@jwt_required()
def get_user_liked_status(post_id):
    """
    Check Logged-in User Liked Status Endpoint
    ---
    tags:
      - Likes
    summary: Check whether current user liked a post
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
        description: Liked status retrieved successfully
    """
    current_user_id = get_jwt_identity()
    result = check_user_liked_post(current_user_id, str(post_id))

    return jsonify({
        'success': True,
        'message': 'Liked status retrieved successfully.',
        'data': result
    }), 200
