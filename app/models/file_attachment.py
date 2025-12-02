"""
FileAttachment model for uploaded files.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from app.db.session import Base


class FileAttachment(Base):
    """
    FileAttachment model for managing uploaded files.
    """
    __tablename__ = "file_attachments"

    id = Column(Integer, primary_key=True, index=True)

    # File information
    original_filename = Column(
        String(255),
        nullable=False,
        comment="Original filename from upload"
    )
    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Unique filename on server/storage"
    )
    file_path = Column(
        String(500),
        nullable=False,
        comment="Full path to file in storage"
    )
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of file"
    )

    # Uploader information
    uploaded_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # Tenant association
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Timestamps
    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<FileAttachment(id={self.id}, filename='{self.original_filename}')>"
