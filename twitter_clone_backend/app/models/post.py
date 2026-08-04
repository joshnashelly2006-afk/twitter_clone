from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Post(BaseModel):
    """Post Model representing tweets/posts created by users."""

    __tablename__ = 'posts'

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=False)
    media_path = Column(String(255), nullable=True)
    media_type = Column(String(20), nullable=True)  # 'image' or 'video'

    # Relationships
    user = relationship('User', back_populates='posts')
    comments = relationship(
        'Comment',
        back_populates='post',
        cascade='all, delete-orphan',
        lazy='select'
    )
    likes = relationship(
        'Like',
        back_populates='post',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self):
        return f"<Post(id='{self.id}', user_id='{self.user_id}', media_type='{self.media_type}')>"
