# Contacts & Companies API Reference

Complete reference for managing contacts and companies in Freshdesk.

## Contacts

Contacts represent individual customers who submit support tickets.

### Contact Object

```json
{
  "id": 1001,
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+1-555-123-4567",
  "mobile": "+1-555-987-6543",
  "twitter_id": "@johnsmith",
  "facebook_id": "john.smith.12345",
  "unique_external_id": "EXT-1001",
  "company_id": 500,
  "view_all_tickets": false,
  "description": "VIP customer",
  "job_title": "Director of Operations",
  "language": "en",
  "time_zone": "Eastern Time (US & Canada)",
  "tags": ["vip", "enterprise"],
  "address": "123 Main St, New York, NY 10001",
  "avatar": null,
  "active": true,
  "deleted": false,
  "custom_fields": {
    "cf_account_tier": "Enterprise",
    "cf_renewal_date": "2025-01-15"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-12-01T14:30:00Z"
}
```

---

## List Contacts

Get all contacts with optional filtering.

```
GET /api/v2/contacts
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `email` | string | Filter by email address |
| `mobile` | string | Filter by mobile number |
| `phone` | string | Filter by phone number |
| `company_id` | integer | Filter by company |
| `state` | string | `verified`, `unverified`, `blocked`, `deleted` |
| `updated_since` | datetime | Contacts updated after date |
| `page` | integer | Page number |
| `per_page` | integer | Results per page (max 100) |

### Examples

```bash
# Get all contacts
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"

# Filter by email
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?email=john@example.com"

# Get contacts for a company
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?company_id=500"

# Get verified contacts updated recently
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?state=verified&updated_since=2024-12-01T00:00:00Z"
```

---

## Get Contact

Get a single contact by ID.

```
GET /api/v2/contacts/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001"
```

---

## Create Contact

Create a new contact.

```
POST /api/v2/contacts
```

### Required Fields (one of)

- `email` - Email address
- `phone` - Phone number
- `mobile` - Mobile number
- `twitter_id` - Twitter handle
- `unique_external_id` - External system ID

### Request Body

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-555-111-2222",
  "mobile": "+1-555-333-4444",
  "company_id": 500,
  "job_title": "Product Manager",
  "description": "Main point of contact for Project X",
  "language": "en",
  "time_zone": "Pacific Time (US & Canada)",
  "tags": ["project-x", "decision-maker"],
  "custom_fields": {
    "cf_account_tier": "Professional",
    "cf_department": "Product"
  }
}
```

### Examples

```bash
# Create basic contact
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"

# Create contact with full details
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-111-2222",
    "company_id": 500,
    "job_title": "Product Manager",
    "tags": ["vip"],
    "custom_fields": {
      "cf_account_tier": "Enterprise"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"

# Create contact with external ID
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "API User",
    "email": "api.user@example.com",
    "unique_external_id": "CRM-12345"
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"
```

---

## Update Contact

Update an existing contact.

```
PUT /api/v2/contacts/{id}
```

### Examples

```bash
# Update contact details
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "name": "Jane Smith",
    "job_title": "VP of Product",
    "company_id": 600
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001"

# Update custom fields
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "custom_fields": {
      "cf_account_tier": "Enterprise",
      "cf_renewal_date": "2025-06-01"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001"

# Add tags
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "tags": ["vip", "enterprise", "renewal-2025"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001"
```

---

## Delete Contact

Soft delete a contact.

```
DELETE /api/v2/contacts/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001"
```

---

## Restore Contact

Restore a deleted contact.

```
PUT /api/v2/contacts/{id}/restore
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X PUT \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001/restore"
```

---

## Hard Delete Contact

Permanently delete a contact (cannot be restored).

```
DELETE /api/v2/contacts/{id}/hard_delete?force=true
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001/hard_delete?force=true"
```

---

## Make Agent

Convert a contact to an agent.

```
PUT /api/v2/contacts/{id}/make_agent
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X PUT \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001/make_agent"
```

---

## Merge Contacts

Merge duplicate contacts.

```
PUT /api/v2/contacts/{id}/merge
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "contact_ids": [1002, 1003]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/1001/merge"
```

