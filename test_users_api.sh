#!/bin/bash

echo "=== Testing User Management APIs ==="
echo ""

# Step 1: Create organization and get token
echo "1. Creating new organization..."
SIGNUP_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "UserTest Corp",
    "subdomain": "usertest2",
    "email": "admin@usertest2.com",
    "password": "TestPass123!",
    "full_name": "Admin User"
  }')

echo "$SIGNUP_RESPONSE" | python3 -m json.tool
echo ""

# Extract token
TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Access Token: ${TOKEN:0:50}..."
echo ""

# Step 2: List users (should show only admin)
echo "2. Listing users in tenant..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 3: Invite a new user
echo "3. Inviting a new user..."
INVITE_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@usertest2.com",
    "full_name": "John Doe",
    "designation": "Software Engineer",
    "phone": "+1234567890"
  }')

echo "$INVITE_RESPONSE" | python3 -m json.tool
echo ""

# Extract user ID
USER_ID=$(echo "$INVITE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])")
echo "Created User ID: $USER_ID"
echo ""

# Step 4: Get specific user
echo "4. Getting user details..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 5: Update user
echo "5. Updating user..."
curl -s -X PUT "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "designation": "Senior Software Engineer"
  }' | python3 -m json.tool
echo ""

# Step 6: List users again (should show 2 users)
echo "6. Listing users again..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 7: Search users
echo "7. Searching for 'john'..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users?search=john" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Step 8: Try to invite a 3rd user (should fail - FREE plan limit)
echo "8. Trying to invite 3rd user (should fail due to FREE plan limit)..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/users/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@usertest2.com",
    "full_name": "Jane Smith"
  }' | python3 -m json.tool
echo ""

# Step 9: Delete user
echo "9. Deleting user (soft delete)..."
curl -s -X DELETE "http://127.0.0.1:8000/api/v1/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN"
echo "User deleted (soft delete)"
echo ""

# Step 10: List users after deletion
echo "10. Listing users after deletion..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== User Management API Tests Complete ==="
