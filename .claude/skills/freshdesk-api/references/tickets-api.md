# Tickets API Reference

Complete reference for Freshdesk Tickets API v2 including CRUD operations, conversations, time entries, and bulk operations.

## Ticket Object

```json
{
  "id": 1,
  "subject": "Support needed",
  "description": "<p>Details of the issue</p>",
  "description_text": "Details of the issue",
  "type": "Question",
  "status": 2,
  "priority": 1,
  "source": 1,
  "requester_id": 129,
  "responder_id": 12,
  "group_id": 3,
  "company_id": 1,
  "product_id": null,
  "email_config_id": 1,
  "due_by": "2024-12-25T10:00:00Z",
  "fr_due_by": "2024-12-23T10:00:00Z",
  "is_escalated": false,
  "tags": ["urgent", "billing"],
  "cc_emails": ["cc@example.com"],
  "fwd_emails": [],
  "reply_cc_emails": [],
  "spam": false,
  "deleted": false,
  "attachments": [],
  "custom_fields": {
    "cf_account_number": "ACC123",
    "cf_department": "Sales"
  },
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-15T14:30:00Z",
  "stats": {
    "agent_responded_at": "2024-12-01T11:00:00Z",
    "requester_responded_at": "2024-12-01T12:00:00Z",
    "first_responded_at": "2024-12-01T11:00:00Z",
    "status_updated_at": "2024-12-15T14:30:00Z",
    "reopened_at": null,
    "resolved_at": null,
    "closed_at": null,
    "pending_since": null
  }
}
```

## List Tickets

Get all tickets or filter by predefined views.

```
GET /api/v2/tickets
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `filter` | string | Predefined filter name |
| `requester_id` | integer | Filter by requester |
| `email` | string | Filter by requester email |
| `company_id` | integer | Filter by company |
| `updated_since` | datetime | Tickets updated after date |
| `order_by` | string | Field to sort by |
| `order_type` | string | `asc` or `desc` |
| `include` | string | Comma-separated: `requester`, `company`, `stats`, `description` |
| `page` | integer | Page number |
| `per_page` | integer | Results per page (max 100) |

### Predefined Filters

| Filter | Description |
|--------|-------------|
| `new_and_my_open` | New and open tickets assigned to you |
| `watching` | Tickets you're watching |
| `spam` | Spam tickets |
| `deleted` | Deleted tickets |
| `all_unresolved` | All unresolved tickets |

### Examples

```bash
# Get all tickets
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets"

# Get tickets with filters
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets?filter=new_and_my_open"

# Get tickets for a company
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets?company_id=123"

# Get tickets with embedded data
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets?include=requester,stats"

# Get recently updated tickets
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets?updated_since=2024-12-01T00:00:00Z"
```

## Get Ticket

Get a single ticket by ID.

```
GET /api/v2/tickets/{id}
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `include` | string | `conversations`, `requester`, `company`, `stats` |

### Examples

```bash
# Get ticket
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"

# Get ticket with conversations
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1?include=conversations"

# Get ticket with all related data
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1?include=conversations,requester,company,stats"
```

## Create Ticket

Create a new support ticket.

```
POST /api/v2/tickets
```

### Required Fields (one of)

- `requester_id` - ID of existing contact
- `email` - Email address (creates contact if new)
- `phone` - Phone number (creates contact if new)
- `twitter_id` - Twitter handle
- `facebook_id` - Facebook ID

### Request Body

```json
{
  "subject": "Support needed",
  "description": "<p>Detailed description with <b>HTML</b></p>",
  "email": "customer@example.com",
  "priority": 2,
  "status": 2,
  "type": "Question",
  "source": 1,
  "group_id": 3,
  "responder_id": 12,
  "product_id": 1,
  "cc_emails": ["cc@example.com"],
  "tags": ["billing", "urgent"],
  "due_by": "2024-12-25T10:00:00Z",
  "fr_due_by": "2024-12-23T10:00:00Z",
  "custom_fields": {
    "cf_account_number": "ACC123"
  }
}
```

