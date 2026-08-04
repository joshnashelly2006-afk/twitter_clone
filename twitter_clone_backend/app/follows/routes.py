from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.follows.services import (
    follow_user,
    unfollow_user,
    get_user_followers,
    get_user_following,
    get_follow_status
)

follows_bp = Blueprint('follows', __name__)


@follows_bp.route('/users/<uuid:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_a_user(user_id):
    """
    Follow User Endpoint
    ---
    tags:
      - Follows
    summary: Follow a user
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
        description: User followed successfully
    """
    current_user_id = get_jwt_identity()
    result = follow_user(current_user_id, str(user_id))

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {
            'followers_count': result['followers_count']
        }
    }), 200


@follows_bp.route('/users/<uuid:user_id>/follow', methods=['DELETE'])
@jwt_required()
def unfollow_a_user(user_id):
    """
    Unfollow User Endpoint
    ---
    tags:
      - Follows
    summary: Unfollow a user
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
        description: User unfollowed successfully
    """
    current_user_id = get_jwt_identity()
    result = unfollow_user(current_user_id, str(user_id))

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {
            'followers_count': result['followers_count']
        }
    }), 200


@follows_bp.route('/users/<uuid:user_id>/followers', methods=['GET'])
def get_followers_list(user_id):
    """
    Get User Followers Endpoint
    ---
    tags:
      - Follows
    summary: Retrieve list of followers for a user
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
        description: Followers list retrieved successfully
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_user_followers(str(user_id), page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Followers list retrieved successfully.',
        'data': result
    }), 200


@follows_bp.route('/users/<uuid:user_id>/following', methods=['GET'])
def get_following_list(user_id):
    """
    Get User Following List Endpoint
    ---
    tags:
      - Follows
    summary: Retrieve list of users followed by a user
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
        description: Following list retrieved successfully
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_user_following(str(user_id), page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Following list retrieved successfully.',
        'data': result
    }), 200


@follows_bp.route('/users/<uuid:user_id>/follow-status', methods=['GET'])
@jwt_required()
def get_mutual_follow_status(user_id):
    """
    Get Follow Status Endpoint
    ---
    tags:
      - Follows
    summary: Check mutual follow status between current user and target user
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
        description: Follow status retrieved successfully
    """
    current_user_id = get_jwt_identity()
    result = get_follow_status(current_user_id, str(user_id))

    return jsonify({
        'success': True,
        'message': 'Follow status retrieved successfully.',
        'data': result
    }), 200
