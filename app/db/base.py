"""
Import all models here for Alembic to discover them.
This file must be imported in alembic/env.py for auto-generation of migrations.
"""
from app.db.session import Base

# Import all models so Alembic can discover them
from app.models.tenant import Tenant
from app.models.user import User, Role, Permission, user_roles, role_permissions
from app.models.form import Form, FormField
from app.models.submission import Submission, SubmissionResponse
from app.models.form_approval import FormApproval
from app.models.audit_log import AuditLog
from app.models.file_attachment import FileAttachment

__all__ = [
    "Base",
    "Tenant",
    "User",
    "Role",
    "Permission",
    "user_roles",
    "role_permissions",
    "Form",
    "FormField",
    "Submission",
    "SubmissionResponse",
    "FormApproval",
    "AuditLog",
    "FileAttachment",
]
