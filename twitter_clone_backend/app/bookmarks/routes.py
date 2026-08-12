from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.bookmarks.services import (
    bookmark_post,
    unbookmark_post,
    get_user_bookmarks
)

bookmarks_bp = Blueprint('bookmarks', __name__)


@bookmarks_bp.route('/posts/<string:post_id>/bookmark', methods=['POST'])
@jwt_required()
def add_bookmark(post_id):
    """
    Bookmark Post Endpoint
    ---
    tags:
      - Bookmarks
    summary: Save a post to bookmarks
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
        description: Post bookmarked successfully
      409:
        description: Post already bookmarked
    """
    current_user_id = get_jwt_identity()
    result = bookmark_post(current_user_id, str(post_id))
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@bookmarks_bp.route('/posts/<string:post_id>/bookmark', methods=['DELETE'])
@jwt_required()
def remove_bookmark(post_id):
    """
    Remove Bookmark Endpoint
    ---
    tags:
      - Bookmarks
    summary: Remove a saved post from bookmarks
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
        description: Bookmark removed successfully
    """
    current_user_id = get_jwt_identity()
    result = unbookmark_post(current_user_id, str(post_id))
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@bookmarks_bp.route('/bookmarks', methods=['GET'])
@jwt_required()
def list_bookmarks():
    """
    Get Bookmarked Posts Endpoint
    ---
    tags:
      - Bookmarks
    summary: Retrieve paginated list of saved posts
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 10
    responses:
      200:
        description: Bookmarks list retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_user_bookmarks(current_user_id, page=page, per_page=per_page)
    return jsonify({
        'success': True,
        'message': 'Bookmarked posts retrieved successfully.',
        'data': result
    }), 200
