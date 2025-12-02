"""
Tenant model for multi-tenancy support.
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class PlanType(str, PyEnum):
    """Subscription plan types for tenants."""
    FREE = "free"
    PRO = "pro"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """
    Tenant/Organization model for SaaS multi-tenancy.

    Each tenant represents a separate organization using the platform.
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="Organization name")
    subdomain = Column(
        String(63),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique subdomain for tenant"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether tenant account is active"
    )

    # Additional tenant metadata
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Subscription/billing
    plan = Column(
        Enum(PlanType),
        default=PlanType.FREE,
        nullable=False,
        comment="Subscription plan tier"
    )
    max_users = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Maximum number of users allowed"
    )
    max_forms = Column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum number of forms allowed"
    )

    # Trial management
    trial_started_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When trial period started"
    )
    trial_ends_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When trial period ends"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', subdomain='{self.subdomain}')>"

    def is_trial_active(self) -> bool:
        """Check if trial period is still active."""
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() < self.trial_ends_at.replace(tzinfo=None)

    def is_within_user_limit(self, current_user_count: int) -> bool:
        """Check if tenant is within user limit."""
        return current_user_count < self.max_users

    def is_within_form_limit(self, current_form_count: int) -> bool:
        """Check if tenant is within form limit."""
        return current_form_count < self.max_forms

    @classmethod
    def get_plan_limits(cls, plan: PlanType) -> dict:
        """
        Get user and form limits for a given plan.

        Args:
            plan: Plan type

        Returns:
            Dictionary with max_users and max_forms
        """
        limits = {
            PlanType.FREE: {"max_users": 1, "max_forms": 3},
            PlanType.PRO: {"max_users": 10, "max_forms": 30},
            PlanType.ADVANCED: {"max_users": 100, "max_forms": 300},
            PlanType.ENTERPRISE: {"max_users": 999999, "max_forms": 999999}  # "Unlimited"
        }
        return limits.get(plan, limits[PlanType.FREE])
