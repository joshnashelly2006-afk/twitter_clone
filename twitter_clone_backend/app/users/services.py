import os
import uuid
from pathlib import Path
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from app.errors import NotFoundError, ConflictError


def get_user_profile(user_id):
    """Fetch full profile data for logged-in user including counts."""
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    posts_count = Post.query.filter_by(user_id=user.id).count()
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'posts_count': posts_count,
        'followers_count': follower_count,
        'following_count': following_count,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }


def update_user_profile(user_id, validated_data):
    """
    Update logged-in user profile (username, email, bio).
    Checks for uniqueness if username or email is modified.
    """
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    # Check username uniqueness if updating username
    if 'username' in validated_data and validated_data['username'] != user.username:
        existing = User.query.filter_by(username=validated_data['username']).first()
        if existing:
            raise ConflictError('Username is already taken.')
        user.username = validated_data['username']

    # Check email uniqueness if updating email
    if 'email' in validated_data and validated_data['email'] != user.email:
        existing = User.query.filter_by(email=validated_data['email']).first()
        if existing:
            raise ConflictError('Email is already registered.')
        user.email = validated_data['email']

    # Update bio if provided
    if 'bio' in validated_data:
        user.bio = validated_data['bio']

    db.session.commit()

    posts_count = Post.query.filter_by(user_id=user.id).count()
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'posts_count': posts_count,
        'followers_count': follower_count,
        'following_count': following_count,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }


def get_public_user_profile(target_user_id):
    """
    Fetch public profile information and metrics for a specific user.
    """
    user = User.query.get(target_user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    posts_count = Post.query.filter_by(user_id=user.id).count()
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return {
        'id': str(user.id),
        'username': user.username,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'posts_count': posts_count,
        'followers_count': follower_count,
        'following_count': following_count
    }


def get_public_user_profile_by_username(username):
    """
    Fetch public profile information by username.
    """
    user = User.query.filter_by(username=username).first()
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    posts_count = Post.query.filter_by(user_id=user.id).count()
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    return {
        'id': str(user.id),
        'username': user.username,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'posts_count': posts_count,
        'followers_count': follower_count,
        'following_count': following_count
    }


def search_users(query_string, page=1, per_page=10):
    """
    Search users by username (partial, case-insensitive) with pagination.
    """
    if not query_string or not str(query_string).strip():
        return {
            'users': [],
            'pagination': {
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0
            }
        }

    search_pattern = f"%{str(query_string).strip()}%"
    pagination = User.query.filter(
        User.username.ilike(search_pattern),
        User.is_active.is_(True)
    ).order_by(User.username.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    user_list = [
        {
            'id': str(user.id),
            'username': user.username,
            'bio': user.bio,
            'profile_picture': user.profile_picture
        }
        for user in pagination.items
    ]

    return {
        'users': user_list,
        'pagination': {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    }


def upload_profile_picture(user_id, file_storage, ext):
    """
    Store profile picture in uploads/images/profile/ using UUID filename.
    Removes old picture file if present and updates DB relative path.
    """
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    base_dir = Path(current_app.config['IMAGE_UPLOAD_FOLDER'])
    profile_dir = base_dir / 'profile'
    profile_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    destination_path = profile_dir / unique_filename

    file_storage.save(destination_path)
    relative_db_path = f"uploads/images/profile/{unique_filename}"

    if user.profile_picture:
        try:
            root_dir = Path(current_app.config['UPLOAD_FOLDER']).parent
            old_file_path = root_dir / user.profile_picture
            if old_file_path.exists() and old_file_path.is_file():
                old_file_path.unlink()
        except Exception:
            pass

    user.profile_picture = relative_db_path
    db.session.commit()

    return {
        'id': str(user.id),
        'username': user.username,
        'profile_picture': relative_db_path
    }


def delete_profile_picture(user_id):
    """
    Delete profile picture file from server and set database field to None.
    """
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise NotFoundError('User profile not found.')

    if user.profile_picture:
        try:
            root_dir = Path(current_app.config['UPLOAD_FOLDER']).parent
            old_file_path = root_dir / user.profile_picture
            if old_file_path.exists() and old_file_path.is_file():
                old_file_path.unlink()
        except Exception:
            pass

        user.profile_picture = None
        db.session.commit()

    return {
        'id': str(user.id),
        'username': user.username,
        'profile_picture': None
    }
