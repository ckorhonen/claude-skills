# Calendar Scheduling Reference

Complete reference for Google Calendar operations with `gog calendar`.

## Basic Commands

```bash
# List calendars
gog calendar calendars

# List events (defaults to upcoming)
gog calendar events [CALENDAR_ID]

# Create an event
gog calendar create CALENDAR_ID [options]

# Update an event
gog calendar update CALENDAR_ID EVENT_ID [options]

# Delete an event
gog calendar delete CALENDAR_ID EVENT_ID
```

## Calendar IDs

| ID | Description |
|----|-------------|
| `primary` | Your primary calendar |
| `email@domain.com` | Specific calendar by email |
| Calendar ID string | From `gog calendar calendars` output |

## Date/Time Formats

### RFC 3339 Format (Required)

Events use RFC 3339 datetime format:

```
YYYY-MM-DDTHH:MM:SS±HH:MM
```

### Examples

| Format | Example | Description |
|--------|---------|-------------|
| UTC | `2026-01-15T14:00:00Z` | Z suffix for UTC |
| With offset | `2026-01-15T14:00:00-08:00` | Pacific time |
| With offset | `2026-01-15T14:00:00+05:30` | India time |

### Common Time Zones

| Zone | Offset |
|------|--------|
| US Pacific (PST) | `-08:00` |
| US Pacific (PDT) | `-07:00` |
| US Mountain (MST) | `-07:00` |
| US Central (CST) | `-06:00` |
| US Eastern (EST) | `-05:00` |
| US Eastern (EDT) | `-04:00` |
| UTC/GMT | `+00:00` or `Z` |
| UK (GMT) | `+00:00` |
| UK (BST) | `+01:00` |
| Central Europe (CET) | `+01:00` |
| Central Europe (CEST) | `+02:00` |
| India (IST) | `+05:30` |
| Japan (JST) | `+09:00` |
| Australia Eastern (AEST) | `+10:00` |
| Australia Eastern (AEDT) | `+11:00` |

### All-Day Events

For all-day events, use date only (no time):

```bash
gog calendar create primary \
  --summary="Company Holiday" \
  --from="2026-01-20" \
  --to="2026-01-21" \
  --all-day
```

Note: `--to` date is exclusive (event ends at start of that day).

## Creating Events

### Basic Event

```bash
gog calendar create primary \
  --summary="Team Meeting" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00"
```

### Event with Location

```bash
gog calendar create primary \
  --summary="Client Meeting" \
  --from="2026-01-15T10:00:00-08:00" \
  --to="2026-01-15T11:00:00-08:00" \
  --location="Conference Room A, 123 Main St"
```

### Event with Google Meet

```bash
gog calendar create primary \
  --summary="Video Call" \
  --from="2026-01-15T09:00:00-08:00" \
  --to="2026-01-15T10:00:00-08:00" \
  --with-meet
```

### Event with Attendees

```bash
gog calendar create primary \
  --summary="Project Sync" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00" \
  --attendees="alice@company.com,bob@company.com,carol@company.com" \
  --with-meet
```

### Event with Description

```bash
gog calendar create primary \
  --summary="Quarterly Review" \
  --from="2026-01-15T13:00:00-08:00" \
  --to="2026-01-15T14:30:00-08:00" \
  --description="Agenda:
1. Q4 Results
2. Q1 Planning
3. Team Updates
4. Q&A

Please review the attached materials before the meeting."
```

### Event with Custom Reminders

```bash
gog calendar create primary \
  --summary="Important Meeting" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00" \
  --reminder="popup:15m" \
  --reminder="email:1d"
```

### Reminder Formats

| Format | Description |
|--------|-------------|
| `popup:Nm` | Popup N minutes before |
| `popup:Nh` | Popup N hours before |
| `popup:Nd` | Popup N days before |
| `email:Nm` | Email N minutes before |
| `email:Nh` | Email N hours before |
| `email:Nd` | Email N days before |

## Recurrence Rules (RRULE)

Create recurring events with `--rrule`:

### Basic Patterns

| Pattern | RRULE |
|---------|-------|
| Daily | `RRULE:FREQ=DAILY` |
| Weekly | `RRULE:FREQ=WEEKLY` |
| Monthly | `RRULE:FREQ=MONTHLY` |
| Yearly | `RRULE:FREQ=YEARLY` |

