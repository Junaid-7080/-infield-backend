"""
Database initialization script.
Creates initial tenants, users, roles, and permissions for development.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash


async def create_permissions(db: AsyncSession):
    """Create default permissions."""
    permissions_data = [
        # Forms
        {"name": "forms.create", "resource": "forms", "action": "create", "description": "Create new forms"},
        {"name": "forms.read", "resource": "forms", "action": "read", "description": "View forms"},
        {"name": "forms.update", "resource": "forms", "action": "update", "description": "Edit forms"},
        {"name": "forms.delete", "resource": "forms", "action": "delete", "description": "Delete forms"},
        {"name": "forms.assign", "resource": "forms", "action": "assign", "description": "Assign forms for approval"},

        # Submissions
        {"name": "submissions.create", "resource": "submissions", "action": "create", "description": "Submit forms"},
        {"name": "submissions.read", "resource": "submissions", "action": "read", "description": "View submissions"},
        {"name": "submissions.approve", "resource": "submissions", "action": "approve", "description": "Approve submissions"},
        {"name": "submissions.reject", "resource": "submissions", "action": "reject", "description": "Reject submissions"},

        # Users
        {"name": "users.create", "resource": "users", "action": "create", "description": "Create users"},
        {"name": "users.read", "resource": "users", "action": "read", "description": "View users"},
        {"name": "users.update", "resource": "users", "action": "update", "description": "Edit users"},
        {"name": "users.delete", "resource": "users", "action": "delete", "description": "Delete users"},

        # Roles
        {"name": "roles.create", "resource": "roles", "action": "create", "description": "Create roles"},
        {"name": "roles.read", "resource": "roles", "action": "read", "description": "View roles"},
        {"name": "roles.update", "resource": "roles", "action": "update", "description": "Edit roles"},
        {"name": "roles.delete", "resource": "roles", "action": "delete", "description": "Delete roles"},
    ]

    permissions = []
    for perm_data in permissions_data:
        perm = Permission(**perm_data)
        db.add(perm)
        permissions.append(perm)

    await db.flush()
    print(f"✓ Created {len(permissions)} permissions")
    return permissions


async def create_demo_tenant(db: AsyncSession, permissions: list[Permission]):
    """Create a demo tenant with users and roles."""
    # Create tenant
    tenant = Tenant(
        name="Demo Organization",
        subdomain="demo",
        contact_email="admin@demo.com",
        plan="pro",
        max_users=50,
        max_forms=100
    )
    db.add(tenant)
    await db.flush()
    print(f"✓ Created tenant: {tenant.name} ({tenant.subdomain})")

    # Create roles
    admin_role = Role(
        name="Admin",
        description="Full access to all features",
        tenant_id=tenant.id,
        is_system_role=True
    )
    admin_role.permissions = permissions  # Admin gets all permissions
    db.add(admin_role)

    editor_role = Role(
        name="Editor",
        description="Can create and edit forms",
        tenant_id=tenant.id,
        is_system_role=True
    )
    editor_perms = [p for p in permissions if p.resource in ["forms", "submissions"] and p.action in ["create", "read", "update"]]
    editor_role.permissions = editor_perms
    db.add(editor_role)

    viewer_role = Role(
        name="Viewer",
        description="Read-only access",
        tenant_id=tenant.id,
        is_system_role=True
    )
    viewer_perms = [p for p in permissions if p.action == "read"]
    viewer_role.permissions = viewer_perms
    db.add(viewer_role)

    approver_role = Role(
        name="Approver",
        description="Can approve/reject submissions",
        tenant_id=tenant.id,
        is_system_role=True
    )
    approver_perms = [p for p in permissions if p.resource == "submissions"]
    approver_role.permissions = approver_perms
    db.add(approver_role)

    await db.flush()
    print(f"✓ Created 4 roles: Admin, Editor, Viewer, Approver")

    # Create users
    admin_user = User(
        email="admin@demo.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        designation="Administrator",
        tenant_id=tenant.id,
        is_active=True,
        email_verified=True
    )
    admin_user.roles = [admin_role]
    db.add(admin_user)

    editor_user = User(
        email="editor@demo.com",
        hashed_password=get_password_hash("editor123"),
        full_name="Editor User",
        designation="Form Designer",
        tenant_id=tenant.id,
        is_active=True,
        email_verified=True
    )
    editor_user.roles = [editor_role]
    db.add(editor_user)

    viewer_user = User(
        email="viewer@demo.com",
        hashed_password=get_password_hash("viewer123"),
        full_name="Viewer User",
        designation="Analyst",
        tenant_id=tenant.id,
        is_active=True,
        email_verified=True
    )
    viewer_user.roles = [viewer_role]
    db.add(viewer_user)

    await db.flush()
    print(f"✓ Created 3 users")
    print("  - admin@demo.com / admin123 (Admin)")
    print("  - editor@demo.com / editor123 (Editor)")
    print("  - viewer@demo.com / viewer123 (Viewer)")

    return tenant


async def init_database():
    """Initialize database with seed data."""
    print("Initializing database with seed data...\n")

    async with AsyncSessionLocal() as db:
        try:
            # Create permissions (platform-wide)
            permissions = await create_permissions(db)

            # Create demo tenant
            tenant = await create_demo_tenant(db, permissions)

            # Commit all changes
            await db.commit()

            print("\n✅ Database initialization complete!")
            print("\nYou can now login with:")
            print("  Email: admin@demo.com")
            print("  Password: admin123")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(init_database())
