#!/bin/bash

echo "=== Testing User Management APIs with PRO Plan ==="
echo ""

# Step 1: Create organization
echo "1. Creating new organization..."
SIGNUP_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "UserTestPro Corp",
    "subdomain": "usertestpro",
    "email": "admin@usertestpro.com",
    "password": "TestPass123!",
    "full_name": "Admin User"
  }')

TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
TENANT_ID=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['tenant']['id'])")

echo "Tenant ID: $TENANT_ID"
echo "Token obtained"
echo ""

# Step 2: Manually upgrade to PRO plan (simulating payment)
echo "2. Upgrading tenant to PRO plan (via SQL)..."
./venv/bin/python3 -c "
import asyncio
from app.db.session import async_session_maker
from app.models.tenant import Tenant, PlanType
from sqlalchemy import select

async def upgrade():
    async with async_session_maker() as db:
        result = await db.execute(select(Tenant).where(Tenant.id == $TENANT_ID))
        tenant = result.scalar_one()
        tenant.plan = PlanType.PRO
        tenant.max_users = 10
        tenant.max_forms = 30
        await db.commit()
        print(f'Upgraded tenant {tenant.name} to PRO plan')

asyncio.run(upgrade())
"
echo ""

# Step 3: Invite first user
echo "3. Inviting first user..."
INVITE_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@usertestpro.com",
    "full_name": "John Doe",
    "designation": "Software Engineer",
    "phone": "+1234567890"
  }')

echo "$INVITE_RESPONSE" | python3 -m json.tool | head -30
echo ""

USER_ID=$(echo "$INVITE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])")
TEMP_PASSWORD=$(echo "$INVITE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['temporary_password'])")

echo "Created User ID: $USER_ID"
echo "Temporary Password: $TEMP_PASSWORD"
echo ""

# Step 4: Get user details
echo "4. Getting user details..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 5: Update user
echo "5. Updating user designation..."
curl -s -X PUT "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "designation": "Senior Software Engineer",
    "phone": "+1987654321"
  }' | python3 -m json.tool
echo ""

# Step 6: List all users
echo "6. Listing all users..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -50
echo ""

# Step 7: Search for user
echo "7. Searching for 'doe'..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users?search=doe" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
echo ""

# Step 8: Invite second user
echo "8. Inviting second user..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@usertestpro.com",
    "full_name": "Jane Smith",
    "designation": "Product Manager"
  }' | python3 -m json.tool | head -20
echo ""

# Step 9: Delete first user
echo "9. Soft deleting first user..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "HTTP Status: $HTTP_CODE (204 = success)"
echo ""

# Step 10: Verify user is inactive
echo "10. Verifying user is soft deleted..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 11: List active users (should show admin and jane, john should be is_active=false)
echo "11. Final user list..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -60
echo ""

echo "=== User Management API Tests with PRO Plan Complete ==="
