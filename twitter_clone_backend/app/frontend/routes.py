from flask import render_template
from app.frontend import frontend_bp

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/feed')
def feed():
    return render_template('feed.html')

@frontend_bp.route('/<username>')
def profile(username):
    return render_template('profile.html', username=username)

@frontend_bp.route('/uploads/<path:filename>')
def serve_uploads(filename):
    from flask import send_from_directory, current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
