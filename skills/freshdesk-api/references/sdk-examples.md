# SDK Code Examples

Complete code examples for integrating with Freshdesk using official and community SDKs.

## Python SDK

### Installation

```bash
pip install python-freshdesk
```

**Repository**: [github.com/sjkingo/python-freshdesk](https://github.com/sjkingo/python-freshdesk)

### Setup

```python
from freshdesk.api import API

# Initialize the API client
api = API('yourcompany.freshdesk.com', 'your-api-key')
```

### Tickets

```python
from freshdesk.api import API

api = API('yourcompany.freshdesk.com', 'your-api-key')

# List all tickets
tickets = api.tickets.list_tickets()
for ticket in tickets:
    print(f"#{ticket.id}: {ticket.subject} - {ticket.status}")

# Get a specific ticket
ticket = api.tickets.get_ticket(12345)
print(f"Subject: {ticket.subject}")
print(f"Status: {ticket.status}")
print(f"Priority: {ticket.priority}")
print(f"Requester: {ticket.requester_id}")

# Get ticket with conversations
ticket = api.tickets.get_ticket(12345, include='conversations')
for conv in ticket.conversations:
    print(f"From: {conv.user_id}")
    print(f"Body: {conv.body_text}")

# Create a ticket
new_ticket = api.tickets.create_ticket(
    subject='Support needed',
    description='Please help with this issue',
    email='customer@example.com',
    priority=2,  # Medium
    status=2,    # Open
    tags=['support', 'new']
)
print(f"Created ticket #{new_ticket.id}")

# Update a ticket
api.tickets.update_ticket(
    12345,
    status=4,     # Resolved
    priority=3,   # High
    responder_id=5
)

# Delete a ticket
api.tickets.delete_ticket(12345)

# Restore a deleted ticket
api.tickets.restore_ticket(12345)
```

### Ticket Filters

```python
# Filter tickets by status
open_tickets = api.tickets.list_tickets(filter_name='new_and_my_open')

# Filter by company
company_tickets = api.tickets.list_tickets(company_id=500)

# Filter by requester
requester_tickets = api.tickets.list_tickets(requester_id=1001)

# Get tickets updated since a date
from datetime import datetime, timedelta
since = datetime.now() - timedelta(days=7)
recent_tickets = api.tickets.list_tickets(
    updated_since=since.strftime('%Y-%m-%dT%H:%M:%SZ')
)
```

### Conversations

```python
# Reply to a ticket
api.comments.create_reply(
    ticket_id=12345,
    body='Thank you for contacting us. Your issue has been resolved.'
)

# Add a private note
api.comments.create_note(
    ticket_id=12345,
    body='Internal: Customer called and confirmed resolution.',
    private=True
)

# Add a public note
api.comments.create_note(
    ticket_id=12345,
    body='We are investigating this issue.',
    private=False
)
```

### Contacts

```python
# List all contacts
contacts = api.contacts.list_contacts()
for contact in contacts:
    print(f"{contact.name} - {contact.email}")

# Get a contact
contact = api.contacts.get_contact(1001)

# Create a contact
new_contact = api.contacts.create_contact(
    name='Jane Doe',
    email='jane@example.com',
    phone='+1-555-123-4567',
    company_id=500
)

# Update a contact
api.contacts.update_contact(
    1001,
    job_title='VP of Operations',
    custom_fields={'cf_account_tier': 'Enterprise'}
)

# Delete a contact
api.contacts.delete_contact(1001)
```

### Companies

```python
# List companies
companies = api.companies.list_companies()

# Get a company
company = api.companies.get_company(500)

# Create a company
new_company = api.companies.create_company(
    name='New Corp',
    domains=['newcorp.com', 'newcorp.io'],
    description='Technology startup'
)

# Update a company
api.companies.update_company(
    500,
    health_score='At risk',
    custom_fields={'cf_account_manager': 'Mike Wilson'}
)
```

### Agents

```python
# List agents
agents = api.agents.list_agents()
for agent in agents:
    print(f"{agent.contact.name} - {agent.contact.email}")

# Get current agent
me = api.agents.get_agent(0)  # 0 = current user
```

### Pagination

```python
# Paginate through all tickets
page = 1
all_tickets = []

while True:
    tickets = api.tickets.list_tickets(page=page, per_page=100)
    if not tickets:
        break
    all_tickets.extend(tickets)
    page += 1

print(f"Total tickets: {len(all_tickets)}")
```

### Error Handling

```python
from freshdesk.api import API
from freshdesk.exceptions import FreshdeskError

api = API('yourcompany.freshdesk.com', 'your-api-key')

try:
    ticket = api.tickets.get_ticket(99999)
except FreshdeskError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
```

---

## Node.js SDK

### Installation

```bash
npm install node-freshdesk-api
```

**Repository**: [github.com/kumarharsh/node-freshdesk](https://github.com/kumarharsh/node-freshdesk)

### Setup

```javascript
const Freshdesk = require('node-freshdesk-api');

const freshdesk = new Freshdesk('https://yourcompany.freshdesk.com', 'your-api-key');
```

### Tickets

```javascript
const Freshdesk = require('node-freshdesk-api');

const freshdesk = new Freshdesk('https://yourcompany.freshdesk.com', 'your-api-key');

// List tickets
freshdesk.listAllTickets((err, data) => {
  if (err) {
    console.error('Error:', err);
    return;
  }
  data.forEach(ticket => {
    console.log(`#${ticket.id}: ${ticket.subject}`);
  });
});

