import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.extensions import db


class BaseModel(db.Model):
    """Abstract Base Model providing UUID primary key and timestamp fields."""

    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
