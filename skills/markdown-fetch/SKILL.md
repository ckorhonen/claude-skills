---
name: markdown-fetch
description: Fetch and extract web content as clean Markdown when provided with URLs. Use this skill whenever a user provides a URL (http/https link) that needs to be read, analyzed, summarized, or extracted. Converts web pages to Markdown with 80% fewer tokens than raw HTML. Handles all content types including JS-heavy sites, documentation, articles, and blog posts. Supports three conversion methods (auto, AI, browser rendering). Always use this instead of web_fetch when working with URLs - it's more efficient and provides cleaner output.
---

# Markdown Fetch

Efficiently fetch web content as clean Markdown using the markdown.new service.

## Why Use This

- **80% fewer tokens** than raw HTML
- **5x more content** fits in context window  
- **No external dependencies** or parsing libraries needed
- **Three-tier conversion** (Markdown-first, AI fallback, browser rendering)

## Triggering

This skill should trigger automatically when:
- User provides a URL (e.g., "Read https://example.com")
- User asks to extract/fetch/analyze web content
- User requests summarization of a webpage
- User needs to process article/blog/documentation URLs

## Quick Start

```bash
# Fetch any URL
scripts/fetch.sh "https://example.com"

# Use browser rendering for JS-heavy sites
scripts/fetch.sh "https://example.com" --method browser

# Retain images in output
scripts/fetch.sh "https://example.com" --retain-images
```

## Typical Usage Patterns

When a user says:
- "Read this article: https://..." → Use this skill to fetch the content
- "Summarize https://..." → Fetch with this skill first, then summarize
- "What does this page say: https://..." → Fetch the content
- "Extract the text from https://..." → Use this skill

## Conversion Methods

**auto** (default) - Try Markdown-first, fall back to AI or browser as needed  
**ai** - Use Cloudflare Workers AI for conversion  
**browser** - Full browser rendering for JS-heavy content

## Options

`--method <auto|ai|browser>` - Conversion method  
`--retain-images` - Keep image references in output  
`--output <file>` - Save to file instead of stdout

## Output

Returns clean Markdown with metadata:

```markdown
---
title: Page Title
url: https://example.com
method: auto
duration_ms: 725
fetched_at: 2026-03-07T12:00:00Z
---

# Content here...
```

## When to Use

- Extracting articles, documentation, or blog posts
- Building RAG pipelines with web content
- Summarizing web pages
- Fetching content for analysis
- Converting sites to Markdown format

## Implementation Notes

The service handles:
- Content negotiation (Accept: text/markdown)
- Cloudflare Workers AI conversion
- Browser rendering for dynamic content
- Automatic fallback between methods

## Common Pitfalls

### HTML Parsing Failures

**Symptom:** Empty output, truncated content, or "Error: No content in response"

**Root Causes:**
- CSS selectors broken by page layout changes
- Dynamic content not rendered by default (use `--method browser`)
- Page structure uses unusual HTML patterns (iframes, shadow DOM, Web Components)

**Debugging & Workarounds:**
```bash
# 1. Check if the page loads at all
curl -s "https://example.com" | head -c 500

# 2. Try browser rendering (handles JS-heavy sites)
scripts/fetch.sh "https://example.com" --method browser

# 3. Check what the service is getting
scripts/fetch.sh "https://example.com" 2>&1 | head -20

# 4. If still empty, the page may use iframes or require auth
```

**Best Practice:** Always use `--method browser` for single-page apps, social platforms, or content-heavy dashboards.

---

### Rate Limiting & IP Blocks

**Symptom:** HTTP 429 (Too Many Requests), 403 (Forbidden), or connection timeouts

**Root Causes:**
- Multiple rapid requests to same domain
- Service IP address blacklisted by the target site
- Bot detection triggering (User-Agent headers, request patterns)
- Cloudflare/WAF blocks (common on high-traffic sites)

**Debugging & Workarounds:**
```bash
# 1. Check HTTP status code
curl -s -w "\n%{http_code}\n" -o /dev/null "https://example.com"

# 2. Test with curl directly (bypasses service)
curl -H "User-Agent: Mozilla/5.0" "https://example.com" | head -c 500

# 3. Add delays between requests (if fetching multiple URLs)
for url in url1 url2 url3; do
  scripts/fetch.sh "$url"
  sleep 5  # Wait 5 seconds between requests
done

# 4. If blocked, try from different IP or use residential proxy
# For markdown.new service: no built-in proxy rotation; consider mirror services
```

**Best Practice:** Respect site robots.txt and use sensible request delays when processing multiple pages. Some sites require retry-after headers.

---

### Encoding Issues

**Symptom:** Garbled text, mojibake (weird characters), missing non-ASCII content (emojis, accents, CJK)

**Root Causes:**
- Page declares wrong charset in headers vs actual content
- Service not respecting Content-Type charset declaration
- UTF-8 vs Latin-1 mismatch
- Emoji or special symbols stripped during conversion

