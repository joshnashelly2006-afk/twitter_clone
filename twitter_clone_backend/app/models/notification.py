from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    """Notification Model representing real-time system notifications."""

    __tablename__ = 'notifications'

    recipient_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    type = Column(String(20), nullable=False)  # 'LIKE', 'COMMENT', 'FOLLOW', 'MENTION'
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    is_read = Column(Boolean, default=False, nullable=False)

    # Relationships
    recipient = relationship('User', foreign_keys=[recipient_id])
    sender = relationship('User', foreign_keys=[sender_id])
    post = relationship('Post')

    def __repr__(self):
        return f"<Notification(id='{self.id}', recipient_id='{self.recipient_id}', type='{self.type}')>"
