# Gmail Search Syntax Reference

Complete reference for Gmail search operators used with `gog gmail search`.

## Basic Usage

```bash
gog gmail search "<query>" [--max=N] [--oldest] [--page=TOKEN]
```

## Sender & Recipient Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:alice@example.com` | Messages from sender |
| `to:` | `to:team@example.com` | Messages sent to recipient |
| `cc:` | `cc:manager@example.com` | Messages where recipient is CC'd |
| `bcc:` | `bcc:archive@example.com` | Messages where recipient is BCC'd |
| `deliveredto:` | `deliveredto:alias@example.com` | Delivered to address (for aliases) |
| `replyto:` | `replyto:support@example.com` | Reply-To header matches |

### Sender/Recipient Tips

```bash
# From multiple senders (OR)
gog gmail search "from:alice@example.com OR from:bob@example.com"

# Using braces shorthand
gog gmail search "{from:alice@example.com from:bob@example.com}"

# From domain
gog gmail search "from:@company.com"

# Exclude sender
gog gmail search "-from:noreply@example.com"
```

## Message Status

| Operator | Example | Description |
|----------|---------|-------------|
| `is:unread` | `is:unread` | Unread messages |
| `is:read` | `is:read` | Read messages |
| `is:starred` | `is:starred` | Starred messages |
| `is:important` | `is:important` | Marked as important |
| `is:snoozed` | `is:snoozed` | Snoozed messages |
| `is:muted` | `is:muted` | Muted conversations |

### Star Colors

| Operator | Description |
|----------|-------------|
| `has:yellow-star` | Yellow star |
| `has:orange-star` | Orange star |
| `has:red-star` | Red star |
| `has:purple-star` | Purple star |
| `has:blue-star` | Blue star |
| `has:green-star` | Green star |
| `has:red-bang` | Red exclamation |
| `has:orange-guillemet` | Orange double angle |
| `has:yellow-bang` | Yellow exclamation |
| `has:green-check` | Green check |
| `has:blue-info` | Blue info |
| `has:purple-question` | Purple question |

## Location Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `in:inbox` | `in:inbox` | In inbox |
| `in:sent` | `in:sent` | In sent folder |
| `in:drafts` | `in:drafts` | In drafts |
| `in:spam` | `in:spam` | In spam folder |
| `in:trash` | `in:trash` | In trash |
| `in:chats` | `in:chats` | Chat messages |
| `in:anywhere` | `in:anywhere` | All mail (including spam/trash) |
| `label:` | `label:work/projects` | Has specific label (use / for nested) |

### Label Examples

```bash
# Simple label
gog gmail search "label:work"

# Nested label
gog gmail search "label:work/important"

# Multiple labels (AND)
gog gmail search "label:work label:urgent"

# Either label (OR)
gog gmail search "label:work OR label:personal"

# Without label
gog gmail search "-label:processed"
```

## Content Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `subject:` | `subject:meeting` | Word in subject |
| `"phrase"` | `"quarterly report"` | Exact phrase anywhere |
| `+word` | `+run` | Exact word match (no stemming) |
| `-word` | `-newsletter` | Exclude word |
| `AROUND` | `meeting AROUND 5 budget` | Words within N words of each other |

### Subject Search Tips

```bash
# Subject contains exact phrase
gog gmail search "subject:\"project update\""

# Subject contains any of these words
gog gmail search "subject:(urgent OR important OR asap)"

# Subject excludes word
gog gmail search "subject:report -subject:weekly"
```

## Attachment Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `has:attachment` | `has:attachment` | Has any attachment |
| `has:drive` | `has:drive` | Has Google Drive attachment |
| `has:document` | `has:document` | Has Google Doc attachment |
| `has:spreadsheet` | `has:spreadsheet` | Has Google Sheet attachment |
| `has:presentation` | `has:presentation` | Has Google Slides attachment |
| `has:youtube` | `has:youtube` | Contains YouTube link |
| `filename:` | `filename:pdf` | Attachment filename or extension |

### Attachment Examples

```bash
# Any PDF attachment
gog gmail search "has:attachment filename:pdf"

# Specific filename
gog gmail search "filename:report.xlsx"

# Image attachments
gog gmail search "filename:jpg OR filename:png OR filename:gif"

# Large attachments
gog gmail search "has:attachment larger:5M"
```

## Date Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `newer_than:` | `newer_than:7d` | Within last N units |
| `older_than:` | `older_than:1y` | Older than N units |
| `after:` | `after:2026/01/01` | After specific date |
| `before:` | `before:2026/12/31` | Before specific date |
| `newer:` | `newer:2026/01/01` | Same as after: |
| `older:` | `older:2026/01/01` | Same as before: |

### Time Units for newer_than/older_than