**Debugging & Workarounds:**
```bash
# 1. Check the page's declared charset
curl -sI "https://example.com" | grep -i "charset"

# 2. Save raw HTML and inspect encoding
curl -s "https://example.com" > raw.html
file raw.html
head -c 200 raw.html | od -c  # Show raw bytes

# 3. Try the markdown.new service and check output
scripts/fetch.sh "https://example.com" | file -  # Check output encoding

# 4. If output is garbled, convert explicitly
scripts/fetch.sh "https://example.com" | iconv -f UTF-8 -t UTF-8 > fixed.md
```

**Best Practice:** Always verify output is valid UTF-8. If encountering garbled content, the page likely has a charset mismatch — notify the site owner or use `--method browser` (more robust).

---

### JavaScript-Rendered Content

**Symptom:** Page returns but content is missing, loads as empty, or shows loading spinners instead of data

**Root Causes:**
- Page uses client-side JavaScript to render content (React, Vue, Angular, etc.)
- Default `auto` method only fetches HTML skeleton without executing JS
- Content loaded after page render (lazy loading, infinite scroll)
- JavaScript requires authentication or API keys

**Debugging & Workarounds:**
```bash
# 1. Fetch with browser rendering (executes JS)
scripts/fetch.sh "https://example.com" --method browser

# 2. Check what the auto method returns
scripts/fetch.sh "https://example.com" --method auto

# 3. Inspect page source to confirm JS-rendering
curl -s "https://example.com" | grep -i "react\|vue\|angular\|<div id=\"app\""

# 4. If content still missing, page may require interaction
# (e.g., clicking buttons, scrolling) — no workaround in current service
```

**Best Practice:** Use `--method browser` by default for modern web apps, news sites, and any site built in the last 5 years. The `auto` method is faster but misses JS-rendered content.

---

### Authentication & Paywall Content

**Symptom:** Returns login page instead of content, shows "Subscribe to read more", or HTTP 401/403

**Root Causes:**
- Page requires login/authentication
- Content behind paywall (subscription, membership)
- IP-based access restrictions (geo-blocking)
- Session-based authentication (cookies) not provided

**Debugging & Workarounds:**
```bash
# 1. Check if curl can access without auth
curl -s "https://example.com/article" | head -c 300

# 2. Identify authentication method
curl -sI "https://example.com" | grep -i "auth\|set-cookie\|www-authenticate"

# 3. Try public/preview version if available
# For paywalled sites, look for preview URLs or RSS feeds
curl -s "https://example.com/rss" | head -c 500

# 4. Check for paywall indicators
curl -s "https://example.com/article" | grep -i "paywall\|subscribe\|login required"

# 5. If member-only, request your credentials in the conversation
# (Don't embed in scripts — use prompt)
```

**Best Practice:** This skill cannot bypass authentication or paywalls by design. For protected content:
- Use public preview links if available
- Ask the user for authenticated access
- Try RSS feeds (often unpaywalled summaries)
- Check archive services (archive.org, 12ft.io for paywalled content) separately

---

### Service-Side Failures

**Symptom:** HTTP error codes (5xx), timeout, or malformed JSON responses

**Root Causes:**
- markdown.new service is down or overloaded
- Request body malformed (invalid URL, missing required fields)
- Service response is corrupted or incomplete
- Cloudflare Workers timeout (pages >10MB or slow servers)

**Debugging & Workarounds:**
```bash
# 1. Check service health
curl -s "https://markdown.new/health" 2>&1 | head

# 2. Verify request format
jq -n --arg url "https://example.com" --arg method "auto" \
  '{url: $url, method: $method, retain_images: false}' | jq .

# 3. Retry with exponential backoff
for attempt in {1..3}; do
  result=$(scripts/fetch.sh "https://example.com" 2>&1)
  if [[ $? -eq 0 ]]; then
    echo "$result"
    break
  fi
  sleep $((2 ** attempt))  # 2s, 4s, 8s
done

# 4. If service is down, no workaround available
# — try again later or use alternative (curl, browser, etc.)
```

**Best Practice:** The service is stateless and generally reliable. If failures persist, fall back to `curl` directly or ask the user for an alternative source.

---

## Troubleshooting Decision Tree

```
No content returned?
  ├─ Check if site requires JavaScript
  │   └─ YES → Use --method browser
  │   └─ NO → Continue
  ├─ Check if site requires authentication
  │   └─ YES → Use authenticated request (see Paywall section)
  │   └─ NO → Continue
  ├─ Check for encoding issues
  │   └─ YES → Garbled text → likely site charset mismatch
  │   └─ NO → Continue
  └─ Service may be down → Wait and retry

Getting rate-limited (HTTP 429)?
  ├─ Add delays between requests (5-10 seconds)
  └─ If persistent, try different time or request fewer pages

Truncated or broken output?
  └─ Try --method browser (more robust but slower)

Can't access paywalled content?
  └─ No workaround — try public preview, RSS, or archive services
```
