from sqlalchemy import Column, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Block(BaseModel):
    """Block Model representing blocked relationships between users."""

    __tablename__ = 'blocks'

    blocker_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    blocked_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='uq_blocker_blocked'),
        CheckConstraint('blocker_id != blocked_id', name='ck_prevent_self_block'),
    )

    # Relationships
    blocker = relationship('User', foreign_keys=[blocker_id])
    blocked = relationship('User', foreign_keys=[blocked_id])

    def __repr__(self):
        return f"<Block(id='{self.id}', blocker_id='{self.blocker_id}', blocked_id='{self.blocked_id}')>"
