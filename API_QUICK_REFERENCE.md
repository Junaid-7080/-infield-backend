# API Quick Reference Guide

**Base URL:** `http://localhost:8000/api/v1`

---

## Authentication

```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
Authorization: Bearer <your_token>
```

---

## Forms API - Quick Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/forms` | Create form | Required |
| GET | `/forms` | List forms | Required |
| GET | `/forms/{id}` | Get form | Required |
| PUT | `/forms/{id}` | Update form | Required |
| DELETE | `/forms/{id}` | Delete form | Required |
| POST | `/forms/{id}/publish` | Publish/unpublish | Required |
| POST | `/forms/{id}/fields` | Add field | Required |

---

## Submissions API - Quick Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/submissions` | Submit form | Optional |
| GET | `/submissions` | List submissions | Required |
| GET | `/submissions/{id}` | Get submission | Required |
| GET | `/submissions/form/{id}` | Get form submissions | Required |
| PUT | `/submissions/{id}/approve` | Approve/reject | Required (Admin) |
| DELETE | `/submissions/{id}` | Delete submission | Required (Admin) |

---

## Field Types Cheat Sheet

### Basic Fields
```json
{
  "field_type": "text",      // value_text
  "field_type": "textarea",  // value_text
  "field_type": "number",    // value_number
  "field_type": "email",     // value_text
  "field_type": "url",       // value_text
  "field_type": "phone",     // value_text
  "field_type": "date",      // value_date
  "field_type": "time",      // value_text
  "field_type": "checkbox",  // value_boolean
  "field_type": "select",    // value_text
  "field_type": "radio",     // value_text
  "field_type": "file"       // file_attachment_id
}
```

### Table Field
```json
{
  "field_type": "table",
  "field_config": {
    "columns": [
      {"id": "col1", "label": "Column 1", "type": "text", "required": true}
    ],
    "minRows": 1,
    "maxRows": 50,
    "showRowNumbers": true
  }
}

// Submit:
{
  "field_id": 1,
  "value_json": [
    {"col1": "value1"},
    {"col1": "value2"}
  ]
}
```

### Signature Field
```json
{
  "field_type": "signature",
  "field_config": {
    "width": 400,
    "height": 200,
    "penColor": "#000000",
    "backgroundColor": "#ffffff"
  }
}

// Submit:
{
  "field_id": 2,
  "value_text": "data:image/png;base64,iVBORw0..."
}
// Returns: file_attachment_id
```

### Section Field
```json
{
  "field_type": "section",
  "field_config": {
    "collapsible": true,
    "defaultExpanded": false
  }
}
// No submission value needed
```

---

## Common Request Examples

### Create Form with Table and Signature
```bash
curl -X POST http://localhost:8000/api/v1/forms \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Inspection Form",
    "fields": [
      {
        "field_type": "table",
        "label": "Equipment",
        "required": true,
        "order": 0,
        "field_config": {
          "columns": [
            {"id": "item", "label": "Item", "type": "text", "required": true},
            {"id": "status", "label": "Status", "type": "select", "required": true, "options": ["Good", "Bad"]}
          ],
          "minRows": 1,
          "maxRows": 20
        }
      },
      {
        "field_type": "signature",
        "label": "Signature",
        "required": true,
        "order": 1,
        "field_config": {
          "width": 400,
          "height": 200
        }
      }
    ],
    "is_published": true
  }'
```

### Submit Form
```bash
curl -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "form_id": 1,
    "responses": [
      {
        "field_id": 1,
        "value_json": [
          {"item": "Item 1", "status": "Good"},
          {"item": "Item 2", "status": "Bad"}
        ]
      },
      {
        "field_id": 2,
        "value_text": "data:image/png;base64,iVBORw0..."
      }
    ],
    "submitted_by_email": "user@example.com",
    "submitted_by_name": "John Doe"
  }'
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Delete success) |
| 400 | Bad Request (Validation failed) |
| 401 | Unauthorized (Missing/invalid token) |
| 403 | Forbidden (Insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (Schema error) |
| 429 | Too Many Requests (Rate limited) |
| 500 | Internal Server Error |

---

## Common Validation Errors

### Table Field
- "Table field 'X' expects an array of rows, got dict"
- "Table field 'X' requires minimum 3 rows, got 1"
- "Required column 'Y' is missing or empty in row 2"

### Signature Field
- "Invalid base64 signature data"
- "Signature size (6.5MB) exceeds maximum allowed size (5.0MB)"
- "Invalid image data: cannot identify image file"

### Form
- "Form is not published and cannot accept submissions"
- "Required field 'X' (ID: Y) is missing"
- "You have already submitted this form. Multiple submissions are not allowed."

---

## Response Field Mapping

| Frontend | Backend | Type |
|----------|---------|------|
| `id` | `id` | string → int |
| `name` | `title` | string |
| `tableConfig` | `field_config` | object |
| `signatureConfig` | `field_config` | object |
| `sectionConfig` | `field_config` | object |

---

## Integration Checklist

Frontend needs:
- [ ] HTTP client (axios/fetch)
- [ ] API base URL configuration
- [ ] JWT token storage and handling
- [ ] Request interceptor (add auth header)
- [ ] Response interceptor (handle errors)
- [ ] DTO mappers (frontend types ↔ backend types)
- [ ] Form builder save to API (not localStorage)
- [ ] Form submission to API
- [ ] Error handling and display
- [ ] Loading states

---

For full documentation, see: **API_DOCUMENTATION.md**
