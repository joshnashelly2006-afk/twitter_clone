from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.notifications.services import (
    get_user_notifications,
    get_unread_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification
)

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def list_notifications():
    """
    Get Notifications Endpoint
    ---
    tags:
      - Notifications
    summary: Retrieve paginated notifications list for authenticated user
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
        description: Notifications retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = get_user_notifications(current_user_id, page=page, per_page=per_page)
    return jsonify({
        'success': True,
        'message': 'Notifications retrieved successfully.',
        'data': result
    }), 200


@notifications_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    """
    Get Unread Notifications Count Endpoint
    ---
    tags:
      - Notifications
    summary: Retrieve count of unread notifications
    security:
      - Bearer: []
    responses:
      200:
        description: Unread count retrieved successfully
    """
    current_user_id = get_jwt_identity()
    result = get_unread_count(current_user_id)
    return jsonify({
        'success': True,
        'message': 'Unread notification count retrieved.',
        'data': result
    }), 200


@notifications_bp.route('/notifications/<uuid:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    """
    Mark Notification Read Endpoint
    ---
    tags:
      - Notifications
    summary: Mark single notification as read
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Notification marked as read
    """
    current_user_id = get_jwt_identity()
    result = mark_notification_as_read(str(notification_id), current_user_id)
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@notifications_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """
    Mark All Notifications Read Endpoint
    ---
    tags:
      - Notifications
    summary: Mark all notifications as read
    security:
      - Bearer: []
    responses:
      200:
        description: All notifications marked as read
    """
    current_user_id = get_jwt_identity()
    result = mark_all_notifications_as_read(current_user_id)
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@notifications_bp.route('/notifications/<uuid:notification_id>', methods=['DELETE'])
@jwt_required()
def remove_notification(notification_id):
    """
    Delete Notification Endpoint
    ---
    tags:
      - Notifications
    summary: Delete a notification
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        required: true
        type: string
        format: uuid
    responses:
      200:
        description: Notification deleted successfully
    """
    current_user_id = get_jwt_identity()
    result = delete_notification(str(notification_id), current_user_id)
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200
