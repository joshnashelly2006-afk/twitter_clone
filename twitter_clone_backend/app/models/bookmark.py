from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Bookmark(BaseModel):
    """Bookmark Model representing saved posts per user."""

    __tablename__ = 'bookmarks'

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_bookmark'),
    )

    # Relationships
    user = relationship('User')
    post = relationship('Post')

    def __repr__(self):
        return f"<Bookmark(id='{self.id}', user_id='{self.user_id}', post_id='{self.post_id}')>"
