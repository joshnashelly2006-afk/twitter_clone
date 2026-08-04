from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Report(BaseModel):
    """Report Model representing user and post content moderation reports."""

    __tablename__ = 'reports'

    reporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    reported_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    reported_post_id = Column(
        UUID(as_uuid=True),
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    reason = Column(String(50), nullable=False)  # 'SPAM', 'ABUSE', 'HARASSMENT', 'VIOLENCE', 'OTHER'
    details = Column(Text, nullable=True)
    status = Column(String(20), default='PENDING', nullable=False)  # 'PENDING', 'RESOLVED', 'DISMISSED'

    # Relationships
    reporter = relationship('User', foreign_keys=[reporter_id])
    reported_user = relationship('User', foreign_keys=[reported_user_id])
    reported_post = relationship('Post', foreign_keys=[reported_post_id])

    def __repr__(self):
        return f"<Report(id='{self.id}', reason='{self.reason}', status='{self.status}')>"