---

## Search Contacts

Search contacts with query syntax.

```
GET /api/v2/search/contacts
```

### Searchable Fields

| Field | Type | Example |
|-------|------|---------|
| `email` | string | `email:'john@example.com'` |
| `name` | string | `name:'John Smith'` |
| `phone` | string | `phone:'+1-555-123'` |
| `mobile` | string | `mobile:'+1-555-987'` |
| `company_id` | integer | `company_id:500` |
| `created_at` | datetime | `created_at:>'2024-01-01'` |
| `updated_at` | datetime | `updated_at:<'2024-12-01'` |

### Examples

```bash
# Search by name
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/contacts?query=\"name:'John'\""

# Search by company
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/contacts?query=\"company_id:500\""

# Full-text search
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/contacts?query=\"~'acme corp'\""
```

---

## Contact Fields

Get contact field definitions including custom fields.

```
GET /api/v2/contact_fields
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contact_fields"
```

---

# Companies

Companies represent organizations that contacts belong to.

## Company Object

```json
{
  "id": 500,
  "name": "Acme Corporation",
  "description": "Enterprise software company",
  "domains": ["acme.com", "acme.io"],
  "note": "Key account - handle with priority",
  "health_score": "At risk",
  "account_tier": "Enterprise",
  "renewal_date": "2025-01-15",
  "industry": "Technology",
  "custom_fields": {
    "cf_contract_value": 50000,
    "cf_account_manager": "Sarah Jones"
  },
  "created_at": "2023-06-15T10:00:00Z",
  "updated_at": "2024-12-01T14:30:00Z"
}
```

---

## List Companies

Get all companies.

```
GET /api/v2/companies
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `per_page` | integer | Results per page (max 100) |

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies"
```

---

## Get Company

Get a single company by ID.

```
GET /api/v2/companies/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/500"
```

---

## Create Company

Create a new company.

```
POST /api/v2/companies
```

### Required Fields

- `name` - Company name (unique)

### Request Body

```json
{
  "name": "New Corp",
  "description": "Startup in fintech space",
  "domains": ["newcorp.com", "newcorp.io"],
  "note": "Referred by existing customer",
  "health_score": "Happy",
  "account_tier": "Professional",
  "industry": "Financial Services",
  "custom_fields": {
    "cf_contract_value": 25000,
    "cf_account_manager": "Mike Wilson"
  }
}
```

### Examples

```bash
# Create basic company
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "New Corp",
    "domains": ["newcorp.com"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies"

# Create company with full details
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "Enterprise Inc",
    "description": "Fortune 500 company",
    "domains": ["enterprise.com", "enterprise.io"],
    "health_score": "Happy",
    "account_tier": "Enterprise",
    "industry": "Manufacturing",
    "custom_fields": {
      "cf_contract_value": 100000,
      "cf_account_manager": "Lisa Park"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies"
```

---

## Update Company

Update an existing company.

```
PUT /api/v2/companies/{id}
```

### Examples

```bash
# Update company details
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "description": "Updated company description",
    "health_score": "At risk",
    "note": "Escalation pending"
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/500"

# Update domains
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "domains": ["acme.com", "acme.io", "acme.net"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/500"

# Update custom fields
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "custom_fields": {
      "cf_contract_value": 75000,
      "cf_renewal_date": "2025-06-01"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/500"
```

---

## Delete Company

Delete a company.

```
DELETE /api/v2/companies/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/500"
```

---

## Search Companies

Search companies with query syntax.

```
GET /api/v2/search/companies
```

### Searchable Fields

| Field | Type | Example |
|-------|------|---------|
| `name` | string | `name:'Acme'` |
| `domain` | string | `domain:'acme.com'` |
| `created_at` | datetime | `created_at:>'2024-01-01'` |
| `updated_at` | datetime | `updated_at:<'2024-12-01'` |

### Examples

```bash
# Search by name
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/companies?query=\"name:'Acme'\""

# Search by domain
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/companies?query=\"domain:'acme.com'\""
```

---

## Company Fields

Get company field definitions including custom fields.

```
GET /api/v2/company_fields
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/company_fields"
```

---

