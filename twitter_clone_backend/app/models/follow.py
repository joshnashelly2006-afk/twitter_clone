from sqlalchemy import Column, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Follow(BaseModel):
    """Follow Model representing follower/following relationship between users."""

    __tablename__ = 'follows'

    follower_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    following_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
        CheckConstraint('follower_id != following_id', name='ck_prevent_self_follow'),
    )

    # Relationships
    follower = relationship('User', foreign_keys=[follower_id], back_populates='following')
    following = relationship('User', foreign_keys=[following_id], back_populates='followers')

    def __repr__(self):
        return f"<Follow(id='{self.id}', follower_id='{self.follower_id}', following_id='{self.following_id}')>"
