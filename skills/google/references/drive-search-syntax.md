# Google Drive Search Syntax Reference

Complete reference for Drive search queries used with `gog drive search` and `gog drive ls --query`.

## Basic Usage

```bash
# Full-text search
gog drive search "<query>"

# Query filter with ls
gog drive ls --query="<query>" --parent=FOLDER_ID
```

## Query Structure

Drive queries use a SQL-like syntax:
```
field operator value [and|or field operator value ...]
```

## File Name Operators

| Query | Description |
|-------|-------------|
| `name = 'filename.pdf'` | Exact filename match |
| `name contains 'report'` | Filename contains substring |
| `name != 'draft.docx'` | Filename does not match |

### Name Examples

```bash
# Find files containing "budget"
gog drive search "name contains 'budget'"

# Exact filename
gog drive search "name = 'Q4 Report.pdf'"

# Files starting with pattern (use fullText for content)
gog drive search "name contains '2026'"
```

## Full-Text Search

| Query | Description |
|-------|-------------|
| `fullText contains 'keyword'` | Content contains word |
| `fullText contains '"exact phrase"'` | Content contains exact phrase |

### Full-Text Examples

```bash
# Search document content
gog drive search "fullText contains 'quarterly revenue'"

# Exact phrase in content
gog drive search "fullText contains '\"action items\"'"

# Combine name and content
gog drive search "name contains 'meeting' and fullText contains 'budget'"
```

## MIME Type Filtering

### Common MIME Types

| Type | MIME Type |
|------|-----------|
| Google Doc | `application/vnd.google-apps.document` |
| Google Sheet | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Google Form | `application/vnd.google-apps.form` |
| Google Drawing | `application/vnd.google-apps.drawing` |
| Google Sites | `application/vnd.google-apps.site` |
| Google Apps Script | `application/vnd.google-apps.script` |
| Folder | `application/vnd.google-apps.folder` |
| Shortcut | `application/vnd.google-apps.shortcut` |

### Standard File Types

| Type | MIME Type |
|------|-----------|
| PDF | `application/pdf` |
| Word (.docx) | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Word (.doc) | `application/msword` |
| Excel (.xlsx) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| Excel (.xls) | `application/vnd.ms-excel` |
| PowerPoint (.pptx) | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| PowerPoint (.ppt) | `application/vnd.ms-powerpoint` |
| Plain text | `text/plain` |
| HTML | `text/html` |
| CSV | `text/csv` |
| JSON | `application/json` |
| XML | `application/xml` |
| ZIP | `application/zip` |

### Image Types

| Type | MIME Type |
|------|-----------|
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` |
| SVG | `image/svg+xml` |
| BMP | `image/bmp` |
| WEBP | `image/webp` |

### Video Types

| Type | MIME Type |
|------|-----------|
| MP4 | `video/mp4` |
| MOV | `video/quicktime` |
| AVI | `video/x-msvideo` |
| WEBM | `video/webm` |

### Audio Types

| Type | MIME Type |
|------|-----------|
| MP3 | `audio/mpeg` |
| WAV | `audio/wav` |
| OGG | `audio/ogg` |

### MIME Type Examples

```bash
# All Google Docs
gog drive search "mimeType = 'application/vnd.google-apps.document'"

# All PDFs
gog drive search "mimeType = 'application/pdf'"

# All spreadsheets (Google Sheets)
gog drive search "mimeType = 'application/vnd.google-apps.spreadsheet'"

# All folders
gog drive search "mimeType = 'application/vnd.google-apps.folder'"

# Not a folder (files only)
gog drive search "mimeType != 'application/vnd.google-apps.folder'"

# Images (multiple types)
gog drive search "mimeType contains 'image/'"
```

## Date Filters

### Date Fields

| Field | Description |
|-------|-------------|
| `modifiedTime` | When file was last modified |
| `createdTime` | When file was created |
| `viewedByMeTime` | When you last viewed it |

### Date Operators

| Operator | Example |
|----------|---------|
| `>` | `modifiedTime > '2026-01-01'` |
| `<` | `modifiedTime < '2026-01-01'` |
| `>=` | `modifiedTime >= '2026-01-01'` |
| `<=` | `modifiedTime <= '2026-01-01'` |
| `=` | `modifiedTime = '2026-01-01'` |
| `!=` | `modifiedTime != '2026-01-01'` |

### Date Format

Dates use RFC 3339 format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`

### Date Examples

```bash
# Modified in last week
gog drive search "modifiedTime > '2026-01-03'"

# Created this year
gog drive search "createdTime > '2026-01-01'"

# Not modified in 6 months
gog drive search "modifiedTime < '2025-07-01'"

# Specific date range
gog drive search "modifiedTime > '2026-01-01' and modifiedTime < '2026-01-31'"

# Recently viewed
gog drive search "viewedByMeTime > '2026-01-08'"
```

## Ownership & Sharing

### Owner Queries

| Query | Description |
|-------|-------------|
| `'email' in owners` | Owned by user |
| `'me' in owners` | Owned by you |

### Writer/Reader Queries

| Query | Description |
|-------|-------------|
| `'email' in writers` | User can edit |
| `'email' in readers` | User can view |

### Sharing Queries

| Query | Description |
|-------|-------------|
| `sharedWithMe` | Shared with you |
| `sharedWithMe = true` | Shared with you (explicit) |
| `sharedWithMe = false` | Not shared (you own it) |

### Visibility Queries

| Query | Description |
|-------|-------------|
| `visibility = 'anyoneCanFind'` | Publicly searchable |
| `visibility = 'anyoneWithLink'` | Anyone with link |
| `visibility = 'domainCanFind'` | Domain searchable |
| `visibility = 'domainWithLink'` | Domain with link |
| `visibility = 'limited'` | Specific people only |

