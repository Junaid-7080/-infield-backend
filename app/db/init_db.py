"""
Database initialization - auto-create tables and seed data.
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.models.user import Permission, Role, User
from app.models.tenant import Tenant
from app.core.security import get_password_hash


async def create_tables():
    """
    Create all database tables if they don't exist.
    Uses SQLAlchemy metadata to create tables from model definitions.
    """
    print("🔍 Checking database tables...")

    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables ready")


async def check_if_db_empty(db: AsyncSession) -> bool:
    """
    Check if database is empty (no tenants exist).

    Args:
        db: Database session

    Returns:
        True if database is empty, False otherwise
    """
    result = await db.execute(text("SELECT COUNT(*) FROM tenants"))
    count = result.scalar()
    return count == 0


async def seed_initial_data():
    """
    Seed database with initial data if it's empty.
    Creates permissions, demo tenant, roles, and users.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Check if database already has data
            if not await check_if_db_empty(db):
                print("📊 Database already contains data, skipping seed")
                return

            print("🌱 Seeding initial data...")

            # 1. Create permissions (platform-wide)
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
            print(f"  ✓ Created {len(permissions)} permissions")

            # 2. Create demo tenant
            tenant = Tenant(
                name="Demo Organization",
                subdomain="demo",
                contact_email="admin@demo.com",
                plan="pro",
                max_users=50,
                max_forms=100,
                is_active=True
            )
            db.add(tenant)
            await db.flush()
            print(f"  ✓ Created tenant: {tenant.name} ({tenant.subdomain})")

            # 3. Create roles for demo tenant
            # Admin role - all permissions
            admin_role = Role(
                name="Admin",
                description="Full access to all features",
                tenant_id=tenant.id,
                is_system_role=True
            )
            admin_role.permissions = permissions
            db.add(admin_role)

            # Editor role - can create and edit forms
            editor_role = Role(
                name="Editor",
                description="Can create and edit forms",
                tenant_id=tenant.id,
                is_system_role=True
            )
            editor_perms = [p for p in permissions if p.resource in ["forms", "submissions"] and p.action in ["create", "read", "update"]]
            editor_role.permissions = editor_perms
            db.add(editor_role)

            # Viewer role - read-only access
            viewer_role = Role(
                name="Viewer",
                description="Read-only access",
                tenant_id=tenant.id,
                is_system_role=True
            )
            viewer_perms = [p for p in permissions if p.action == "read"]
            viewer_role.permissions = viewer_perms
            db.add(viewer_role)

            # Approver role - can approve/reject submissions
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
            print(f"  ✓ Created 4 roles: Admin, Editor, Viewer, Approver")

            # 4. Create demo users
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
            print(f"  ✓ Created 3 demo users")

            # Commit all changes
            await db.commit()

            print("\n✅ Database seeded successfully!")
            print("\n📝 Demo login credentials:")
            print("   Email: admin@demo.com")
            print("   Password: admin123")
            print("\n   Email: editor@demo.com")
            print("   Password: editor123")
            print("\n   Email: viewer@demo.com")
            print("   Password: viewer123")

        except Exception as e:
            print(f"\n❌ Error seeding database: {e}")
            await db.rollback()
            raise


async def init_db():
    """
    Initialize database: create tables and seed initial data.
    Called on application startup.
    """
    try:
        # Create tables
        await create_tables()

        # Seed initial data if database is empty
        await seed_initial_data()

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# For standalone execution
if __name__ == "__main__":
    asyncio.run(init_db())
