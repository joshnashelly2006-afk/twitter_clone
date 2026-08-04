from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.settings.services import get_settings, update_settings

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@jwt_required()
def retrieve_settings():
    """
    Get User Settings Endpoint
    ---
    tags:
      - Settings
    summary: Retrieve user application preferences
    security:
      - Bearer: []
    responses:
      200:
        description: User settings retrieved successfully
    """
    current_user_id = get_jwt_identity()
    result = get_settings(current_user_id)
    return jsonify({
        'success': True,
        'message': 'User settings retrieved.',
        'data': result
    }), 200


@settings_bp.route('/settings', methods=['PUT'])
@jwt_required()
def modify_settings():
    """
    Update User Settings Endpoint
    ---
    tags:
      - Settings
    summary: Update user preferences
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            dark_mode:
              type: boolean
            is_private:
              type: boolean
            email_notifications:
              type: boolean
            push_notifications:
              type: boolean
            language:
              type: string
    responses:
      200:
        description: User settings updated successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    result = update_settings(current_user_id, data)

    return jsonify({
        'success': True,
        'message': 'User settings updated successfully.',
        'data': result
    }), 200
