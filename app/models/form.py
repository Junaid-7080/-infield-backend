"""
Form and FormField models.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class FieldType(str, enum.Enum):
    """Supported form field types"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    DATE = "date"
    TIME = "time"
    TABLE = "table"
    SIGNATURE = "signature"
    SECTION = "section"


class Form(Base):
    """
    Form model representing a form template/definition.
    """
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="Form title")
    description = Column(Text, nullable=True, comment="Form description")

    # Form header/letterhead (stored as JSON)
    header = Column(
        JSON,
        nullable=True,
        comment="Form header configuration: logo, org name, address, etc."
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_published = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether form is published and available for submissions"
    )

    # Tenant and creator
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    created_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # Version control (future enhancement)
    version = Column(Integer, default=1, nullable=False)

    # Settings
    allow_multiple_submissions = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Allow users to submit multiple times"
    )
    requires_approval = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether submissions require approval"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="forms")
    created_by_user = relationship("User", back_populates="created_forms", foreign_keys=[created_by])
    fields = relationship(
        "FormField",
        back_populates="form",
        cascade="all, delete-orphan",
        order_by="FormField.order"
    )
    submissions = relationship("Submission", back_populates="form", cascade="all, delete-orphan")
    approvals = relationship("FormApproval", back_populates="form", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Form(id={self.id}, title='{self.title}', tenant_id={self.tenant_id})>"


class FormField(Base):
    """
    FormField model representing individual fields within a form.
    """
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)

    # Form association
    form_id = Column(
        Integer,
        ForeignKey('forms.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Field configuration
    field_type = Column(SQLEnum(FieldType), nullable=False)
    label = Column(String(200), nullable=False, comment="Field label displayed to user")
    placeholder = Column(String(200), nullable=True, comment="Placeholder text")
    help_text = Column(Text, nullable=True, comment="Helper text/description")

    # Validation
    required = Column(Boolean, default=False, nullable=False)

    # Options for select/radio/checkbox fields (stored as JSON array)
    options = Column(
        JSON,
        nullable=True,
        comment="Options for select/radio/checkbox: ['Option 1', 'Option 2']"
    )

    # Field order
    order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Display order in form"
    )

    # Additional validation rules (future enhancement)
    validation_rules = Column(
        JSON,
        nullable=True,
        comment="Custom validation rules: min, max, pattern, etc."
    )

    # Field configuration for complex field types
    field_config = Column(
        JSON,
        nullable=True,
        comment="Configuration for complex field types (table, signature, section)"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    form = relationship("Form", back_populates="fields")
    responses = relationship("SubmissionResponse", back_populates="field")

    def __repr__(self):
        return f"<FormField(id={self.id}, form_id={self.form_id}, label='{self.label}', type={self.field_type})>"
