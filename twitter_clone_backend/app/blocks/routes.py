from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.blocks.services import (
    block_user,
    unblock_user,
    get_blocked_users
)

blocks_bp = Blueprint('blocks', __name__)


@blocks_bp.route('/users/<uuid:user_id>/block', methods=['POST'])
@jwt_required()
def block_a_user(user_id):
    """
    Block User Endpoint
    ---
    tags:
      - Block System
    summary: Block a user
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: User blocked successfully
    """
    current_user_id = get_jwt_identity()
    result = block_user(current_user_id, str(user_id))
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@blocks_bp.route('/users/<uuid:user_id>/block', methods=['DELETE'])
@jwt_required()
def unblock_a_user(user_id):
    """
    Unblock User Endpoint
    ---
    tags:
      - Block System
    summary: Unblock a user
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: User unblocked successfully
    """
    current_user_id = get_jwt_identity()
    result = unblock_user(current_user_id, str(user_id))
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@blocks_bp.route('/blocks', methods=['GET'])
@jwt_required()
def list_blocked():
    """
    Get Blocked Users Endpoint
    ---
    tags:
      - Block System
    summary: Retrieve list of blocked users
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
        description: Blocked users list retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_blocked_users(current_user_id, page=page, per_page=per_page)
    return jsonify({
        'success': True,
        'message': 'Blocked users list retrieved.',
        'data': result
    }), 200
