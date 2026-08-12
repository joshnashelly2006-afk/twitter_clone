from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Hashtag(BaseModel):
    """Hashtag Model storing unique hashtag names and usage frequency."""

    __tablename__ = 'hashtags'

    name = Column(String(100), unique=True, nullable=False, index=True)
    use_count = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<Hashtag(id='{self.id}', name='{self.name}', use_count={self.use_count})>"


class PostHashtag(BaseModel):
    """PostHashtag Model linking posts and hashtags."""

    __tablename__ = 'post_hashtags'

    post_id = Column(
        String(36),
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    hashtag_id = Column(
        String(36),
        ForeignKey('hashtags.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint('post_id', 'hashtag_id', name='uq_post_hashtag'),
    )

    # Relationships
    post = relationship('Post')
    hashtag = relationship('Hashtag')

    def __repr__(self):
        return f"<PostHashtag(post_id='{self.post_id}', hashtag_id='{self.hashtag_id}')>"
