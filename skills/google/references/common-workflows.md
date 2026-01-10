# Common PA/CoS Workflows

Extended workflow recipes for Personal Assistant and Chief of Staff tasks using `gog`.

## Daily Operations

### Executive Morning Briefing Prep

```bash
#!/bin/bash
# Prepare morning briefing materials

echo "=== INBOX SUMMARY ==="

# Count unread by priority
echo "Unread from VIPs:"
gog gmail search "is:unread from:(ceo@company.com OR cfo@company.com OR board@company.com)" --max=50 --json | jq 'length'

echo "Action Required emails:"
gog gmail search "is:unread subject:(\"action required\" OR \"please review\" OR \"approval needed\")" --max=20

echo ""
echo "=== TODAY'S CALENDAR ==="
gog calendar events --today

echo ""
echo "=== CONFLICTS THIS WEEK ==="
gog calendar conflicts --week

echo ""
echo "=== PENDING TASKS ==="
gog tasks list @default --max=20
```

### End-of-Day Email Cleanup

```bash
# Archive processed newsletters
gog gmail search "category:promotions is:unread older_than:7d" --json | \
  jq -r '.[].threadId' | \
  xargs -I {} gog gmail thread modify {} --remove-labels=INBOX

# Star important unread for tomorrow
gog gmail search "is:unread in:inbox -category:promotions -category:social -category:updates" --max=10

# Check what needs response
gog gmail search "is:unread from:@company.com newer_than:1d" --max=20
```

### Weekly Calendar Review

```bash
#!/bin/bash
# Weekly calendar prep script

echo "=== NEXT WEEK'S SCHEDULE ==="
# Assuming Monday is 2026-01-13
gog calendar events \
  --from="2026-01-13T00:00:00Z" \
  --to="2026-01-17T23:59:59Z" \
  --all

echo ""
echo "=== SCHEDULING CONFLICTS ==="
gog calendar conflicts --days=7

echo ""
echo "=== TEAM AVAILABILITY ==="
gog calendar team leadership@company.com --week

echo ""
echo "=== SUGGESTED FOCUS BLOCKS ==="
# Find gaps for focus time
gog calendar freebusy "primary" \
  --from="2026-01-13T09:00:00-08:00" \
  --to="2026-01-17T17:00:00-08:00"
```

## Meeting Management

### Schedule a Multi-Party Meeting

Complete workflow for scheduling meetings with multiple attendees:

```bash
# Step 1: Check availability for all participants
gog calendar freebusy \
  "executive1@company.com,executive2@company.com,stakeholder@partner.com" \
  --from="2026-01-15T09:00:00-08:00" \
  --to="2026-01-15T17:00:00-08:00"

# Step 2: Check your own calendar for conflicts
gog calendar events --from="2026-01-15T00:00:00Z" --to="2026-01-15T23:59:59Z"

# Step 3: Create the meeting
gog calendar create primary \
  --summary="Quarterly Business Review" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:30:00-08:00" \
  --attendees="executive1@company.com,executive2@company.com,stakeholder@partner.com" \
  --location="Main Conference Room" \
  --description="Q4 Business Review

AGENDA:
1. Financial overview (15 min)
2. Key initiatives update (30 min)
3. Q1 planning preview (30 min)
4. Q&A (15 min)

Pre-read materials: [Drive link]" \
  --with-meet \
  --reminder="popup:15m" \
  --reminder="email:1d"

# Step 4: Send calendar hold notification
gog gmail send \
  --to="executive1@company.com,executive2@company.com,stakeholder@partner.com" \
  --subject="Calendar Hold: Quarterly Business Review - Jan 15, 2pm PT" \
  --body="Hi all,

I've scheduled our Quarterly Business Review for Wednesday, January 15th at 2:00 PM Pacific.

Duration: 90 minutes
Location: Main Conference Room (Google Meet link in calendar invite)

Agenda and pre-read materials will be shared 48 hours before the meeting.

Please let me know if you have any conflicts.

Best regards"
```

### Reschedule a Meeting

```bash
# Step 1: Find the event
gog calendar search "Quarterly Business Review" --json | jq '.[0].id'

# Step 2: Check new time availability
gog calendar freebusy \
  "executive1@company.com,executive2@company.com" \
  --from="2026-01-16T09:00:00-08:00" \
  --to="2026-01-16T17:00:00-08:00"

# Step 3: Update the event
gog calendar update primary EVENT_ID \
  --from="2026-01-16T14:00:00-08:00" \
  --to="2026-01-16T15:30:00-08:00" \
  --send-updates=all

# Step 4: Send update notification
gog gmail send \
  --to="executive1@company.com,executive2@company.com" \
  --subject="Meeting Rescheduled: Quarterly Business Review - Now Jan 16" \
  --body="Hi all,

Our Quarterly Business Review has been moved to Thursday, January 16th at 2:00 PM Pacific.

Updated calendar invites have been sent.

Apologies for any inconvenience.

Best regards"
```