### Ownership Examples

```bash
# Files I own
gog drive search "'me' in owners"

# Files owned by colleague
gog drive search "'alice@company.com' in owners"

# Files I can edit (not own)
gog drive search "'me' in writers and not 'me' in owners"

# Files shared with me
gog drive search "sharedWithMe"

# Files shared by specific person
gog drive search "'bob@company.com' in writers and sharedWithMe"
```

## Folder & Parent Queries

| Query | Description |
|-------|-------------|
| `'folderId' in parents` | Direct children of folder |
| `'root' in parents` | In root (My Drive top level) |

### Folder Examples

```bash
# Files in specific folder
gog drive search "'1ABC123xyz' in parents"

# Files in root
gog drive search "'root' in parents"

# PDFs in specific folder
gog drive search "'1ABC123xyz' in parents and mimeType = 'application/pdf'"

# Or use ls with --parent
gog drive ls --parent=1ABC123xyz
```

## Status Flags

| Query | Description |
|-------|-------------|
| `starred` or `starred = true` | Starred files |
| `starred = false` | Not starred |
| `trashed` or `trashed = true` | In trash |
| `trashed = false` | Not in trash |

### Status Examples

```bash
# Starred documents
gog drive search "starred and mimeType = 'application/vnd.google-apps.document'"

# Not trashed (explicit - usually default)
gog drive search "trashed = false and name contains 'report'"

# Find trashed files
gog drive search "trashed = true"
```

## Properties (Extended Metadata)

For files with custom properties:

| Query | Description |
|-------|-------------|
| `properties has { key='name' and value='value' }` | Has public property |
| `appProperties has { key='name' and value='value' }` | Has app-private property |

## Boolean Operators

| Operator | Example |
|----------|---------|
| `and` | `starred and mimeType = 'application/pdf'` |
| `or` | `mimeType = 'application/pdf' or mimeType = 'image/png'` |
| `not` | `not mimeType = 'application/vnd.google-apps.folder'` |

### Operator Precedence

1. `not` (highest)
2. `and`
3. `or` (lowest)

Use parentheses for complex queries (though not all implementations support them).

### Boolean Examples

```bash
# Docs OR Sheets
gog drive search "mimeType = 'application/vnd.google-apps.document' or mimeType = 'application/vnd.google-apps.spreadsheet'"

# Starred PDFs owned by me
gog drive search "starred and mimeType = 'application/pdf' and 'me' in owners"

# Not folders
gog drive search "not mimeType = 'application/vnd.google-apps.folder'"

# Shared docs or sheets
gog drive search "sharedWithMe and (mimeType = 'application/vnd.google-apps.document' or mimeType = 'application/vnd.google-apps.spreadsheet')"
```

## Complete Example Queries

### Personal Assistant Queries

```bash
# Recent documents I need to review (shared with me, recent)
gog drive search "sharedWithMe and modifiedTime > '2026-01-01'"

# All presentations for Q4 planning
gog drive search "mimeType = 'application/vnd.google-apps.presentation' and fullText contains 'Q4'"

# Contracts and agreements
gog drive search "(name contains 'contract' or name contains 'agreement') and mimeType = 'application/pdf'"

# Executive briefing materials
gog drive search "fullText contains 'executive briefing' and modifiedTime > '2025-12-01'"
```

### Project Organization Queries

```bash
# All Project Alpha files
gog drive search "fullText contains 'Project Alpha'"

# Budget spreadsheets
gog drive search "mimeType = 'application/vnd.google-apps.spreadsheet' and (name contains 'budget' or fullText contains 'budget')"

# Meeting notes from team
gog drive search "name contains 'meeting notes' and 'team@company.com' in writers"

# Design files (images and drawings)
gog drive search "mimeType contains 'image/' or mimeType = 'application/vnd.google-apps.drawing'"
```

### Cleanup & Organization Queries

```bash
# Large files (use metadata after search)
gog drive search "'me' in owners" --json | jq '.[] | select(.size > 10000000)'

# Old files not accessed
gog drive search "viewedByMeTime < '2025-01-01' and 'me' in owners"

# Duplicate detection (by name)
gog drive search "name contains 'copy of'"

# Orphaned files (no parent - careful with this)
# Better done via API, but can list root first
gog drive search "'root' in parents"
```

## Output Formatting

```bash
# JSON for scripting
gog drive search "starred" --json | jq '.[].name'

# Get file IDs
gog drive search "mimeType = 'application/pdf'" --json | jq '.[].id'

# Plain output
gog drive search "starred" --plain

# Limit results
gog drive search "fullText contains 'budget'" --max=10
```

## Combining with Other Commands

```bash
# Search and download first result
FILE_ID=$(gog drive search "name = 'report.pdf'" --json | jq -r '.[0].id')
gog drive download "$FILE_ID"

# Search and get URLs
gog drive search "starred" --json | jq -r '.[].webViewLink'

# Search and share
FILE_ID=$(gog drive search "name contains 'Q4 Report'" --json | jq -r '.[0].id')
gog drive share "$FILE_ID" --type=user --email=colleague@company.com --role=reader
```

## Performance Tips

1. **Use specific MIME types** - Faster than content search
2. **Add date filters** - Narrows scope significantly
3. **Use `'me' in owners`** - Faster than searching all shared
4. **Avoid `fullText`** on large corpora - Slower, use name first
5. **Use folder parents** - Search within specific folders
6. **Limit results** - Use `--max` when exploring