// Using async/await with promisify
const util = require('util');
const listTickets = util.promisify(freshdesk.listAllTickets.bind(freshdesk));

async function getTickets() {
  try {
    const tickets = await listTickets();
    return tickets;
  } catch (err) {
    console.error('Error:', err);
  }
}

// Get a ticket
freshdesk.getTicket(12345, (err, ticket) => {
  console.log(`Subject: ${ticket.subject}`);
  console.log(`Status: ${ticket.status}`);
});

// Create a ticket
freshdesk.createTicket({
  subject: 'Support needed',
  description: 'Please help with this issue',
  email: 'customer@example.com',
  priority: 2,
  status: 2,
  tags: ['support']
}, (err, ticket) => {
  if (err) {
    console.error('Error:', err);
    return;
  }
  console.log(`Created ticket #${ticket.id}`);
});

// Update a ticket
freshdesk.updateTicket(12345, {
  status: 4,
  priority: 3
}, (err, ticket) => {
  console.log(`Updated ticket #${ticket.id}`);
});

// Delete a ticket
freshdesk.deleteTicket(12345, (err) => {
  if (!err) {
    console.log('Ticket deleted');
  }
});
```

### Modern Async/Await Pattern

```javascript
const Freshdesk = require('node-freshdesk-api');
const util = require('util');

class FreshdeskClient {
  constructor(domain, apiKey) {
    this.client = new Freshdesk(`https://${domain}.freshdesk.com`, apiKey);

    // Promisify all methods
    this.listTickets = util.promisify(this.client.listAllTickets.bind(this.client));
    this.getTicket = util.promisify(this.client.getTicket.bind(this.client));
    this.createTicket = util.promisify(this.client.createTicket.bind(this.client));
    this.updateTicket = util.promisify(this.client.updateTicket.bind(this.client));
    this.deleteTicket = util.promisify(this.client.deleteTicket.bind(this.client));
    this.listContacts = util.promisify(this.client.listAllContacts.bind(this.client));
    this.getContact = util.promisify(this.client.getContact.bind(this.client));
    this.createContact = util.promisify(this.client.createContact.bind(this.client));
  }
}

// Usage
async function main() {
  const fd = new FreshdeskClient('yourcompany', process.env.FRESHDESK_API_KEY);

  // List tickets
  const tickets = await fd.listTickets();
  console.log(`Found ${tickets.length} tickets`);

  // Create ticket
  const newTicket = await fd.createTicket({
    subject: 'Test ticket',
    description: 'Created via API',
    email: 'test@example.com',
    priority: 2,
    status: 2
  });
  console.log(`Created #${newTicket.id}`);

  // Update and close
  await fd.updateTicket(newTicket.id, { status: 5 });
  console.log('Ticket closed');
}

main().catch(console.error);
```

### Contacts

```javascript
// List contacts
freshdesk.listAllContacts((err, contacts) => {
  contacts.forEach(contact => {
    console.log(`${contact.name} - ${contact.email}`);
  });
});

