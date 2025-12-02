"""
User, Role, and Permission models for authentication and RBAC.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)


# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email (used for login)"
    )
    hashed_password = Column(String(255), nullable=False)

    # Profile information
    full_name = Column(String(200), nullable=True)
    designation = Column(String(100), nullable=True, comment="Job title/position")
    phone = Column(String(20), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Platform administrator (not tenant-specific)"
    )
    email_verified = Column(Boolean, default=False, nullable=False)

    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True, comment="TOTP secret for MFA")

    # Tenant association
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_forms = relationship("Form", back_populates="created_by_user", foreign_keys="Form.created_by")
    created_submissions = relationship("Submission", back_populates="submitted_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tenant_id={self.tenant_id})>"


class Role(Base):
    """
    Role model for RBAC (Role-Based Access Control).

    Roles are tenant-specific. Each tenant can define their own roles.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(50),
        nullable=False,
        comment="Role name: admin, editor, viewer, approver, etc."
    )
    description = Column(Text, nullable=True)

    # Tenant association - roles are tenant-specific
    tenant_id = Column(
        Integer,
        ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # System roles (created by platform, not deletable)
    is_system_role = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="System-defined role that cannot be modified"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"


class Permission(Base):
    """
    Permission model for granular access control.

    Permissions are platform-wide (not tenant-specific).
    Format: resource.action (e.g., "forms.create", "forms.delete", "users.update")
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="Permission identifier: resource.action"
    )
    resource = Column(
        String(50),
        nullable=False,
        comment="Resource type: forms, users, submissions, etc."
    )
    action = Column(
        String(50),
        nullable=False,
        comment="Action: create, read, update, delete, approve, etc."
    )
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"
