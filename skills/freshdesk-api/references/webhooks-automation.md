# Webhooks & Automation Reference

Configure webhooks and automation rules to react to Freshdesk events in real-time.

## Webhooks Overview

Webhooks allow external applications to receive real-time notifications when events occur in Freshdesk. Instead of polling the API repeatedly, webhooks push data to your endpoint when something happens.

### Benefits

- **Real-time updates** - Immediate notification when events occur
- **Reduced API usage** - No need to poll for changes
- **Event-driven architecture** - React to specific events
- **Scalability** - Handle high volumes of updates efficiently

---

## Setting Up Webhooks

### Via Admin Portal

1. Log into Freshdesk as Admin
2. Go to **Admin** → **Automations** → **Ticket Updates** (or **Ticket Creation**)
3. Create a new rule or edit existing
4. Add action: **Trigger Webhook** or **Trigger API**
5. Configure the webhook URL and payload

### Webhook vs API Action

| Action | Use Case |
|--------|----------|
| **Trigger Webhook** | When you don't need the API response |
| **Trigger API** | When you need the response for subsequent actions |

---

## Webhook Configuration

### Basic Setup

```json
{
  "url": "https://your-app.com/webhook/freshdesk",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-secret-token"
  },
  "body": {
    "event": "ticket_created",
    "ticket_id": "{{ticket.id}}",
    "subject": "{{ticket.subject}}",
    "requester_email": "{{ticket.requester.email}}"
  }
}
```

### Available Placeholders

Use these placeholders in webhook URLs and payloads:

#### Ticket Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{ticket.id}}` | Ticket ID |
| `{{ticket.subject}}` | Ticket subject |
| `{{ticket.description}}` | Full description (HTML) |
| `{{ticket.description_text}}` | Plain text description |
| `{{ticket.status}}` | Status name |
| `{{ticket.priority}}` | Priority name |
| `{{ticket.type}}` | Ticket type |
| `{{ticket.source}}` | Source (Email, Portal, etc.) |
| `{{ticket.tags}}` | Comma-separated tags |
| `{{ticket.created_at}}` | Creation timestamp |
| `{{ticket.updated_at}}` | Last update timestamp |
| `{{ticket.due_by}}` | Due date |
| `{{ticket.url}}` | Ticket URL in Freshdesk |

#### Requester Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{ticket.requester.id}}` | Requester ID |
| `{{ticket.requester.name}}` | Requester name |
| `{{ticket.requester.email}}` | Requester email |
| `{{ticket.requester.phone}}` | Requester phone |
| `{{ticket.requester.company}}` | Company name |

#### Agent Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{ticket.agent.id}}` | Assigned agent ID |
| `{{ticket.agent.name}}` | Assigned agent name |
| `{{ticket.agent.email}}` | Assigned agent email |

#### Group Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{ticket.group.id}}` | Group ID |
| `{{ticket.group.name}}` | Group name |

#### Company Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{ticket.company.id}}` | Company ID |
| `{{ticket.company.name}}` | Company name |

---

## Event Types

### Ticket Creation Events

Trigger webhooks when new tickets are created.

**Rule Location**: Admin → Automations → Ticket Creation

**Common Conditions**:
- Source is Email
- Priority is High/Urgent
- Subject contains specific keywords
- Requester belongs to specific company

**Example Rule**:
```
IF ticket.source = "Email"
AND ticket.priority = "Urgent"
THEN trigger_webhook(url, payload)
```

### Ticket Update Events

Trigger webhooks when tickets are modified.

**Rule Location**: Admin → Automations → Ticket Updates

**Available Triggers**:
- Status changed
- Priority changed
- Agent assigned
- Group changed
- Tag added/removed
- Reply added
- Note added

**Example Rule**:
```
IF ticket.status changes to "Resolved"
THEN trigger_webhook(url, payload)
```

---

## Webhook Payload Examples

### Ticket Created

```json
{
  "freshdesk_webhook": {
    "ticket_id": 12345,
    "ticket_subject": "Order not received",
    "ticket_status": "Open",
    "ticket_priority": "Medium",
    "ticket_source": "Email",
    "ticket_type": "Question",
    "ticket_requester_name": "John Smith",
    "ticket_requester_email": "john@example.com",
    "ticket_company": "Acme Corp",
    "ticket_created_at": "2024-12-15T10:00:00Z",
    "triggered_event": "ticket_created"
  }
}
```

### Ticket Updated (Status Change)

```json
{
  "freshdesk_webhook": {
    "ticket_id": 12345,
    "ticket_subject": "Order not received",
    "ticket_old_status": "Open",
    "ticket_new_status": "Resolved",
    "ticket_agent_name": "Sarah Support",
    "ticket_resolved_at": "2024-12-15T14:30:00Z",
    "triggered_event": "ticket_status_updated"
  }
}
```

