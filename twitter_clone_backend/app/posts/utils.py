import os
import uuid
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename
from app.errors import ValidationError, PayloadTooLargeError, UnsupportedMediaTypeError

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_VIDEO_EXTENSIONS)

ALLOWED_IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
ALLOWED_VIDEO_MIME_TYPES = {'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/mkv'}
ALLOWED_MIME_TYPES = ALLOWED_IMAGE_MIME_TYPES.union(ALLOWED_VIDEO_MIME_TYPES)

MAX_MEDIA_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def allowed_file(filename):
    """Check if filename has an allowed image or video extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def detect_media_type(ext):
    """Determine whether extension is image or video."""
    ext_lower = ext.lower()
    if ext_lower in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext_lower in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    return None


def generate_unique_filename(ext):
    """Generate unique UUID v4 filename with given extension."""
    return f"{uuid.uuid4().hex}.{ext.lower()}"


def save_uploaded_file(file_storage):
    """
    Validate, sanitize, and save uploaded image/video file stream.

    Returns:
        tuple: (relative_db_path, media_type)
    """
    if file_storage is None or not file_storage.filename:
        return None, None

    filename = secure_filename(file_storage.filename)
    if not filename or '.' not in filename:
        raise ValidationError('Invalid file name.')

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaTypeError(
            f'Unsupported file format .{ext}. Allowed formats: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        )

    # Check MIME type
    content_type = getattr(file_storage, 'content_type', '').lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise UnsupportedMediaTypeError('Invalid MIME type for uploaded media file.')

    # Check file size (<= 50MB)
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)

    if size > MAX_MEDIA_SIZE_BYTES:
        raise PayloadTooLargeError('Media file size exceeds maximum allowed limit of 50 MB.')

    media_type = detect_media_type(ext)
    unique_filename = generate_unique_filename(ext)

    # Base folder configuration
    if media_type == 'image':
        target_dir = Path(current_app.config['UPLOAD_FOLDER']) / 'posts' / 'images'
        relative_path = f"uploads/posts/images/{unique_filename}"
    else:
        target_dir = Path(current_app.config['UPLOAD_FOLDER']) / 'posts' / 'videos'
        relative_path = f"uploads/posts/videos/{unique_filename}"

    target_dir.mkdir(parents=True, exist_ok=True)
    destination_path = target_dir / unique_filename

    file_storage.save(destination_path)

    return relative_path, media_type


def delete_uploaded_file(relative_path):
    """Safely delete uploaded file from server disk."""
    if not relative_path:
        return

    try:
        root_dir = Path(current_app.config['UPLOAD_FOLDER']).parent
        file_path = root_dir / relative_path
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
    except Exception:
        pass  # Ignore filesystem cleanup glitches
