from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Like(BaseModel):
    """Like Model representing user post likes."""

    __tablename__ = 'likes'

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
    )

    # Relationships
    user = relationship('User', back_populates='likes')
    post = relationship('Post', back_populates='likes')

    def __repr__(self):
        return f"<Like(id='{self.id}', user_id='{self.user_id}', post_id='{self.post_id}')>"
