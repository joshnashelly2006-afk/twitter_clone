from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.comments.validators import validate_comment_input
from app.comments.services import (
    add_comment,
    get_post_comments,
    update_comment,
    delete_comment
)

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/posts/<string:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """
    Add Comment Endpoint
    ---
    tags:
      - Comments
    summary: Add a comment to a post
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        required: true
        type: string
        format: uuid
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - comment
          properties:
            comment:
              type: string
              example: Great post!
    responses:
      201:
        description: Comment created successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    validated_text = validate_comment_input(data)
    comment_data = add_comment(current_user_id, str(post_id), validated_text)

    return jsonify({
        'success': True,
        'message': 'Comment added successfully.',
        'data': comment_data
    }), 201


@comments_bp.route('/posts/<string:post_id>/comments', methods=['GET'])
def get_comments_for_post(post_id):
    """
    Get Post Comments Endpoint
    ---
    tags:
      - Comments
    summary: Retrieve comments for a post
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
        description: Comments retrieved successfully
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_post_comments(str(post_id), page=page, per_page=per_page)

    return jsonify({
        'success': True,
        'message': 'Post comments retrieved successfully.',
        'data': result
    }), 200


@comments_bp.route('/comments/<string:comment_id>', methods=['PUT'])
@jwt_required()
def edit_comment(comment_id):
    """
    Edit Comment Endpoint
    ---
    tags:
      - Comments
    summary: Update comment text
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        required: true
        type: string
        format: uuid
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - comment
          properties:
            comment:
              type: string
    responses:
      200:
        description: Comment updated successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    validated_text = validate_comment_input(data)
    updated = update_comment(str(comment_id), current_user_id, validated_text)

    return jsonify({
        'success': True,
        'message': 'Comment updated successfully.',
        'data': updated
    }), 200


@comments_bp.route('/comments/<string:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_comment(comment_id):
    """
    Delete Comment Endpoint
    ---
    tags:
      - Comments
    summary: Delete a comment
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Comment deleted successfully
    """
    current_user_id = get_jwt_identity()
    result = delete_comment(str(comment_id), current_user_id)

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {'id': str(comment_id)}
    }), 200
