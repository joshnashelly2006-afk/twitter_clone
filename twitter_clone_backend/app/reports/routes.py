from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.reports.services import submit_report

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    """
    Submit Report Endpoint
    ---
    tags:
      - Reporting
    summary: Report user or post for moderation
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - reason
          properties:
            reported_user_id:
              type: string
              format: uuid
            reported_post_id:
              type: string
              format: uuid
            reason:
              type: string
              enum: [SPAM, ABUSE, HARASSMENT, VIOLENCE, OTHER]
            details:
              type: string
    responses:
      201:
        description: Report submitted successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    result = submit_report(current_user_id, data)

    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {'id': result['id']}
    }), 201
