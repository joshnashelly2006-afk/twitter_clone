import os
from flask import Blueprint, send_from_directory, current_app

media_bp = Blueprint('media', __name__)


@media_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    """Serve uploaded image and video media files."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)