### With Count (End After N Occurrences)

```bash
# Weekly for 10 weeks
--rrule="RRULE:FREQ=WEEKLY;COUNT=10"
```

### With Until (End Date)

```bash
# Daily until specific date
--rrule="RRULE:FREQ=DAILY;UNTIL=20260301T000000Z"
```

### With Interval

```bash
# Every 2 weeks
--rrule="RRULE:FREQ=WEEKLY;INTERVAL=2"

# Every 3 months
--rrule="RRULE:FREQ=MONTHLY;INTERVAL=3"
```

### Specific Days (BYDAY)

| Day | Code |
|-----|------|
| Sunday | `SU` |
| Monday | `MO` |
| Tuesday | `TU` |
| Wednesday | `WE` |
| Thursday | `TH` |
| Friday | `FR` |
| Saturday | `SA` |

```bash
# Every Monday, Wednesday, Friday
--rrule="RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"

# Every Tuesday and Thursday
--rrule="RRULE:FREQ=WEEKLY;BYDAY=TU,TH"
```

### Monthly Patterns

```bash
# First Monday of each month
--rrule="RRULE:FREQ=MONTHLY;BYDAY=1MO"

# Last Friday of each month
--rrule="RRULE:FREQ=MONTHLY;BYDAY=-1FR"

# 15th of each month
--rrule="RRULE:FREQ=MONTHLY;BYMONTHDAY=15"
```

### Complete Recurring Event Example

```bash
gog calendar create primary \
  --summary="Weekly Team Standup" \
  --from="2026-01-13T09:00:00-08:00" \
  --to="2026-01-13T09:30:00-08:00" \
  --attendees="team@company.com" \
  --rrule="RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;COUNT=52" \
  --with-meet \
  --reminder="popup:5m"
```

## Event Visibility

| Value | Description |
|-------|-------------|
| `default` | Uses calendar default |
| `public` | Visible to everyone |
| `private` | Only you see details |
| `confidential` | Only see busy (no details) |

```bash
gog calendar create primary \
  --summary="1:1 with Manager" \
  --from="2026-01-15T11:00:00-08:00" \
  --to="2026-01-15T11:30:00-08:00" \
  --visibility="private"
```

## Event Transparency (Show As)

| Value | Description |
|-------|-------------|
| `opaque` | Show as busy (default) |
| `transparent` | Show as free |

Or use aliases:
- `--busy` = `--transparency=opaque`
- `--free` = `--transparency=transparent`

```bash
# Optional meeting, doesn't block calendar
gog calendar create primary \
  --summary="Optional Training Session" \
  --from="2026-01-15T15:00:00-08:00" \
  --to="2026-01-15T16:00:00-08:00" \
  --free
```

## Event Colors

| ID | Color |
|----|-------|
| 1 | Lavender |
| 2 | Sage |
| 3 | Grape |
| 4 | Flamingo |
| 5 | Banana |
| 6 | Tangerine |
| 7 | Peacock |
| 8 | Graphite |
| 9 | Blueberry |
| 10 | Basil |
| 11 | Tomato |

```bash
gog calendar create primary \
  --summary="High Priority Meeting" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00" \
  --event-color=11
```

List available colors:
```bash
gog calendar colors
```

## Guest Permissions

| Flag | Description |
|------|-------------|
| `--guests-can-invite` | Allow guests to add others |
| `--guests-can-modify` | Allow guests to edit event |
| `--guests-can-see-others` | Allow guests to see attendee list |

## Send Updates

| Value | Description |
|-------|-------------|
| `all` | Notify all attendees (default) |
| `externalOnly` | Only notify external attendees |
| `none` | Don't send notifications |

```bash
# Create without notifying
gog calendar create primary \
  --summary="Draft Meeting" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:00:00-08:00" \
  --attendees="team@company.com" \
  --send-updates=none
```

## Checking Availability

### Free/Busy Query

```bash
# Check availability for multiple people
gog calendar freebusy "alice@company.com,bob@company.com,carol@company.com" \
  --from="2026-01-15T09:00:00-08:00" \
  --to="2026-01-15T17:00:00-08:00"
```