// Create contact
freshdesk.createContact({
  name: 'Jane Doe',
  email: 'jane@example.com',
  phone: '+1-555-123-4567',
  company_id: 500
}, (err, contact) => {
  console.log(`Created contact #${contact.id}`);
});

// Update contact
freshdesk.updateContact(1001, {
  job_title: 'Director',
  custom_fields: { cf_department: 'Engineering' }
}, (err, contact) => {
  console.log('Contact updated');
});
```

### Companies

```javascript
// List companies
freshdesk.listAllCompanies((err, companies) => {
  companies.forEach(company => {
    console.log(`${company.name} - ${company.domains.join(', ')}`);
  });
});

// Create company
freshdesk.createCompany({
  name: 'New Corp',
  domains: ['newcorp.com']
}, (err, company) => {
  console.log(`Created company #${company.id}`);
});
```

---

## Ruby SDK

### Installation

```bash
gem install freshdesk
```

**Repository**: [github.com/snkrheads/freshdesk-ruby](https://github.com/snkrheads/freshdesk-ruby)

### Setup

```ruby
require 'freshdesk'

# Configure the client
Freshdesk.configure do |config|
  config.domain = 'yourcompany'
  config.api_key = 'your-api-key'
end
```

### Tickets

```ruby
require 'freshdesk'

Freshdesk.configure do |config|
  config.domain = 'yourcompany'
  config.api_key = ENV['FRESHDESK_API_KEY']
end

# List tickets
tickets = Freshdesk::Ticket.all
tickets.each do |ticket|
  puts "##{ticket.id}: #{ticket.subject}"
end

# Get a ticket
ticket = Freshdesk::Ticket.find(12345)
puts "Subject: #{ticket.subject}"
puts "Status: #{ticket.status}"

# Create a ticket
ticket = Freshdesk::Ticket.create(
  subject: 'Support needed',
  description: 'Please help with this issue',
  email: 'customer@example.com',
  priority: 2,
  status: 2
)
puts "Created ticket ##{ticket.id}"

# Update a ticket
ticket = Freshdesk::Ticket.find(12345)
ticket.update(status: 4, priority: 3)
puts "Ticket updated"

# Delete a ticket
ticket = Freshdesk::Ticket.find(12345)
ticket.destroy
puts "Ticket deleted"
```

### Contacts

```ruby
# List contacts
contacts = Freshdesk::Contact.all
contacts.each do |contact|
  puts "#{contact.name} - #{contact.email}"
end

# Create contact
contact = Freshdesk::Contact.create(
  name: 'Jane Doe',
  email: 'jane@example.com',
  company_id: 500
)
puts "Created contact ##{contact.id}"

# Update contact
contact = Freshdesk::Contact.find(1001)
contact.update(job_title: 'VP of Operations')
```

### Companies

```ruby
# List companies
companies = Freshdesk::Company.all

# Create company
company = Freshdesk::Company.create(
  name: 'New Corp',
  domains: ['newcorp.com']
)
```

---

## PHP Examples

Using direct HTTP requests with Guzzle:

### Installation

```bash
composer require guzzlehttp/guzzle
```

### Setup

```php
<?php
require 'vendor/autoload.php';

use GuzzleHttp\Client;

class FreshdeskAPI {
    private $client;
    private $domain;
    private $apiKey;

    public function __construct($domain, $apiKey) {
        $this->domain = $domain;
        $this->apiKey = $apiKey;
        $this->client = new Client([
            'base_uri' => "https://{$domain}.freshdesk.com/api/v2/",
            'auth' => [$apiKey, 'X'],
            'headers' => ['Content-Type' => 'application/json']
        ]);
    }

    // Tickets
    public function listTickets($params = []) {
        $response = $this->client->get('tickets', ['query' => $params]);
        return json_decode($response->getBody(), true);
    }

    public function getTicket($id) {
        $response = $this->client->get("tickets/{$id}");
        return json_decode($response->getBody(), true);
    }

    public function createTicket($data) {
        $response = $this->client->post('tickets', ['json' => $data]);
        return json_decode($response->getBody(), true);
    }

