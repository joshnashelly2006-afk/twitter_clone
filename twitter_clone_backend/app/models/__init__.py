"""
Models Package Initialization.

All SQLAlchemy models are imported here for centralized access and
Flask-Migrate auto-detection.
"""

from app.models.base import BaseModel
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.follow import Follow
from app.models.bookmark import Bookmark
from app.models.hashtag import Hashtag, PostHashtag
from app.models.notification import Notification
from app.models.block import Block
from app.models.report import Report
from app.models.user_settings import UserSettings

__all__ = [
    'BaseModel',
    'User',
    'Post',
    'Comment',
    'Like',
    'Follow',
    'Bookmark',
    'Hashtag',
    'PostHashtag',
    'Notification',
    'Block',
    'Report',
    'UserSettings',
]
