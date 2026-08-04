from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserSettings(BaseModel):
    """UserSettings Model storing user preferences and privacy settings."""

    __tablename__ = 'user_settings'

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True
    )
    dark_mode = Column(Boolean, default=False, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    language = Column(String(10), default='en', nullable=False)

    # Relationships
    user = relationship('User')

    def __repr__(self):
        return f"<UserSettings(user_id='{self.user_id}', dark_mode={self.dark_mode}, language='{self.language}')>"