    public function updateTicket($id, $data) {
        $response = $this->client->put("tickets/{$id}", ['json' => $data]);
        return json_decode($response->getBody(), true);
    }

    public function deleteTicket($id) {
        $this->client->delete("tickets/{$id}");
        return true;
    }

    // Contacts
    public function listContacts($params = []) {
        $response = $this->client->get('contacts', ['query' => $params]);
        return json_decode($response->getBody(), true);
    }

    public function createContact($data) {
        $response = $this->client->post('contacts', ['json' => $data]);
        return json_decode($response->getBody(), true);
    }

    // Companies
    public function listCompanies() {
        $response = $this->client->get('companies');
        return json_decode($response->getBody(), true);
    }

    public function createCompany($data) {
        $response = $this->client->post('companies', ['json' => $data]);
        return json_decode($response->getBody(), true);
    }
}
```

### Usage

```php
<?php
$api = new FreshdeskAPI('yourcompany', 'your-api-key');

// List tickets
$tickets = $api->listTickets();
foreach ($tickets as $ticket) {
    echo "#{$ticket['id']}: {$ticket['subject']}\n";
}

// Create ticket
$newTicket = $api->createTicket([
    'subject' => 'Support needed',
    'description' => 'Please help with this issue',
    'email' => 'customer@example.com',
    'priority' => 2,
    'status' => 2
]);
echo "Created ticket #{$newTicket['id']}\n";

// Update ticket
$api->updateTicket($newTicket['id'], [
    'status' => 4,
    'priority' => 3
]);

// Create contact
$contact = $api->createContact([
    'name' => 'Jane Doe',
    'email' => 'jane@example.com'
]);
```

---

## Java Examples

Using HttpClient (Java 11+):

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Base64;

public class FreshdeskAPI {
    private final HttpClient client;
    private final String baseUrl;
    private final String authHeader;

    public FreshdeskAPI(String domain, String apiKey) {
        this.client = HttpClient.newHttpClient();
        this.baseUrl = "https://" + domain + ".freshdesk.com/api/v2/";
        this.authHeader = "Basic " + Base64.getEncoder()
            .encodeToString((apiKey + ":X").getBytes());
    }

    public String listTickets() throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "tickets"))
            .header("Authorization", authHeader)
            .header("Content-Type", "application/json")
            .GET()
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    public String getTicket(int id) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "tickets/" + id))
            .header("Authorization", authHeader)
            .header("Content-Type", "application/json")
            .GET()
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    public String createTicket(String jsonBody) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "tickets"))
            .header("Authorization", authHeader)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    public String updateTicket(int id, String jsonBody) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "tickets/" + id))
            .header("Authorization", authHeader)
            .header("Content-Type", "application/json")
            .PUT(HttpRequest.BodyPublishers.ofString(jsonBody))
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    public static void main(String[] args) throws Exception {
        FreshdeskAPI api = new FreshdeskAPI("yourcompany", "your-api-key");

        // List tickets
        String tickets = api.listTickets();
        System.out.println(tickets);

        // Create ticket
        String newTicket = api.createTicket("""
            {
                "subject": "Support needed",
                "description": "Please help",
                "email": "customer@example.com",
                "priority": 2,
                "status": 2
            }
            """);
        System.out.println("Created: " + newTicket);
    }
}
```

---

## TypeScript Examples

Using fetch with full type safety:

