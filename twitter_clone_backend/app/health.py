import time
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from app.extensions import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - System
    summary: Check application and database health status
    description: Returns system status, database connectivity check, application version, and uptime in seconds.
    responses:
      200:
        description: System is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            database:
              type: string
              example: healthy
            version:
              type: string
              example: 1.0.0
            uptime_seconds:
              type: number
              example: 3600.5
      500:
        description: System or database issue
    """
    # 1. Database Connectivity Check
    db_status = 'healthy'
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    start_time = current_app.config.get('SERVER_START_TIME', time.time())
    uptime = round(time.time() - start_time, 2)

    is_healthy = db_status == 'healthy'
    status_code = 200 if is_healthy else 500

    return jsonify({
        'status': 'ok' if is_healthy else 'degraded',
        'database': db_status,
        'version': '1.0.0',
        'uptime_seconds': uptime
    }), status_code