### Examples

```bash
# Create basic ticket
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "subject": "Order not received",
    "description": "I placed an order last week...",
    "email": "customer@example.com",
    "priority": 2,
    "status": 2
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets"

# Create ticket with custom fields
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "subject": "Account issue",
    "description": "Cannot access my account",
    "email": "user@example.com",
    "priority": 3,
    "status": 2,
    "custom_fields": {
      "cf_account_number": "ACC789",
      "cf_department": "Support"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets"

# Create ticket with attachments (multipart)
curl -u "$FRESHDESK_API_KEY:X" \
  -X POST \
  -F "subject=Issue with attachment" \
  -F "description=Please see attached screenshot" \
  -F "email=user@example.com" \
  -F "priority=2" \
  -F "status=2" \
  -F "attachments[]=@/path/to/file.png" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets"
```

## Update Ticket

Update an existing ticket.

```
PUT /api/v2/tickets/{id}
```

### Examples

```bash
# Update status and priority
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "status": 4,
    "priority": 3
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"

# Assign to agent and group
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "responder_id": 12,
    "group_id": 5
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"

# Update custom fields
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "custom_fields": {
      "cf_resolution": "Issue resolved via phone call"
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"

# Add tags
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "tags": ["billing", "escalated", "vip"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"
```

## Delete Ticket

Move ticket to trash (soft delete).

```
DELETE /api/v2/tickets/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1"
```

## Restore Ticket

Restore a deleted ticket.

```
PUT /api/v2/tickets/{id}/restore
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X PUT \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/restore"
```

---

## Conversations

Manage ticket replies, notes, and forwards.

### Conversation Object

```json
{
  "id": 101,
  "body": "<p>Response content</p>",
  "body_text": "Response content",
  "incoming": false,
  "private": false,
  "source": 0,
  "user_id": 12,
  "to_emails": ["customer@example.com"],
  "cc_emails": [],
  "bcc_emails": [],
  "attachments": [],
  "created_at": "2024-12-15T10:00:00Z",
  "updated_at": "2024-12-15T10:00:00Z"
}
```

### List Conversations

```
GET /api/v2/tickets/{id}/conversations
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/conversations"
```

### Reply to Ticket

Send a public reply to the requester.

```
POST /api/v2/tickets/{id}/reply
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "body": "<p>Thank you for contacting us. We have resolved your issue.</p>",
    "cc_emails": ["manager@company.com"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/reply"
```

### Add Note

Add a private or public note.

```
POST /api/v2/tickets/{id}/notes
```

```bash
# Private note (internal)
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "body": "Customer called and confirmed issue is resolved.",
    "private": true
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/notes"

# Public note
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "body": "We are looking into this issue.",
    "private": false,
    "notify_emails": ["customer@example.com"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/notes"
```

### Forward Ticket

Forward ticket to external email.

```
POST /api/v2/tickets/{id}/forward
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "body": "Please review this customer issue.",
    "to_emails": ["vendor@external.com"]
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/forward"
```

### Update Conversation

```
PUT /api/v2/conversations/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "body": "<p>Updated response content</p>"
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/conversations/101"
```

### Delete Conversation

```
DELETE /api/v2/conversations/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/conversations/101"
```

---

## Time Entries

Track time spent on tickets.

### Time Entry Object

```json
{
  "id": 201,
  "agent_id": 12,
  "billable": true,
  "executed_at": "2024-12-15T10:00:00Z",
  "note": "Investigated issue and applied fix",
  "start_time": "2024-12-15T09:00:00Z",
  "time_spent": "01:30",
  "timer_running": false,
  "created_at": "2024-12-15T10:30:00Z",
  "updated_at": "2024-12-15T10:30:00Z"
}
```

### List Time Entries

```
GET /api/v2/tickets/{id}/time_entries
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/time_entries"
```

### Create Time Entry