```typescript
interface Ticket {
  id: number;
  subject: string;
  description: string;
  status: number;
  priority: number;
  requester_id: number;
  responder_id: number | null;
  created_at: string;
  updated_at: string;
  tags: string[];
  custom_fields: Record<string, unknown>;
}

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  company_id: number | null;
  created_at: string;
}

interface CreateTicketParams {
  subject: string;
  description: string;
  email?: string;
  requester_id?: number;
  priority: 1 | 2 | 3 | 4;
  status: 2 | 3 | 4 | 5;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
}

class FreshdeskClient {
  private baseUrl: string;
  private headers: HeadersInit;

  constructor(domain: string, apiKey: string) {
    this.baseUrl = `https://${domain}.freshdesk.com/api/v2`;
    this.headers = {
      'Authorization': `Basic ${btoa(`${apiKey}:X`)}`,
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: { ...this.headers, ...options.headers },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Freshdesk API Error: ${JSON.stringify(error)}`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Tickets
  async listTickets(params?: Record<string, string>): Promise<Ticket[]> {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return this.request<Ticket[]>(`/tickets${query}`);
  }

  async getTicket(id: number): Promise<Ticket> {
    return this.request<Ticket>(`/tickets/${id}`);
  }

  async createTicket(data: CreateTicketParams): Promise<Ticket> {
    return this.request<Ticket>('/tickets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTicket(
    id: number,
    data: Partial<CreateTicketParams>
  ): Promise<Ticket> {
    return this.request<Ticket>(`/tickets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTicket(id: number): Promise<void> {
    await this.request<void>(`/tickets/${id}`, { method: 'DELETE' });
  }

  // Contacts
  async listContacts(): Promise<Contact[]> {
    return this.request<Contact[]>('/contacts');
  }

  async getContact(id: number): Promise<Contact> {
    return this.request<Contact>(`/contacts/${id}`);
  }

  async createContact(data: Partial<Contact>): Promise<Contact> {
    return this.request<Contact>('/contacts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Usage
async function main() {
  const client = new FreshdeskClient(
    'yourcompany',
    process.env.FRESHDESK_API_KEY!
  );

  // List tickets
  const tickets = await client.listTickets();
  tickets.forEach(ticket => {
    console.log(`#${ticket.id}: ${ticket.subject}`);
  });

  // Create ticket
  const newTicket = await client.createTicket({
    subject: 'Support needed',
    description: 'Please help with this issue',
    email: 'customer@example.com',
    priority: 2,
    status: 2,
  });
  console.log(`Created ticket #${newTicket.id}`);

  // Update ticket
  await client.updateTicket(newTicket.id, { status: 4 });
  console.log('Ticket resolved');
}

main().catch(console.error);
```

---

## Common Integration Patterns

### Rate Limit Handling

```python
import time
from functools import wraps

def rate_limit_handler(max_retries=3, base_delay=1):
    """Decorator to handle rate limiting with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if '429' in str(e):
                        delay = base_delay * (2 ** retries)
                        print(f"Rate limited. Retrying in {delay}s...")
                        time.sleep(delay)
                        retries += 1
                    else:
                        raise
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator

@rate_limit_handler(max_retries=3)
def get_ticket(api, ticket_id):
    return api.tickets.get_ticket(ticket_id)
```

### Bulk Export

```python
import json
import time

def export_all_tickets(api, output_file='tickets.json'):
    """Export all tickets to JSON file"""
    all_tickets = []
    page = 1

    while True:
        tickets = api.tickets.list_tickets(page=page, per_page=100)
        if not tickets:
            break

        for ticket in tickets:
            all_tickets.append({
                'id': ticket.id,
                'subject': ticket.subject,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at
            })

        print(f"Exported page {page} ({len(all_tickets)} tickets)")
        page += 1
        time.sleep(0.5)  # Respect rate limits

    with open(output_file, 'w') as f:
        json.dump(all_tickets, f, indent=2, default=str)

    print(f"Exported {len(all_tickets)} tickets to {output_file}")
    return all_tickets
```

### Webhook Handler

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook/freshdesk', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Freshdesk-Signature')
    if signature:
        expected = hmac.new(
            WEBHOOK_SECRET.encode(),
            request.data,
            hashlib.sha256
        ).hexdigest()
        if signature != expected:
            return jsonify({'error': 'Invalid signature'}), 401

    payload = request.json.get('freshdesk_webhook', {})
    event = payload.get('triggered_event')

    # Route to handler
    handlers = {
        'ticket_created': handle_new_ticket,
        'ticket_status_updated': handle_status_change,
        'agent_reply_added': handle_agent_reply,
    }

    handler = handlers.get(event)
    if handler:
        handler(payload)

    return jsonify({'status': 'ok'})

def handle_new_ticket(payload):
    print(f"New ticket: #{payload['ticket_id']} - {payload['ticket_subject']}")

def handle_status_change(payload):
    print(f"Status changed: {payload['ticket_old_status']} -> {payload['ticket_new_status']}")

def handle_agent_reply(payload):
    print(f"Agent reply on #{payload['ticket_id']}")
```
