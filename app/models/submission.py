"""
Submission and SubmissionResponse models for form responses.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class SubmissionStatus(str, enum.Enum):
    """Submission status lifecycle"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Submission(Base):
    """
    Submission model representing a completed form response.
    """
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    # Form association
    form_id = Column(
        Integer,
        ForeignKey('forms.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Submitter information
    submitted_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who submitted the form"
    )
    submitted_by_email = Column(
        String(255),
        nullable=True,
        comment="Email of submitter (for anonymous submissions)"
    )
    submitted_by_name = Column(
        String(200),
        nullable=True,
        comment="Name of submitter (for anonymous submissions)"
    )

    # Status
    status = Column(
        SQLEnum(SubmissionStatus),
        default=SubmissionStatus.SUBMITTED,
        nullable=False,
        index=True
    )

    # Metadata
    submission_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional metadata: IP address, user agent, location, etc."
    )

    # Tenant association (for multi-tenancy)
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When submission was created/started"
    )
    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When submission was completed"
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    form = relationship("Form", back_populates="submissions")
    submitted_by_user = relationship("User", back_populates="created_submissions")
    responses = relationship(
        "SubmissionResponse",
        back_populates="submission",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Submission(id={self.id}, form_id={self.form_id}, status={self.status})>"


class SubmissionResponse(Base):
    """
    SubmissionResponse model representing an answer to a single form field.
    """
    __tablename__ = "submission_responses"

    id = Column(Integer, primary_key=True, index=True)

    # Submission association
    submission_id = Column(
        Integer,
        ForeignKey('submissions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Field association
    field_id = Column(
        Integer,
        ForeignKey('form_fields.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Response value (polymorphic based on field type)
    value_text = Column(Text, nullable=True, comment="Text/textarea/email/url responses")
    value_number = Column(Integer, nullable=True, comment="Number responses")
    value_boolean = Column(Boolean, nullable=True, comment="Checkbox responses")
    value_date = Column(DateTime(timezone=True), nullable=True, comment="Date/time responses")
    value_json = Column(
        JSON,
        nullable=True,
        comment="Multiple selections (checkbox) or complex data"
    )

    # File upload reference
    file_attachment_id = Column(
        Integer,
        ForeignKey('file_attachments.id', ondelete='SET NULL'),
        nullable=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    submission = relationship("Submission", back_populates="responses")
    field = relationship("FormField", back_populates="responses")
    file_attachment = relationship("FileAttachment")

    def __repr__(self):
        return f"<SubmissionResponse(id={self.id}, submission_id={self.submission_id}, field_id={self.field_id})>"
