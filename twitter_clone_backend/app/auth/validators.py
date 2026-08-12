import re
from app.errors import ValidationError

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def validate_email_format(email):
    """Validate email address format using regular expression."""
    if not email or not re.match(EMAIL_REGEX, str(email).strip()):
        raise ValidationError('Invalid email format.')


def validate_registration_input(data):
    """Validate registration payload."""
    if not data or not isinstance(data, dict):
        raise ValidationError('Request body must be a valid JSON object.')

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password') or data.get('password_confirmation')

    if not username or not str(username).strip():
        raise ValidationError('Username is required.')

    username_str = str(username).strip()
    if len(username_str) < 3 or len(username_str) > 50:
        raise ValidationError('Username must be between 3 and 50 characters.')

    if not email or not str(email).strip():
        raise ValidationError('Email is required.')

    validate_email_format(str(email).strip())

    if not password:
        raise ValidationError('Password is required.')

    if len(str(password)) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

    if confirm_password is None:
        raise ValidationError('Password confirmation is required.')

    if str(password) != str(confirm_password):
        raise ValidationError('Password and password confirmation do not match.')

    return {
        'username': username_str,
        'email': str(email).strip().lower(),
        'password': str(password)
    }


def validate_login_input(data):
    """Validate login payload (supports email or username)."""
    if not data or not isinstance(data, dict):
        raise ValidationError('Request body must be a valid JSON object.')

    identifier = data.get('email') or data.get('username') or data.get('emailOrUsername')
    password = data.get('password')

    if not identifier or not str(identifier).strip():
        raise ValidationError('Email or username is required.')

    if not password:
        raise ValidationError('Password is required.')

    return {
        'identifier': str(identifier).strip(),
        'password': str(password)
    }