| Unit | Meaning |
|------|---------|
| `d` | Days |
| `m` | Months |
| `y` | Years |

### Date Format

Dates use `YYYY/MM/DD` format.

### Date Examples

```bash
# Last week
gog gmail search "newer_than:7d"

# Last 3 months
gog gmail search "newer_than:3m"

# Specific date range
gog gmail search "after:2026/01/01 before:2026/01/31"

# Last year but not last month
gog gmail search "older_than:1m newer_than:1y"
```

## Size Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `larger:` | `larger:5M` | Larger than size |
| `smaller:` | `smaller:100K` | Smaller than size |
| `size:` | `size:1M` | Approximately this size |

### Size Units

| Unit | Meaning |
|------|---------|
| (none) | Bytes |
| `K` | Kilobytes |
| `M` | Megabytes |

### Size Examples

```bash
# Large emails (> 10MB)
gog gmail search "larger:10M"

# Small emails (< 50KB)
gog gmail search "smaller:50K"

# Large attachments from specific sender
gog gmail search "from:colleague@example.com has:attachment larger:5M"
```

## Category Operators

Gmail automatically categorizes messages:

| Operator | Description |
|----------|-------------|
| `category:primary` | Primary inbox |
| `category:social` | Social networks |
| `category:promotions` | Marketing/promotions |
| `category:updates` | Notifications/updates |
| `category:forums` | Forums/mailing lists |
| `category:reservations` | Travel reservations |
| `category:purchases` | Order confirmations |

### Category Examples

```bash
# Unread excluding promotions
gog gmail search "is:unread -category:promotions -category:social"

# Only primary inbox
gog gmail search "category:primary is:unread"

# Find purchase receipts
gog gmail search "category:purchases newer_than:30d"
```

## Boolean Operators

| Operator | Example | Description |
|----------|---------|-------------|
| (space) | `from:alice subject:meeting` | AND (implicit) |
| `AND` | `from:alice AND subject:meeting` | AND (explicit) |
| `OR` | `from:alice OR from:bob` | Either condition |
| `-` | `-from:noreply` | NOT (exclude) |
| `()` | `(from:alice OR from:bob) is:unread` | Grouping |
| `{}` | `{from:alice from:bob}` | OR shorthand |

### Boolean Examples

```bash
# Complex query with grouping
gog gmail search "(from:alice OR from:bob) subject:project is:unread"

# Exclude multiple
gog gmail search "is:unread -from:noreply -category:promotions -category:updates"

# Using braces for OR
gog gmail search "{from:alice@example.com from:bob@example.com to:team@example.com}"
```

## Special Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `list:` | `list:team@googlegroups.com` | Mailing list messages |
| `Rfc822msgid:` | `Rfc822msgid:<id>` | Message-ID header |
| `has:userlabels` | `has:userlabels` | Has user-created label |
| `has:nouserlabels` | `has:nouserlabels` | No user labels |

## Complete Example Queries

### Executive Assistant Queries

```bash
# VIP inbox triage
gog gmail search "is:unread from:(ceo@company.com OR cfo@company.com OR board@company.com) newer_than:24h" --max=20

# Action required emails
gog gmail search "is:unread subject:(\"action required\" OR \"please review\" OR \"needs approval\" OR \"for your review\")"

# Meeting-related emails today
gog gmail search "newer_than:1d subject:(meeting OR calendar OR invite OR schedule)"

# Contracts awaiting signature
gog gmail search "subject:(contract OR agreement OR NDA) has:attachment filename:pdf newer_than:30d"
```

### Inbox Cleanup Queries

```bash
# Large old attachments
gog gmail search "has:attachment larger:10M older_than:6m"

# Old unread newsletters
gog gmail search "is:unread category:promotions older_than:30d"

# Old social notifications
gog gmail search "category:social older_than:90d"
```

### Project Tracking Queries

```bash
# All emails about Project Alpha
gog gmail search "\"Project Alpha\" newer_than:6m"

# Thread with specific participants
gog gmail search "from:client@example.com to:team@company.com subject:project"

# Files shared about budget
gog gmail search "has:drive \"budget\" newer_than:3m"
```

## Output Formatting

```bash
# JSON for scripting
gog gmail search "is:unread" --json | jq '.[].snippet'

# Plain TSV for parsing
gog gmail search "is:unread" --plain

# Limit results
gog gmail search "is:unread" --max=10

# Paginate
gog gmail search "is:unread" --max=25 --page=TOKEN
```

## Performance Tips

1. **Use date filters** - Dramatically reduces search time
2. **Be specific** - More operators = faster narrowing
3. **Limit results** - Use `--max` when exploring
4. **Avoid `in:anywhere`** - Searches spam/trash, slower
5. **Use labels** - Pre-filtered, faster than search
