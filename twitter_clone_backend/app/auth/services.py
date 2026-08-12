from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db, bcrypt
from app.models.user import User
from app.errors import ConflictError, UnauthorizedError, NotFoundError

# In-memory JWT blocklist set for revoked tokens (logout)
JWT_BLOCKLIST = set()


def is_token_revoked(jwt_header, jwt_payload):
    """Callback for Flask-JWT-Extended to check if a token is in the blocklist."""
    jti = jwt_payload['jti']
    return jti in JWT_BLOCKLIST


def revoke_token(jti):
    """Add token JTI to blocklist set."""
    JWT_BLOCKLIST.add(jti)


def register_user(validated_data):
    """
    Register a new user.

    Hashes password using Flask-Bcrypt and persists user to DB.
    """
    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    # Check for existing user with username
    if User.query.filter_by(username=username).first():
        raise ConflictError('Username already exists.')

    # Check for existing user with email
    if User.query.filter_by(email=email).first():
        raise ConflictError('Email already registered.')

    # Hash password using Flask-Bcrypt
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create new user instance
    user = User(
        username=username,
        email=email,
        password_hash=hashed_pw
    )

    db.session.add(user)
    db.session.commit()

    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'created_at': user.created_at.isoformat()
    }


def authenticate_user(validated_data):
    """
    Authenticate user credentials (by email or username) and issue JWT access and refresh tokens.
    """
    identifier = validated_data['identifier']
    password = validated_data['password']

    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        raise UnauthorizedError('Invalid email/username or password.')

    if not user.is_active:
        raise UnauthorizedError('User account is deactivated.')

    identity = str(user.id)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'profile_picture': user.profile_picture
        }
    }


def get_current_user_profile(user_id):
    """
    Fetch user profile data by user UUID.
    """
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat()
    }