### Agent Reply Added

```json
{
  "freshdesk_webhook": {
    "ticket_id": 12345,
    "ticket_subject": "Order not received",
    "conversation_body": "Thank you for contacting us...",
    "conversation_agent": "Sarah Support",
    "conversation_created_at": "2024-12-15T11:00:00Z",
    "triggered_event": "agent_reply_added"
  }
}
```

### Customer Reply Added

```json
{
  "freshdesk_webhook": {
    "ticket_id": 12345,
    "ticket_subject": "Order not received",
    "conversation_body": "Thank you for the update...",
    "conversation_requester": "John Smith",
    "conversation_created_at": "2024-12-15T12:00:00Z",
    "triggered_event": "customer_reply_added"
  }
}
```

---

## Rate Limits

### Webhook Execution Limits

| Limit | Value |
|-------|-------|
| Webhooks per hour | 1000 |
| Buffer time | Up to 24 hours |
| Retry interval | Every 30 minutes |
| Max retries | 48 attempts |

### What Happens When Limited

1. Webhooks exceeding rate limit are buffered
2. Buffered webhooks are sent in the next hour
3. Webhooks buffered for >24 hours are dropped
4. Failed webhooks retry every 30 minutes

### Monitoring

- Failed webhooks trigger email notifications to admins
- View webhook logs in Admin → Automations → Webhooks

---

## Receiving Webhooks

### Example: Node.js/Express

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Webhook endpoint
app.post('/webhook/freshdesk', (req, res) => {
  // Verify webhook (optional - if you've set a secret)
  const signature = req.headers['x-freshdesk-signature'];
  if (signature) {
    const expectedSignature = crypto
      .createHmac('sha256', process.env.WEBHOOK_SECRET)
      .update(JSON.stringify(req.body))
      .digest('hex');

    if (signature !== expectedSignature) {
      return res.status(401).send('Invalid signature');
    }
  }

  // Process the webhook
  const payload = req.body.freshdesk_webhook;

  console.log('Event:', payload.triggered_event);
  console.log('Ticket ID:', payload.ticket_id);
  console.log('Subject:', payload.ticket_subject);

  // Handle different events
  switch (payload.triggered_event) {
    case 'ticket_created':
      handleNewTicket(payload);
      break;
    case 'ticket_status_updated':
      handleStatusChange(payload);
      break;
    case 'agent_reply_added':
      handleAgentReply(payload);
      break;
  }

  // Respond quickly to avoid timeout
  res.status(200).send('OK');
});

function handleNewTicket(payload) {
  // Create Slack notification
  // Create CRM record
  // etc.
}

function handleStatusChange(payload) {
  // Update external systems
  // Send customer notification
  // etc.
}

function handleAgentReply(payload) {
  // Log to analytics
  // Update response time metrics
  // etc.
}

app.listen(3000);
```

### Example: Python/Flask

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import os

app = Flask(__name__)

@app.route('/webhook/freshdesk', methods=['POST'])
def freshdesk_webhook():
    # Verify signature (optional)
    signature = request.headers.get('X-Freshdesk-Signature')
    if signature:
        expected = hmac.new(
            os.environ['WEBHOOK_SECRET'].encode(),
            request.data,
            hashlib.sha256
        ).hexdigest()

        if signature != expected:
            return jsonify({'error': 'Invalid signature'}), 401

    # Process payload
    payload = request.json.get('freshdesk_webhook', {})

    event = payload.get('triggered_event')
    ticket_id = payload.get('ticket_id')
    subject = payload.get('ticket_subject')

    print(f"Event: {event}, Ticket: {ticket_id}, Subject: {subject}")

    # Handle events
    if event == 'ticket_created':
        handle_new_ticket(payload)
    elif event == 'ticket_status_updated':
        handle_status_change(payload)

    return jsonify({'status': 'ok'}), 200

def handle_new_ticket(payload):
    # Implement your logic
    pass

def handle_status_change(payload):
    # Implement your logic
    pass

if __name__ == '__main__':
    app.run(port=3000)
```

---

## Automation Rules

Beyond webhooks, Freshdesk supports automation rules for internal actions.

### Ticket Creation Rules

**Location**: Admin → Automations → Ticket Creation

**Available Actions**:
- Assign to agent/group
- Set priority/status
- Add tags
- Send email notification
- Trigger webhook
- Add note

**Example: Route VIP Tickets**

```
Conditions:
  - Ticket company is "Enterprise Corp"
  OR
  - Requester email contains "@enterprise.com"

Actions:
  - Set priority to "Urgent"
  - Assign to group "Enterprise Support"
  - Add tag "vip"
  - Trigger webhook to notify Slack
```

### Time-Based Rules

