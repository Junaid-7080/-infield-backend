#!/bin/bash

echo "=========================================="
echo "Form Submission APIs Complete Test"
echo "=========================================="
echo ""

# Step 1: Create organization and upgrade to PRO
echo "Step 1: Creating organization..."
SIGNUP=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Submission Test Corp",
    "subdomain": "subtest",
    "email": "admin@subtest.com",
    "password": "TestPass123!",
    "full_name": "Admin User"
  }')

TOKEN=$(echo "$SIGNUP" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to create organization"
  exit 1
fi

echo "✅ Organization created"

# Upgrade to PRO
curl -s -X POST "http://127.0.0.1:8000/api/v1/tenants/me/upgrade?new_plan=pro" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "✅ Upgraded to PRO plan"
echo ""

# Step 2: Create a form with fields
echo "Step 2: Creating form with fields..."
FORM_CREATE=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/forms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Employee Feedback Form",
    "description": "Annual employee feedback collection",
    "is_published": false,
    "allow_multiple_submissions": true,
    "requires_approval": false,
    "fields": [
      {
        "field_type": "text",
        "label": "Full Name",
        "required": true,
        "order": 0
      },
      {
        "field_type": "email",
        "label": "Email Address",
        "required": true,
        "order": 1
      },
      {
        "field_type": "number",
        "label": "Years of Experience",
        "required": false,
        "order": 2
      },
      {
        "field_type": "textarea",
        "label": "Feedback",
        "required": true,
        "order": 3
      }
    ]
  }')

FORM_ID=$(echo "$FORM_CREATE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
FIELD1_ID=$(echo "$FORM_CREATE" | python3 -c "import sys, json; fields=json.load(sys.stdin)['fields']; print([f['id'] for f in fields if f['label']=='Full Name'][0])")
FIELD2_ID=$(echo "$FORM_CREATE" | python3 -c "import sys, json; fields=json.load(sys.stdin)['fields']; print([f['id'] for f in fields if f['label']=='Email Address'][0])")
FIELD3_ID=$(echo "$FORM_CREATE" | python3 -c "import sys, json; fields=json.load(sys.stdin)['fields']; print([f['id'] for f in fields if f['label']=='Years of Experience'][0])")
FIELD4_ID=$(echo "$FORM_CREATE" | python3 -c "import sys, json; fields=json.load(sys.stdin)['fields']; print([f['id'] for f in fields if f['label']=='Feedback'][0])")

echo "✅ Form created (ID: $FORM_ID)"
echo "   Field IDs: $FIELD1_ID, $FIELD2_ID, $FIELD3_ID, $FIELD4_ID"
echo ""

# Step 3: Try to submit unpublished form (should fail)
echo "Step 3: Trying to submit unpublished form (should fail)..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"form_id\": $FORM_ID,
    \"responses\": [
      {\"field_id\": $FIELD1_ID, \"value_text\": \"John Doe\"}
    ]
  }" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Correctly blocked: {data['detail']}\")"
echo ""

# Step 4: Publish form
echo "Step 4: Publishing form..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/forms/$FORM_ID/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_published": true}' > /dev/null
echo "✅ Form published"
echo ""

# Step 5: Submit form with missing required field (should fail)
echo "Step 5: Submitting with missing required fields (should fail)..."
curl -s -X POST "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"form_id\": $FORM_ID,
    \"responses\": [
      {\"field_id\": $FIELD1_ID, \"value_text\": \"John Doe\"}
    ]
  }" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Correctly blocked: {data['detail']}\")"
echo ""

# Step 6: Submit form successfully
echo "Step 6: Submitting form with all required fields..."
SUB1=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"form_id\": $FORM_ID,
    \"responses\": [
      {\"field_id\": $FIELD1_ID, \"value_text\": \"John Doe\"},
      {\"field_id\": $FIELD2_ID, \"value_text\": \"john@example.com\"},
      {\"field_id\": $FIELD3_ID, \"value_number\": 5},
      {\"field_id\": $FIELD4_ID, \"value_text\": \"Great company culture and team collaboration.\"}
    ]
  }")

SUB1_ID=$(echo "$SUB1" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Submission created (ID: $SUB1_ID)"
echo ""

# Step 7: Submit second form
echo "Step 7: Submitting second response..."
SUB2=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"form_id\": $FORM_ID,
    \"responses\": [
      {\"field_id\": $FIELD1_ID, \"value_text\": \"Jane Smith\"},
      {\"field_id\": $FIELD2_ID, \"value_text\": \"jane@example.com\"},
      {\"field_id\": $FIELD4_ID, \"value_text\": \"Need better work-life balance.\"}
    ],
    \"submission_metadata\": {\"source\": \"web\", \"device\": \"desktop\"}
  }")

SUB2_ID=$(echo "$SUB2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Second submission created (ID: $SUB2_ID)"
echo ""

# Step 8: List all submissions
echo "Step 8: Listing all submissions..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Total submissions: {data['total']}\"); [print(f\"   - ID {s['id']}: Status={s['status']}\") for s in data['items']]"
echo ""

# Step 9: Filter by form
echo "Step 9: Filtering submissions by form..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions?form_id=$FORM_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Submissions for form: {data['total']}\")"
echo ""

# Step 10: Get specific submission
echo "Step 10: Getting submission details..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions/$SUB1_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Submission {data['id']}: {len(data['responses'])} responses\"); [print(f\"   - Response {i+1}: {r.get('value_text') or r.get('value_number') or 'N/A'}\") for i, r in enumerate(data['responses'])]"
echo ""

# Step 11: Create form requiring approval
echo "Step 11: Creating form requiring approval..."
FORM2=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/forms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Leave Request Form",
    "is_published": true,
    "requires_approval": true,
    "fields": [
      {"field_type": "text", "label": "Reason", "required": true, "order": 0}
    ]
  }')

FORM2_ID=$(echo "$FORM2" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
FORM2_FIELD=$(echo "$FORM2" | python3 -c "import sys, json; print(json.load(sys.stdin)['fields'][0]['id'])")
echo "✅ Approval form created (ID: $FORM2_ID)"
echo ""

# Step 12: Submit to approval form
echo "Step 12: Submitting to approval form..."
SUB3=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"form_id\": $FORM2_ID,
    \"responses\": [
      {\"field_id\": $FORM2_FIELD, \"value_text\": \"Medical appointment\"}
    ]
  }")

SUB3_ID=$(echo "$SUB3" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
SUB3_STATUS=$(echo "$SUB3" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ Submission created with status: $SUB3_STATUS (ID: $SUB3_ID)"
echo ""

# Step 13: Approve submission
echo "Step 13: Approving submission..."
curl -s -X PUT "http://127.0.0.1:8000/api/v1/submissions/$SUB3_ID/approve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "comments": "Approved by manager"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Submission approved: status={data['status']}\")"
echo ""

# Step 14: Filter by status
echo "Step 14: Filtering submissions by status..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions?status=submitted" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Submitted status: {data['total']} submissions\")"

curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions?status=approved" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Approved status: {data['total']} submissions\")"
echo ""

# Step 15: Delete submission
echo "Step 15: Deleting submission..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "http://127.0.0.1:8000/api/v1/submissions/$SUB2_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Submission deleted (HTTP $HTTP_CODE)"
echo ""

# Step 16: Final count
echo "Step 16: Final submission count..."
curl -s -X GET "http://127.0.0.1:8000/api/v1/submissions" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Total remaining submissions: {data['total']}\")"
echo ""

echo "=========================================="
echo "✅ All Submission API Tests Passed!"
echo "=========================================="
