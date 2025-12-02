"""
AuditLog model for tracking all system activities.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class AuditLog(Base):
    """
    AuditLog model for tracking all user actions and system events.

    Provides a complete audit trail for compliance and debugging.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Actor information
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )

    # Action details
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed: create, update, delete, login, etc."
    )
    resource_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of resource affected: form, user, submission, etc."
    )
    resource_id = Column(
        Integer,
        nullable=True,
        comment="ID of the affected resource"
    )

    # Details
    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of the action"
    )
    changes = Column(
        JSON,
        nullable=True,
        comment="Detailed changes: before/after values"
    )

    # Request metadata
    ip_address = Column(String(45), nullable=True, comment="IPv4 or IPv6 address")
    user_agent = Column(String(500), nullable=True)

    # Tenant association
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource_type='{self.resource_type}')>"
