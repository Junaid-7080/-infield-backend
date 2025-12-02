"""
Tenant context middleware for multi-tenancy support.
"""
from contextvars import ContextVar
from typing import Optional

# Context variable to store current tenant ID for the request
tenant_context: ContextVar[Optional[int]] = ContextVar('tenant_id', default=None)


def get_current_tenant_id() -> Optional[int]:
    """
    Get the current tenant ID from context.

    Returns:
        Current tenant ID or None
    """
    return tenant_context.get()


def set_current_tenant_id(tenant_id: int) -> None:
    """
    Set the current tenant ID in context.

    Args:
        tenant_id: Tenant ID to set
    """
    tenant_context.set(tenant_id)


def clear_current_tenant_id() -> None:
    """Clear the current tenant ID from context."""
    tenant_context.set(None)
