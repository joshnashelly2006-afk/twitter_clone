from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Comment(BaseModel):
    """Comment Model representing replies/comments on posts."""

    __tablename__ = 'comments'

    user_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    post_id = Column(
        String(36),
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