### Cancel a Meeting

```bash
# Step 1: Get event ID
EVENT_ID=$(gog calendar search "Quarterly Business Review" --json | jq -r '.[0].id')

# Step 2: Delete with notifications
gog calendar delete primary "$EVENT_ID" --send-updates=all

# Step 3: Send cancellation email
gog gmail send \
  --to="executive1@company.com,executive2@company.com" \
  --subject="Meeting Cancelled: Quarterly Business Review" \
  --body="Hi all,

Unfortunately, we need to cancel the Quarterly Business Review originally scheduled for this week.

We will send a new invite once we've identified an alternative time that works for everyone.

Apologies for any inconvenience.

Best regards"
```

## Travel Coordination

### Book Travel Calendar Blocks

```bash
# Create travel day blocks
gog calendar create primary \
  --summary="Travel - SFO to NYC" \
  --from="2026-01-20" \
  --to="2026-01-21" \
  --all-day \
  --description="Flight: UA123 departing 7:00am
Arriving: 3:30pm ET
Hotel: NYC Grand, confirmation #12345"

# Block travel time
gog calendar create primary \
  --summary="In Transit - Limited Availability" \
  --from="2026-01-20T07:00:00-08:00" \
  --to="2026-01-20T15:30:00-05:00" \
  --visibility="private" \
  --description="In flight - no WiFi expected"
```

### Out of Office Setup

```bash
# Set OOO in calendar
gog calendar out-of-office \
  --from="2026-01-20" \
  --to="2026-01-25" \
  --summary="Out of Office - Client Visit NYC"

# Search for meetings that need rescheduling
gog calendar events \
  --from="2026-01-20T00:00:00Z" \
  --to="2026-01-25T23:59:59Z"

# Decline meetings with message (manual per meeting)
gog calendar respond primary EVENT_ID --status=declined
```

## Document Management

### Project Document Roundup

```bash
#!/bin/bash
# Gather all documents for a project

PROJECT="Project Alpha"

echo "=== GOOGLE DOCS ==="
gog drive search "mimeType = 'application/vnd.google-apps.document' and fullText contains '$PROJECT'" --max=50

echo ""
echo "=== GOOGLE SHEETS ==="
gog drive search "mimeType = 'application/vnd.google-apps.spreadsheet' and fullText contains '$PROJECT'" --max=50

echo ""
echo "=== PRESENTATIONS ==="
gog drive search "mimeType = 'application/vnd.google-apps.presentation' and fullText contains '$PROJECT'" --max=50

echo ""
echo "=== PDFS ==="
gog drive search "mimeType = 'application/pdf' and (name contains '$PROJECT' or fullText contains '$PROJECT')" --max=50

echo ""
echo "=== RECENT CHANGES (last 7 days) ==="
gog drive search "fullText contains '$PROJECT' and modifiedTime > '$(date -v-7d +%Y-%m-%d)'" --max=20
```

### Weekly Report Compilation

```bash
# Find all reports from team members
gog drive search "name contains 'weekly report' and modifiedTime > '$(date -v-7d +%Y-%m-%d)'" --max=20

# Or search by owner
gog drive search "'team-member@company.com' in owners and name contains 'report' and modifiedTime > '$(date -v-7d +%Y-%m-%d)'"

# Download reports as PDFs
for id in $(gog drive search "name contains 'weekly report'" --json | jq -r '.[].id'); do
  gog docs export "$id" --format=pdf --output="./reports/${id}.pdf"
done
```

### Share Documents with Team

```bash
# Share a folder with team
FOLDER_ID="1ABC123xyz"
gog drive share "$FOLDER_ID" \
  --type=user \
  --email="team@company.com" \
  --role=writer

# Share document as read-only
gog drive share "$DOC_ID" \
  --type=user \
  --email="external@partner.com" \
  --role=reader

# Get shareable link
gog drive url "$DOC_ID"
```

## Contact & Communication

### Lookup Contact Before Call

```bash
# Search for contact
gog contacts search "Jane Smith"

# Get full details
gog contacts get RESOURCE_NAME

# Search directory (Workspace)
gog contacts directory search "Jane Smith"
```

### Group Communication

```bash
# Find all members of a group
gog groups members marketing@company.com

# Send to group
gog gmail send \
  --to="marketing@company.com" \
  --subject="Q1 Marketing Planning" \
  --body="Hi team,

Attached please find the Q1 marketing planning document.

Please review and add your comments by EOD Friday.

Thanks!"
```

### VIP Email Monitoring

```bash
# Monitor VIP inbox continuously
VIP_LIST="ceo@company.com,cfo@company.com,board@company.com,investor@vc.com"

# Check for new VIP emails
gog gmail search "is:unread from:($VIP_LIST)" --max=10

# Check for mentions
gog gmail search "is:unread \"@yourname\"" --max=10

# Urgent VIP emails
gog gmail search "is:unread from:($VIP_LIST) subject:(urgent OR asap OR important)"
```