**Location**: Admin → Automations → Time Triggers

**Available Triggers**:
- Hours since created
- Hours since updated
- Hours since agent responded
- Hours since customer responded
- Hours since status changed

**Example: Escalation Rule**

```
Conditions:
  - Hours since created > 4
  - Status is "Open"
  - Priority is "High"

Actions:
  - Add tag "escalated"
  - Send email to manager
  - Trigger webhook
```

### Event-Based Rules

**Location**: Admin → Automations → Ticket Updates

**Available Triggers**:
- Status changed
- Priority changed
- Agent assigned
- Group changed
- Tag added
- Reply received

---

## Testing Webhooks

### Using RequestBin

1. Go to [RequestBin](https://requestbin.com) or [Webhook.site](https://webhook.site)
2. Create a new bin and copy the URL
3. Use the URL in your Freshdesk webhook configuration
4. Trigger the event and inspect the payload

### Using curl

```bash
# Simulate a webhook payload
curl -X POST https://your-app.com/webhook/freshdesk \
  -H "Content-Type: application/json" \
  -d '{
    "freshdesk_webhook": {
      "ticket_id": 12345,
      "ticket_subject": "Test ticket",
      "ticket_status": "Open",
      "triggered_event": "ticket_created"
    }
  }'
```

### Local Development

Use [ngrok](https://ngrok.com) to expose your local server:

```bash
# Install ngrok
brew install ngrok

# Expose local port 3000
ngrok http 3000

# Use the ngrok URL in Freshdesk webhook configuration
# e.g., https://abc123.ngrok.io/webhook/freshdesk
```

---

## Best Practices

### Reliability

1. **Respond quickly** - Return 200 OK within 30 seconds
2. **Process async** - Queue heavy processing for background jobs
3. **Implement idempotency** - Handle duplicate webhook deliveries
4. **Store raw payloads** - Log webhooks for debugging

### Security

1. **Use HTTPS** - Only accept webhooks over HTTPS
2. **Verify signatures** - Validate webhook authenticity
3. **Use secrets** - Include shared secret in headers
4. **Whitelist IPs** - Restrict to Freshdesk IP ranges (if available)

### Monitoring

1. **Log all webhooks** - Track successes and failures
2. **Set up alerts** - Notify on failed webhooks
3. **Monitor latency** - Track webhook processing time
4. **Track event counts** - Monitor webhook volume

### Error Handling

1. **Return proper status codes**:
   - 200: Success
   - 4xx: Client error (don't retry)
   - 5xx: Server error (retry)

2. **Handle missing data** - Not all fields may be present

3. **Implement retry logic** - For downstream failures

---

## Integration Patterns

### Slack Notifications

```javascript
async function notifySlack(payload) {
  const message = {
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*New Ticket*: ${payload.ticket_subject}`
        }
      },
      {
        type: 'section',
        fields: [
          {
            type: 'mrkdwn',
            text: `*From:* ${payload.ticket_requester_name}`
          },
          {
            type: 'mrkdwn',
            text: `*Priority:* ${payload.ticket_priority}`
          }
        ]
      },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: { type: 'plain_text', text: 'View Ticket' },
            url: `https://yourcompany.freshdesk.com/a/tickets/${payload.ticket_id}`
          }
        ]
      }
    ]
  };

  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message)
  });
}
```

### CRM Sync

```python
def sync_to_crm(payload):
    """Sync ticket data to external CRM"""
    crm_data = {
        'external_id': payload['ticket_id'],
        'type': 'support_ticket',
        'subject': payload['ticket_subject'],
        'customer_email': payload['ticket_requester_email'],
        'status': map_status(payload['ticket_status']),
        'created_at': payload['ticket_created_at']
    }

    response = requests.post(
        f"{CRM_API_URL}/tickets",
        headers={'Authorization': f"Bearer {CRM_API_KEY}"},
        json=crm_data
    )

    return response.status_code == 201

def map_status(freshdesk_status):
    """Map Freshdesk status to CRM status"""
    mapping = {
        'Open': 'active',
        'Pending': 'waiting',
        'Resolved': 'completed',
        'Closed': 'archived'
    }
    return mapping.get(freshdesk_status, 'unknown')
```

### Analytics Pipeline

```javascript
async function trackEvent(payload) {
  const event = {
    event_name: 'freshdesk_ticket',
    event_type: payload.triggered_event,
    timestamp: new Date().toISOString(),
    properties: {
      ticket_id: payload.ticket_id,
      status: payload.ticket_status,
      priority: payload.ticket_priority,
      source: payload.ticket_source,
      company: payload.ticket_company,
      requester_email: payload.ticket_requester_email
    }
  };

  // Send to analytics (e.g., Segment, Amplitude, Mixpanel)
  await analytics.track(event);
}
```
