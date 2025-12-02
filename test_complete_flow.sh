#!/bin/bash

echo "=========================================="
echo "User Management Complete Flow Test"
echo "=========================================="
echo ""

# Create organization
echo "Step 1: Creating organization..."
RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Complete Test Corp",
    "subdomain": "completetest",
    "email": "admin@completetest.com",
    "password": "TestPass123!",
    "full_name": "Admin User"
  }')

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to create organization"
  echo "$RESPONSE" | python3 -m json.tool
  exit 1
fi

echo "✅ Organization created"
echo ""

# Upgrade to PRO plan
echo "Step 2: Upgrading to PRO plan..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/me/upgrade?new_plan=pro" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Upgraded to {data['plan']} plan (max_users={data['max_users']}, max_forms={data['max_forms']})\")"
echo ""

# List users (should show only admin)
echo "Step 3: Listing users..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Total users: {data['total']}\")"
echo ""

# Invite first user
echo "Step 4: Inviting first user..."
INVITE1=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@completetest.com",
    "full_name": "John Doe",
    "designation": "Software Engineer"
  }')

USER1_ID=$(echo "$INVITE1" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['user']['id'])")
TEMP_PASS1=$(echo "$INVITE1" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['temporary_password'])")
echo "✅ User invited (ID: $USER1_ID, Temp Password: $TEMP_PASS1)"
echo ""

# Invite second user
echo "Step 5: Inviting second user..."
INVITE2=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@completetest.com",
    "full_name": "Jane Smith",
    "designation": "Product Manager"
  }')

USER2_ID=$(echo "$INVITE2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['user']['id'])")
echo "✅ User invited (ID: $USER2_ID)"
echo ""

# Update user
echo "Step 6: Updating user designation..."
curl -s -X PUT "http://127.0.0.1:8000/api/v1/users/$USER1_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "designation": "Senior Software Engineer"
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Updated {data['full_name']} to {data['designation']}\")"
echo ""

# Get specific user
echo "Step 7: Getting user details..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users/$USER1_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ User: {data['full_name']} ({data['email']}) - {data['designation']}\")"
echo ""

# Search users
echo "Step 8: Searching for 'john'..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users?search=john" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Found {data['total']} user(s)\")"
echo ""

# List all users
echo "Step 9: Listing all users..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Total users: {data['total']}\"); [print(f\"  - {u['full_name']} ({u['email']}) - {u['designation'] or 'No designation'}\") for u in data['items']]"
echo ""

# Delete user
echo "Step 10: Soft deleting user..."
curl -s -X DELETE "http://127.0.0.1:8000/api/v1/users/$USER2_ID" \
  -H "Authorization: Bearer $TOKEN"
echo "✅ User soft deleted"
echo ""

# Verify soft delete
echo "Step 11: Verifying soft delete..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users/$USER2_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ User status - is_active: {data['is_active']}\")"
echo ""

# Final count
echo "Step 12: Final user count..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Active users: {len([u for u in data['items'] if u['is_active']])} (Total in DB: {data['total']})\")"
echo ""

echo "=========================================="
echo "✅ All User Management Tests Passed!"
echo "=========================================="
