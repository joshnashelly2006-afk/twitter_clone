import os
from werkzeug.utils import secure_filename
from app.auth.validators import validate_email_format
from app.errors import ValidationError, PayloadTooLargeError, UnsupportedMediaTypeError

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_BIO_LENGTH = 160


def validate_profile_update_input(data):
    """Validate user profile update payload."""
    if not data or not isinstance(data, dict):
        raise ValidationError('Request body must be a valid JSON object.')

    validated_data = {}

    if 'username' in data and data['username'] is not None:
        username_str = str(data['username']).strip()
        if len(username_str) < 3 or len(username_str) > 50:
            raise ValidationError('Username must be between 3 and 50 characters.')
        validated_data['username'] = username_str

    if 'email' in data and data['email'] is not None:
        email_str = str(data['email']).strip().lower()
        validate_email_format(email_str)
        validated_data['email'] = email_str

    if 'bio' in data:
        if data['bio'] is None:
            validated_data['bio'] = ''
        else:
            bio_str = str(data['bio']).strip()
            if len(bio_str) > MAX_BIO_LENGTH:
                raise ValidationError(f'Bio length cannot exceed {MAX_BIO_LENGTH} characters.')
            validated_data['bio'] = bio_str

    if not validated_data:
        raise ValidationError('At least one valid field (username, email, or bio) must be provided for update.')

    return validated_data


def validate_profile_picture_upload(file_storage):
    """
    Validate uploaded profile picture file.

    Checks:
    - Missing file
    - Filename sanitization / path traversal check
    - File extension check (.jpg, .jpeg, .png, .webp)
    - MIME type check
    - File size check (<= 5MB)
    """
    if file_storage is None or not file_storage.filename:
        raise ValidationError('No profile picture file provided in request.')

    # Sanitize filename to prevent path traversal attacks
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
        raise UnsupportedMediaTypeError('Invalid MIME type for profile picture.')

    # Check file size by seeking end of stream
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)  # Reset stream position

    if size > MAX_FILE_SIZE_BYTES:
        raise PayloadTooLargeError('File size exceeds maximum allowed limit of 5 MB.')

    return ext
