from app.errors import ValidationError

MAX_POST_CONTENT_LENGTH = 280


def validate_post_creation(content, file_storage):
    """
    Validate post creation inputs.
    Content is required if no media is provided.
    """
    has_content = content is not None and bool(str(content).strip())
    has_file = file_storage is not None and bool(file_storage.filename)

    if not has_content and not has_file:
        raise ValidationError('Post must contain either text content or a media attachment.')

    content_str = str(content).strip() if has_content else ''
    if len(content_str) > MAX_POST_CONTENT_LENGTH:
        raise ValidationError(f'Post content cannot exceed {MAX_POST_CONTENT_LENGTH} characters.')

    return content_str


def validate_post_update(data, file_storage):
    """
    Validate post update inputs.
    """
    if data is None and file_storage is None:
        raise ValidationError('No update fields or media provided.')

    content = data.get('content') if isinstance(data, dict) else None
    remove_media = False

    if isinstance(data, dict) and 'remove_media' in data:
        raw_val = data.get('remove_media')
        remove_media = str(raw_val).lower() in ('true', '1', 'yes')

    content_str = None
    if content is not None:
        content_str = str(content).strip()
        if len(content_str) > MAX_POST_CONTENT_LENGTH:
            raise ValidationError(f'Post content cannot exceed {MAX_POST_CONTENT_LENGTH} characters.')

    return content_str, remove_media
