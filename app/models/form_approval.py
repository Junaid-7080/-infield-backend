"""
FormApproval model for approval workflows.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class ApprovalStatus(str, enum.Enum):
    """Approval status for forms"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class FormApproval(Base):
    """
    FormApproval model for tracking form approval workflows.

    Represents the assignment and approval process for forms.
    """
    __tablename__ = "form_approvals"

    id = Column(Integer, primary_key=True, index=True)

    # Form association
    form_id = Column(
        Integer,
        ForeignKey('forms.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Assignment details
    assigned_to = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who should review/approve"
    )
    assigned_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="User who assigned the review"
    )

    # Status
    status = Column(
        SQLEnum(ApprovalStatus),
        default=ApprovalStatus.PENDING,
        nullable=False,
        index=True
    )

    # Comments/notes
    comments = Column(
        Text,
        nullable=True,
        comment="Approval/rejection notes from reviewer"
    )

    # Tenant association
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Timestamps
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When form was assigned for review"
    )
    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When reviewer made decision"
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    form = relationship("Form", back_populates="approvals")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return f"<FormApproval(id={self.id}, form_id={self.form_id}, status={self.status})>"