## Task Management

### Daily Task Review

```bash
#!/bin/bash
# Daily task management routine

echo "=== OVERDUE TASKS ==="
gog tasks list @default --due-max="$(date -u +%Y-%m-%dT00:00:00Z)"

echo ""
echo "=== DUE TODAY ==="
gog tasks list @default \
  --due-min="$(date -u +%Y-%m-%dT00:00:00Z)" \
  --due-max="$(date -u +%Y-%m-%dT23:59:59Z)"

echo ""
echo "=== DUE THIS WEEK ==="
gog tasks list @default \
  --due-max="$(date -v+7d -u +%Y-%m-%dT23:59:59Z)"

echo ""
echo "=== ALL INCOMPLETE ==="
gog tasks list @default --max=50
```

### Convert Email to Task

```bash
# After reading an email that needs follow-up
# Get the email details
gog gmail get MESSAGE_ID --json | jq '.snippet, .payload.headers[] | select(.name=="Subject") | .value'

# Create task with reference
gog tasks add @default \
  --title="Follow up: [Subject from email]" \
  --due="2026-01-17" \
  --notes="Reference email: https://mail.google.com/mail/u/0/#inbox/MESSAGE_ID

Action items:
- Item 1
- Item 2"
```

### Batch Task Creation

```bash
# Create multiple tasks from a list
TASKS=(
  "Review Q4 financials"
  "Prepare board presentation"
  "Schedule team 1:1s"
  "Update project tracker"
)

for task in "${TASKS[@]}"; do
  gog tasks add @default --title="$task" --due="2026-01-20"
done
```

## Reporting & Analysis

### Email Volume Report

```bash
#!/bin/bash
# Weekly email volume analysis

echo "=== EMAIL VOLUME REPORT ==="
echo ""

echo "Received this week:"
gog gmail search "newer_than:7d in:inbox" --json | jq 'length'

echo ""
echo "By sender (top 10):"
gog gmail search "newer_than:7d" --json | \
  jq -r '.[].payload.headers[] | select(.name=="From") | .value' | \
  sort | uniq -c | sort -rn | head -10

echo ""
echo "Unread:"
gog gmail search "is:unread" --json | jq 'length'

echo ""
echo "Unread by category:"
for cat in primary social promotions updates forums; do
  count=$(gog gmail search "is:unread category:$cat" --json | jq 'length')
  echo "  $cat: $count"
done
```

### Calendar Utilization

```bash
#!/bin/bash
# Analyze calendar usage

echo "=== CALENDAR UTILIZATION ==="
echo ""

echo "Events this week:"
gog calendar events --week --json | jq 'length'

echo ""
echo "By type:"
gog calendar events --week --json | jq -r '.[].eventType' | sort | uniq -c

echo ""
echo "Total meeting hours:"
# Would need more complex calculation

echo ""
echo "Conflicts:"
gog calendar conflicts --week
```

## Integration Patterns

### Email → Calendar → Task

```bash
# 1. Find meeting request email
gog gmail search "subject:\"meeting request\" is:unread" --max=5

# 2. Parse details and create calendar event
gog calendar create primary \
  --summary="Meeting: [Parsed subject]" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00" \
  --attendees="requester@company.com"

# 3. Create follow-up task
gog tasks add @default \
  --title="Prepare for meeting: [Subject]" \
  --due="2026-01-14" \
  --notes="Meeting on Jan 15 at 2pm

Prep:
- Review background materials
- Prepare talking points"

# 4. Reply to confirm
gog gmail send \
  --reply-to-message-id=MESSAGE_ID \
  --body="Thanks for reaching out. I've scheduled our meeting for January 15th at 2pm PT. Calendar invite sent.

Looking forward to speaking with you."
```

### Drive → Email Attachment

```bash
# Find document in Drive
FILE_ID=$(gog drive search "name = 'Q4 Report Final.pdf'" --json | jq -r '.[0].id')

# Download locally
gog drive download "$FILE_ID" --output="/tmp/Q4_Report.pdf"

# Send with attachment
gog gmail send \
  --to="executive@company.com" \
  --subject="Q4 Report - Final" \
  --body="Hi,

Please find attached the final Q4 report as discussed.

Let me know if you have any questions.

Best regards" \
  --attach="/tmp/Q4_Report.pdf"
```

### Sheets Data → Email

```bash
# Get data from sheet
SPREADSHEET_ID="1ABC123xyz"
DATA=$(gog sheets get "$SPREADSHEET_ID" "Summary!A1:D10" --json)

# Format and send
gog gmail send \
  --to="team@company.com" \
  --subject="Weekly Metrics Summary" \
  --body="Hi team,

Here are this week's key metrics:

$(echo "$DATA" | jq -r '.values[] | join(" | ")')

Full dashboard: https://docs.google.com/spreadsheets/d/$SPREADSHEET_ID

Best regards"
```
