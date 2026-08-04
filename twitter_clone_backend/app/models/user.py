from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User Model representing application users."""

    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_suspended = Column(Boolean, default=False, nullable=False)

    # Relationships
    posts = relationship(
        'Post',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select'
    )
    comments = relationship(
        'Comment',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select'
    )
    likes = relationship(
        'Like',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select'
    )
    followers = relationship(
        'Follow',
        foreign_keys='Follow.following_id',
        back_populates='following',
        cascade='all, delete-orphan',
        lazy='select'
    )
    following = relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        back_populates='follower',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', is_admin={self.is_admin})>"
