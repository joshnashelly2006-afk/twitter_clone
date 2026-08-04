from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.trending.services import (
    get_trending_hashtags,
    get_trending_posts,
    get_trending_users,
    get_user_analytics
)

trending_bp = Blueprint('trending', __name__)


@trending_bp.route('/trending/hashtags', methods=['GET'])
def list_trending_hashtags():
    """
    Get Trending Hashtags Endpoint
    ---
    tags:
      - Trending & Analytics
    summary: Retrieve popular trending hashtags
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
    responses:
      200:
        description: Trending hashtags retrieved successfully
    """
    limit = request.args.get('limit', default=10, type=int)
    result = get_trending_hashtags(limit=limit)

    return jsonify({
        'success': True,
        'message': 'Trending hashtags retrieved.',
        'data': result
    }), 200


@trending_bp.route('/trending/posts', methods=['GET'])
def list_trending_posts():
    """
    Get Trending Posts Endpoint
    ---
    tags:
      - Trending & Analytics
    summary: Retrieve high-engagement trending posts
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
    responses:
      200:
        description: Trending posts retrieved successfully
    """
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        pass

    limit = request.args.get('limit', default=10, type=int)
    result = get_trending_posts(limit=limit, current_user_id=current_user_id)

    return jsonify({
        'success': True,
        'message': 'Trending posts retrieved.',
        'data': result
    }), 200


@trending_bp.route('/trending/users', methods=['GET'])
def list_trending_users():
    """
    Get Trending Users Endpoint
    ---
    tags:
      - Trending & Analytics
    summary: Retrieve top followed users
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
    responses:
      200:
        description: Trending users retrieved successfully
    """
    limit = request.args.get('limit', default=10, type=int)
    result = get_trending_users(limit=limit)

    return jsonify({
        'success': True,
        'message': 'Trending users retrieved.',
        'data': result
    }), 200


@trending_bp.route('/users/me/analytics', methods=['GET'])
@jwt_required()
def user_analytics():
    """
    Get User Account Analytics Endpoint
    ---
    tags:
      - Trending & Analytics
    summary: Retrieve personal account engagement metrics
    security:
      - Bearer: []
    responses:
      200:
        description: Account analytics retrieved successfully
    """
    current_user_id = get_jwt_identity()
    result = get_user_analytics(current_user_id)

    return jsonify({
        'success': True,
        'message': 'User analytics retrieved.',
        'data': result
    }), 200