## Agents

View and manage support agents.

### Agent Object

```json
{
  "id": 12,
  "contact": {
    "name": "Sarah Support",
    "email": "sarah@company.com",
    "phone": "+1-555-100-2000"
  },
  "type": "support_agent",
  "ticket_scope": 2,
  "available": true,
  "group_ids": [1, 2, 5],
  "role_ids": [1, 2],
  "signature": "<p>Best regards,<br>Sarah</p>",
  "created_at": "2023-01-15T10:00:00Z",
  "updated_at": "2024-12-01T14:30:00Z"
}
```

### Ticket Scope Values

| Value | Scope |
|-------|-------|
| 1 | Global Access |
| 2 | Group Access |
| 3 | Restricted Access |

---

## List Agents

```
GET /api/v2/agents
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/agents"
```

---

## Get Agent

```
GET /api/v2/agents/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/agents/12"
```

---

## Get Currently Authenticated Agent

```
GET /api/v2/agents/me
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/agents/me"
```

---

## Update Agent

```
PUT /api/v2/agents/{id}
```

**Note**: Requires admin privileges.

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "group_ids": [1, 2, 5, 10],
    "ticket_scope": 2
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/agents/12"
```

---

## Groups

Manage agent groups.

### List Groups

```
GET /api/v2/groups
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/groups"
```

### Get Group

```
GET /api/v2/groups/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/groups/5"
```

### Create Group

```
POST /api/v2/groups
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "name": "Premium Support",
    "description": "Handles enterprise customers",
    "agent_ids": [12, 15, 18]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/groups"
```

### Update Group

```
PUT /api/v2/groups/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "name": "Enterprise Support",
    "agent_ids": [12, 15, 18, 20]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/groups/5"
```

### Delete Group

```
DELETE /api/v2/groups/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/groups/5"
```

---

## Bulk Operations

### Export Contacts

```
POST /api/v2/contacts/export
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "fields": ["name", "email", "company_id", "created_at"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/export"
```

### Export Companies

```
POST /api/v2/companies/export
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "fields": ["name", "domains", "account_tier", "created_at"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/export"
```

---

## Common Patterns

### Find or Create Contact

```bash
#!/usr/bin/env bash
# Find contact by email, create if not exists

email="user@example.com"
name="New User"

# Try to find
contact=$(curl -s -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?email=$email")

if [ "$(echo "$contact" | jq length)" -eq 0 ]; then
  # Create new contact
  curl -u "$FRESHDESK_API_KEY:X" \
    -H "Content-Type: application/json" \
    -X POST \
    -d "{\"name\":\"$name\",\"email\":\"$email\"}" \
    "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"
else
  echo "$contact" | jq '.[0]'
fi
```

### Sync Contacts from CRM

```bash
#!/usr/bin/env bash
# Sync contacts from external system using unique_external_id

while IFS=, read -r ext_id name email company; do
  # Check if contact exists
  existing=$(curl -s -u "$FRESHDESK_API_KEY:X" \
    "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?unique_external_id=$ext_id")

  if [ "$(echo "$existing" | jq length)" -eq 0 ]; then
    # Create
    curl -s -u "$FRESHDESK_API_KEY:X" \
      -H "Content-Type: application/json" \
      -X POST \
      -d "{\"name\":\"$name\",\"email\":\"$email\",\"unique_external_id\":\"$ext_id\"}" \
      "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts"
  else
    # Update
    id=$(echo "$existing" | jq '.[0].id')
    curl -s -u "$FRESHDESK_API_KEY:X" \
      -H "Content-Type: application/json" \
      -X PUT \
      -d "{\"name\":\"$name\",\"email\":\"$email\"}" \
      "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts/$id"
  fi
done < crm_export.csv
```

### Get Company with All Contacts

```bash
#!/usr/bin/env bash
# Get company details with all associated contacts

company_id=500

# Get company
company=$(curl -s -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/companies/$company_id")

# Get contacts
contacts=$(curl -s -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/contacts?company_id=$company_id")

# Combine
jq -n --argjson company "$company" --argjson contacts "$contacts" \
  '{company: $company, contacts: $contacts}'
```
