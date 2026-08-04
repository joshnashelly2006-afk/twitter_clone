from app.errors import ValidationError

MAX_COMMENT_LENGTH = 280


def validate_comment_input(data):
    """
    Validate comment payload.
    Checks required comment text and length constraints.
    """
    if not data or not isinstance(data, dict):
        raise ValidationError('Request body must be a valid JSON object.')

    comment_text = data.get('comment')
    if comment_text is None or not str(comment_text).strip():
        raise ValidationError('Comment text is required.')

    clean_text = str(comment_text).strip()
    if len(clean_text) < 1:
        raise ValidationError('Comment cannot be empty.')

    if len(clean_text) > MAX_COMMENT_LENGTH:
        raise ValidationError(f'Comment cannot exceed {MAX_COMMENT_LENGTH} characters.')

    return clean_text