### Find Conflicts

```bash
# Check your conflicts this week
gog calendar conflicts --week

# Check conflicts for next 14 days
gog calendar conflicts --days=14
```

### Team Calendars

```bash
# View team's calendars (for group email)
gog calendar team engineering@company.com --week
```

## Special Event Types

### Focus Time

```bash
gog calendar focus-time \
  --from="2026-01-16T09:00:00-08:00" \
  --to="2026-01-16T12:00:00-08:00"
```

### Out of Office

```bash
# Single day
gog calendar out-of-office \
  --from="2026-01-20" \
  --to="2026-01-21"

# Multiple days with message
gog calendar out-of-office \
  --from="2026-01-20" \
  --to="2026-01-25" \
  --summary="Vacation - limited availability"
```

Aliases: `ooo`

### Working Location

```bash
# Working from home
gog calendar working-location \
  --from="2026-01-17" \
  --to="2026-01-17" \
  --type="home"

# Working from office
gog calendar working-location \
  --from="2026-01-18" \
  --to="2026-01-18" \
  --type="office"
```

Aliases: `wl`

Location types: `home`, `office`, `customLocation`

## Responding to Invitations

```bash
# Accept
gog calendar respond primary EVENT_ID --status=accepted

# Decline
gog calendar respond primary EVENT_ID --status=declined

# Tentative
gog calendar respond primary EVENT_ID --status=tentative
```

## Listing Events

### Time-Based Listing

```bash
# Today's events
gog calendar events --today

# This week
gog calendar events --week

# All calendars
gog calendar events --all

# Custom range
gog calendar events \
  --from="2026-01-15T00:00:00Z" \
  --to="2026-01-31T23:59:59Z"
```

### Search Events

```bash
gog calendar search "project meeting"
```

## Updating Events

```bash
# Update summary
gog calendar update primary EVENT_ID \
  --summary="Updated Meeting Title"

# Update time
gog calendar update primary EVENT_ID \
  --from="2026-01-15T15:00:00-08:00" \
  --to="2026-01-15T16:00:00-08:00"

# Add attendees
gog calendar update primary EVENT_ID \
  --attendees="newperson@company.com"
```

## Deleting Events

```bash
# Delete event
gog calendar delete primary EVENT_ID

# Delete without confirmation
gog calendar delete primary EVENT_ID --force

# Delete and notify
gog calendar delete primary EVENT_ID --send-updates=all
```

## Output Formatting

```bash
# JSON for scripting
gog calendar events --today --json | jq '.[].summary'

# Get event IDs
gog calendar events --week --json | jq -r '.[].id'

# Plain output
gog calendar events --today --plain
```

## Complete Workflow Examples

### Schedule Team Meeting

```bash
# 1. Check team availability
gog calendar freebusy "alice@co.com,bob@co.com" \
  --from="2026-01-15T09:00:00-08:00" \
  --to="2026-01-15T17:00:00-08:00"

# 2. Create meeting at available slot
gog calendar create primary \
  --summary="Team Planning Session" \
  --from="2026-01-15T14:00:00-08:00" \
  --to="2026-01-15T15:30:00-08:00" \
  --attendees="alice@co.com,bob@co.com" \
  --description="Quarterly planning session.

Agenda:
- Review Q4 results
- Set Q1 priorities
- Assign ownership" \
  --with-meet \
  --reminder="popup:15m" \
  --reminder="email:1d"
```

### Setup Weekly Recurring 1:1

```bash
gog calendar create primary \
  --summary="1:1 with Direct Report" \
  --from="2026-01-13T10:00:00-08:00" \
  --to="2026-01-13T10:30:00-08:00" \
  --attendees="report@company.com" \
  --rrule="RRULE:FREQ=WEEKLY;BYDAY=MO" \
  --visibility="private" \
  --with-meet \
  --description="Standing 1:1 meeting.

Running notes: [link to doc]"
```

### Plan Focus Week

```bash
# Block morning focus time Mon-Fri
for day in 13 14 15 16 17; do
  gog calendar focus-time \
    --from="2026-01-${day}T09:00:00-08:00" \
    --to="2026-01-${day}T12:00:00-08:00"
done
```