```
POST /api/v2/tickets/{id}/time_entries
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "agent_id": 12,
    "billable": true,
    "time_spent": "01:30",
    "note": "Troubleshooting and resolution"
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/time_entries"
```

### Update Time Entry

```
PUT /api/v2/time_entries/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X PUT \
  -d '{
    "time_spent": "02:00",
    "billable": true
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/time_entries/201"
```

### Delete Time Entry

```
DELETE /api/v2/time_entries/{id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/time_entries/201"
```

---

## Satisfaction Ratings

Get customer satisfaction survey responses.

### List Satisfaction Ratings

```
GET /api/v2/tickets/{id}/satisfaction_ratings
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/satisfaction_ratings"
```

### Get All Ratings

```
GET /api/v2/surveys/satisfaction_ratings
```

```bash
# Get all ratings
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/surveys/satisfaction_ratings"

# Filter by date
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/surveys/satisfaction_ratings?created_since=2024-12-01"
```

---

## Ticket Fields

Get ticket field definitions including custom fields.

### List Ticket Fields

```
GET /api/v2/ticket_fields
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/ticket_fields"
```

### Response

```json
[
  {
    "id": 1,
    "name": "status",
    "label": "Status",
    "type": "default_status",
    "required_for_agents": true,
    "required_for_customers": false,
    "choices": [
      {"id": 2, "value": "Open"},
      {"id": 3, "value": "Pending"},
      {"id": 4, "value": "Resolved"},
      {"id": 5, "value": "Closed"}
    ]
  },
  {
    "id": 100,
    "name": "cf_department",
    "label": "Department",
    "type": "custom_dropdown",
    "required_for_agents": false,
    "choices": [
      {"id": 1, "value": "Sales"},
      {"id": 2, "value": "Support"},
      {"id": 3, "value": "Billing"}
    ]
  }
]
```

---

## Bulk Operations

### Bulk Update Tickets

Update multiple tickets at once.

```
POST /api/v2/tickets/bulk_update
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "ids": [1, 2, 3, 4, 5],
    "properties": {
      "status": 4,
      "priority": 2,
      "group_id": 5
    }
  }' \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/bulk_update"
```

### Delete Ticket Attachment

```
DELETE /api/v2/tickets/{ticket_id}/attachments/{attachment_id}
```

```bash
curl -u "$FRESHDESK_API_KEY:X" \
  -X DELETE \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/tickets/1/attachments/301"
```

---

## Search Tickets

Advanced ticket search with query syntax.

```
GET /api/v2/search/tickets
```

### Query Syntax

```
"<field>:<operator><value>"
```

### Searchable Fields

| Field | Type | Example |
|-------|------|---------|
| `status` | integer | `status:2` |
| `priority` | integer | `priority:4` |
| `type` | string | `type:'Question'` |
| `tag` | string | `tag:'billing'` |
| `requester_email` | string | `requester_email:'user@example.com'` |
| `agent_id` | integer | `agent_id:12` |
| `group_id` | integer | `group_id:5` |
| `company_id` | integer | `company_id:100` |
| `created_at` | datetime | `created_at:>'2024-01-01'` |
| `updated_at` | datetime | `updated_at:<'2024-12-01'` |
| `due_by` | datetime | `due_by:>'2024-12-25'` |

### Examples

```bash
# High priority open tickets
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/tickets?query=\"status:2 AND priority:4\""

# Tickets from specific company created this month
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/tickets?query=\"company_id:100 AND created_at:>'2024-12-01'\""

# Full-text search
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/tickets?query=\"~'password reset'\""

# Overdue tickets
curl -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN.freshdesk.com/api/v2/search/tickets?query=\"due_by:<'$(date -u +%Y-%m-%dT%H:%M:%SZ)' AND status:2\""
```

### Response

```json
{
  "total": 50,
  "results": [
    {
      "id": 1,
      "subject": "...",
      ...
    }
  ]
}
```

**Note**: Search results are limited to 30 items per page. Use pagination with `page` parameter.
