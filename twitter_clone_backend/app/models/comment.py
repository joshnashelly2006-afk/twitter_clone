from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Comment(BaseModel):
    """Comment Model representing replies/comments on posts."""

    __tablename__ = 'comments'

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
    comment = Column(Text, nullable=False)

    # Relationships
    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')

    def __repr__(self):
        return f"<Comment(id='{self.id}', user_id='{self.user_id}', post_id='{self.post_id}')>"
