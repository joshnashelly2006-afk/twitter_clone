from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.admin.services import (
    get_dashboard_stats,
    list_all_users,
    toggle_user_suspension,
    list_reports,
    resolve_report,
    admin_delete_post
)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    """
    Get Admin Dashboard Stats Endpoint
    ---
    tags:
      - Admin Panel
    summary: Overview dashboard analytics (Admin Only)
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard analytics retrieved successfully
      403:
        description: Forbidden (Not Admin)
    """
    current_user_id = get_jwt_identity()
    result = get_dashboard_stats(current_user_id)
    return jsonify({
        'success': True,
        'message': 'Dashboard statistics retrieved.',
        'data': result
    }), 200


@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def admin_users_list():
    """
    List All Users Endpoint
    ---
    tags:
      - Admin Panel
    summary: Retrieve paginated user management list (Admin Only)
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
        description: User list retrieved successfully
    """
    current_user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = list_all_users(current_user_id, page=page, per_page=per_page)
    return jsonify({
        'success': True,
        'message': 'User accounts list retrieved.',
        'data': result
    }), 200


@admin_bp.route('/admin/users/<string:user_id>/suspend', methods=['PUT'])
@jwt_required()
def suspend_user(user_id):
    """
    Suspend / Unsuspend User Endpoint
    ---
    tags:
      - Admin Panel
    summary: Suspend or restore user account (Admin Only)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
        format: uuid
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            suspend:
              type: boolean
              default: true
    responses:
      200:
        description: User suspension status updated successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    suspend_flag = data.get('suspend', True)

    result = toggle_user_suspension(current_user_id, str(user_id), suspend=suspend_flag)
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@admin_bp.route('/admin/reports', methods=['GET'])
@jwt_required()
def admin_reports_list():
    """
    List Content Moderation Reports Endpoint
    ---
    tags:
      - Admin Panel
    summary: Retrieve moderation reports (Admin Only)
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        default: PENDING
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
        description: Moderation reports list retrieved
    """
    current_user_id = get_jwt_identity()
    status = request.args.get('status', default='PENDING', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = list_reports(current_user_id, status=status, page=page, per_page=per_page)
    return jsonify({
        'success': True,
        'message': 'Moderation reports retrieved.',
        'data': result
    }), 200


@admin_bp.route('/admin/reports/<string:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """
    Resolve Report Endpoint
    ---
    tags:
      - Admin Panel
    summary: Resolve or dismiss report (Admin Only)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: report_id
        required: true
        type: string
        format: uuid
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [RESOLVED, DISMISSED]
    responses:
      200:
        description: Report updated successfully
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    status = data.get('status', 'RESOLVED')

    result = resolve_report(current_user_id, str(report_id), status=status)
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200


@admin_bp.route('/admin/posts/<string:post_id>', methods=['DELETE'])
@jwt_required()
def admin_remove_post(post_id):
    """
    Admin Delete Post Endpoint
    ---
    tags:
      - Admin Panel
    summary: Force delete post (Admin Only)
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
        description: Post deleted by admin
    """
    current_user_id = get_jwt_identity()
    result = admin_delete_post(current_user_id, str(post_id))
    return jsonify({
        'success': True,
        'message': result['message'],
        'data': {}
    }), 200
