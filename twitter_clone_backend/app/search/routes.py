from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.search.services import global_search

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'])
def perform_search():
    """
    Global Search Endpoint
    ---
    tags:
      - Search
    summary: Search across users, posts, and hashtags
    parameters:
      - in: query
        name: q
        required: true
        type: string
        description: Search term or #hashtag
      - in: query
        name: type
        required: false
        type: string
        enum: [all, users, posts, hashtags]
        default: all
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
        description: Search results retrieved successfully
    """
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        pass

    query_str = request.args.get('q', default='', type=str)
    search_type = request.args.get('type', default='all', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    results = global_search(
        query_str,
        search_type=search_type,
        current_user_id=current_user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'message': 'Search results retrieved.',
        'data': results
    }), 200
