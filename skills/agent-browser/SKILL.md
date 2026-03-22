---
name: agent-browser
description: Automate headless browser interactions using agent-browser CLI. Use when scraping web pages, automating form submissions, testing web apps, or performing browser automation tasks. Works with element refs (@e1, @e2) optimized for AI agent reasoning.
---

# agent-browser CLI

A headless browser automation CLI designed for AI agents, with fast Rust-based execution and element refs optimized for LLM reasoning.

## Overview

agent-browser provides programmatic browser control through a CLI that's purpose-built for AI agent workflows. It uses deterministic element references (`@e1`, `@e2`, etc.) from accessibility trees, making it ideal for LLM-based automation where consistent element targeting is critical.

**Key Features:**
- Fast Rust-based CLI with Node.js fallback
- Element refs (`@e1`, `@e2`) for stable LLM reasoning
- Session isolation for parallel browser instances
- JSON output for programmatic parsing
- Accessibility tree snapshots for element discovery
- CDP connection support for existing browser instances

## When to Use

- Automating web interactions (form filling, clicking, navigation)
- Scraping web content with accessibility tree parsing
- Testing web applications programmatically
- Multi-agent scenarios requiring isolated browser sessions
- Screenshot capture and PDF generation
- Monitoring web page state changes

## Prerequisites

- Node.js >= 18 or Bun runtime
- Chromium (installed via `agent-browser install`)

## Installation

```bash
# Install globally
bun install -g agent-browser

# Download Chromium
agent-browser install

# Linux with system dependencies
agent-browser install --with-deps
```

Verify installation:
```bash
agent-browser --version
```

## Quick Start

```bash
# Navigate to a page
agent-browser open https://example.com

# Get accessibility snapshot with element refs
agent-browser snapshot -i  # -i = interactive elements only

# Click an element by ref
agent-browser click @e2

# Fill a form field
agent-browser fill @e3 "test@example.com"

# Take a screenshot
agent-browser screenshot output.png
```

## Core Workflow

### 1. Open Page and Snapshot

```bash
# Open URL
agent-browser open https://example.com

# Get interactive elements with refs
agent-browser snapshot -i --json
```

The snapshot returns elements like:
```
@e1 link "Home"
@e2 textbox "Email"
@e3 button "Submit"
```

### 2. Interact Using Refs

```bash
# Click by ref
agent-browser click @e2

# Type into focused element
agent-browser type @e2 "hello@example.com"

# Fill (clears first, then types)
agent-browser fill @e2 "hello@example.com"

# Press keyboard key
agent-browser press Enter
```

### 3. Verify State

```bash
# Check element visibility
agent-browser is visible @e3

# Get element text
agent-browser get text @e1

# Get page URL
agent-browser get url
```

## Command Reference

### Navigation

| Command | Description |
|---------|-------------|
| `open <url>` | Navigate to URL |
| `back` | Go back in history |
| `forward` | Go forward in history |
| `reload` | Reload current page |
| `close` | Close browser |

### Interactions

| Command | Description |
|---------|-------------|
| `click <ref>` | Click element |
| `dblclick <ref>` | Double-click element |
| `type <ref> <text>` | Type text into element |
| `fill <ref> <text>` | Clear and fill element |
| `press <key>` | Press keyboard key (Enter, Tab, Control+a) |
| `hover <ref>` | Hover over element |
| `focus <ref>` | Focus element |
| `check <ref>` | Check checkbox |
| `uncheck <ref>` | Uncheck checkbox |
| `select <ref> <val>` | Select dropdown option |
| `scroll <dir> [px]` | Scroll (up/down/left/right) |
| `wait <ref\|ms>` | Wait for element or milliseconds |

### Information

| Command | Description |
|---------|-------------|
| `snapshot` | Get accessibility tree with refs |
| `snapshot -i` | Interactive elements only |
| `snapshot -c` | Compact (remove empty elements) |
| `snapshot -d <n>` | Limit tree depth |
| `get text <ref>` | Get element text content |
| `get html <ref>` | Get element HTML |
| `get value <ref>` | Get input value |
| `get url` | Get current page URL |
| `get title` | Get page title |
| `screenshot [path]` | Take screenshot |
| `screenshot --full` | Full page screenshot |
| `pdf <path>` | Save page as PDF |

### State Checks

| Command | Description |
|---------|-------------|
| `is visible <ref>` | Check if element is visible |
| `is enabled <ref>` | Check if element is enabled |
| `is checked <ref>` | Check if checkbox is checked |

### Find Elements

```bash
# Find by role and click
agent-browser find role button click --name Submit

# Find by text
agent-browser find text "Sign In" click

# Find by label
agent-browser find label "Email" fill "test@example.com"

# Find by placeholder
agent-browser find placeholder "Search..." type "query"
```

## Session Management

Sessions provide isolated browser instances for parallel execution:

```bash
# Use named session
agent-browser --session login-flow open https://app.com

# Different session for another task
agent-browser --session checkout open https://app.com/cart

# List active sessions
agent-browser session list

# Environment variable (persistent across commands)
export AGENT_BROWSER_SESSION=my-session
agent-browser open https://example.com
```

## JSON Output

Use `--json` for machine-readable output:

```bash
# Snapshot as JSON
agent-browser snapshot -i --json

# Get element info as JSON
agent-browser get text @e1 --json

# Parse in scripts
agent-browser get url --json | jq -r '.url'
```

## Common Pitfalls

This section covers frequent failure modes and how to debug them. Each pitfall includes the symptom you'll see, the underlying cause, and the fix.

### Browser not found
**Symptom:** `Error: Browser executable not found at default path` or `agent-browser: command not found`

**Cause:** Chromium isn't installed, or agent-browser CLI isn't on PATH

**Fix:**
```bash
# Install Chromium
agent-browser install

# For Linux, install system dependencies
agent-browser install --with-deps

# Verify installation
agent-browser --version
```

### Element ref becomes stale after page change
**Symptom:** `Error: Element @e2 not found` even though you just used it, or clicks fail silently

**Cause:** Element refs change when the DOM updates (navigation, page reload, dynamic content). Refs are only valid for the current DOM snapshot.

**Fix:**
```bash
# Always re-snapshot after major page changes
agent-browser click @e1  # Click submit
agent-browser wait 2000  # Wait for navigation
agent-browser snapshot -i --json  # Get fresh refs
agent-browser click @e1  # Use new ref (was @e1 before? Verify!)
```

**Prevention:** In scripts, capture fresh refs after each navigation or dynamic load.

### Session conflicts and port binding
**Symptom:** `Error: Session "default" already in use` or `Port 9222 already in use`

**Cause:** Browser session is still running from a previous command or crashed script, preventing a new session from starting

**Fix:**
```bash
# List active sessions
agent-browser session list

# Kill a specific session
agent-browser session kill my-session

# Use unique session names to avoid conflicts
agent-browser --session upload-$(date +%s) open https://app.com

# Or set environment variable once
export AGENT_BROWSER_SESSION=task-$(date +%s)
agent-browser open https://example.com
agent-browser close
```

### Clicks and interactions don't work on hidden elements
**Symptom:** `agent-browser click @e5` succeeds but nothing happens, or element is invisible in screenshot

**Cause:** Element is outside viewport, hidden by CSS (`display: none`, `visibility: hidden`), or covered by another element. Accessibility tree may show it, but browser can't interact with it.

**Fix:**
```bash
# Check visibility before interaction
agent-browser is visible @e5

# Scroll to make element visible
agent-browser scroll down 500

# Take screenshot to visually verify
agent-browser screenshot current-state.png

# Try parent element if child is deeply nested
agent-browser click @e4  # Click parent button instead
```

**Prevention:** Always take screenshots before and after critical interactions to verify visual state.

### Timeout waiting for navigation or element
**Symptom:** `Error: Timeout waiting for element` or script hangs indefinitely after clicking a link

**Cause:** 
- Element doesn't exist or appears after longer than expected delay
- Navigation is stuck (network error, page not loading)
- Element selector is wrong

**Fix:**
```bash
# Explicit wait before checking for element
agent-browser wait 2000  # Wait 2 seconds
agent-browser snapshot -i --json  # Check if element exists

# Wait for specific element to appear
agent-browser wait @e3

# Increase timeout with explicit waits in script
agent-browser click @submit
sleep 3  # Shell script sleep
agent-browser snapshot -i

# Check page title to verify navigation worked
agent-browser get title
```

**Prevention:** Add explicit `wait` commands after form submissions or link clicks that cause navigation.

### Snapshot is empty or missing expected elements
**Symptom:** `agent-browser snapshot -i --json` returns `[]` or very few elements, but you see them visually in screenshot

**Cause:** 
- Page content is rendered by JavaScript (React, Vue, etc.) that hasn't completed
- Elements lack accessible labels or roles
- `-i` flag filters too aggressively

**Fix:**
```bash
# Wait for content to render
agent-browser wait 2000
agent-browser snapshot -i

# Remove interactive-only filter to see all elements
agent-browser snapshot -c  # Compact but includes all elements

# Increase tree depth to find nested elements
agent-browser snapshot -d 5

# Use full snapshot to diagnose
agent-browser snapshot --json | jq . | less

# Check page title to verify page loaded
agent-browser get title
```

**Prevention:** Add wait delays after opening pages with heavy JavaScript rendering.

### Form fill doesn't work or text is partial
**Symptom:** Text appears to be cut off, only first few characters typed, or field stays empty

**Cause:** 
- Field wasn't focused before typing (race condition)
- Field has input validation or character limit
- JavaScript event handlers expect specific typing speed or blur event

**Fix:**
```bash
# Always focus explicitly before filling
agent-browser focus @e2
agent-browser wait 500  # Let field settle
agent-browser fill @e2 "complete@example.com"

# For fields with slow JS event handling
agent-browser type @e2 "first part"
agent-browser wait 500
agent-browser type @e2 "second part"

# Verify what was actually entered
agent-browser get value @e2
```

**Prevention:** After any form fill, immediately verify the value was entered correctly with `get value`.

### Network requests fail or external API timeouts
**Symptom:** Page loads but data doesn't populate, or integration tests fail when hitting real APIs

**Cause:** 
- External API is slow or unreachable
- CORS errors (browser blocks requests to different domain)
- Missing authentication headers
- Network is isolated (testing environment)

**Fix:**
```bash
# Set custom headers for auth
agent-browser --headers '{"Authorization": "Bearer token123"}' open https://api.example.com

# Mock API responses instead
agent-browser network route "**/api/data" --body '{"result":"mocked"}'

# Add explicit wait for API response
agent-browser wait 3000  # Give API time to respond
agent-browser snapshot -i

# Fallback: Use `--headed` to see error messages
agent-browser --headed open https://app.com
agent-browser click @e1  # See browser console errors
```

**Prevention:** For testing, use `network route` to mock external APIs. For production, verify connectivity before running automation.

### Browser crashes or becomes unresponsive
**Symptom:** `agent-browser` command hangs or process crashes with segmentation fault; Chrome window closes unexpectedly

**Cause:**
- Out of memory (too many long-running sessions or screenshots)
- Invalid CDP connection
- Rare Chromium/Playwright crash
- Insufficient system resources

**Fix:**
```bash
# Restart with fresh session
agent-browser session kill all-sessions  # Or specify a name

# Use lightweight mode with limited resources
agent-browser --session lite open https://minimal-site.com

# Reduce screenshot frequency
# Instead of: agent-browser screenshot after every click
# Do: agent-browser screenshot only on failure

# Check system resources
top -n 1 | head -20

# Run with --debug for crash diagnostics
agent-browser --debug open https://example.com 2>&1 | tail -50
```

**Prevention:** 
- Close sessions explicitly: `agent-browser close`
- Use unique session names for long-lived tasks
- Monitor memory in long automation scripts

### Element ref is ambiguous (@e1 appears for multiple elements)
**Symptom:** Multiple elements resolve to the same @e number, clicking @e1 affects the wrong element

**Cause:** Accessibility tree groups similar elements (buttons, links) and agent-browser assigns refs based on order, not uniqueness

**Fix:**
```bash
# Use full snapshot to understand structure
agent-browser snapshot -d 3 --json > structure.json
cat structure.json | jq .  # Examine hierarchy

# Click using find by text if available
agent-browser find text "Specific Button Text" click

# Use CSS selector if accessibility tree isn't clear
agent-browser find selector "button.submit-btn" click

# Take screenshot and count visually
agent-browser screenshot debug.png
# Then manually map which @eN corresponds to which button

# Use context to disambiguate
agent-browser get text @e1  # Check what @e1 actually is
```

**Prevention:** Always verify element identity by checking its text or taking screenshots before critical interactions.

## Advanced Features

### CDP Connection

Connect to an existing Chrome instance:

```bash
# Start Chrome with debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Connect agent-browser
agent-browser --cdp 9222 snapshot
```

### Video Recording

```bash
# Start recording
agent-browser record start recording.webm https://example.com

# Perform actions...
agent-browser click @e1
agent-browser fill @e2 "test"

# Stop and save
agent-browser record stop
```

### Network Interception

```bash
# Block requests to URL pattern
agent-browser network route "**/analytics/*" --abort

# Mock API response
agent-browser network route "**/api/user" --body '{"name": "Test"}'

# View captured requests
agent-browser network requests
```

### Custom Headers

```bash
# Set auth headers
agent-browser --headers '{"Authorization": "Bearer token123"}' open https://api.example.com
```

### Browser Extensions

```bash
# Load extension
agent-browser --extension /path/to/extension open https://example.com
```

## AI Agent Patterns

### Form Automation

```bash
#!/bin/bash
# Login automation script

agent-browser open https://app.com/login

# Get form elements
agent-browser snapshot -i --json > elements.json

# Fill credentials
agent-browser fill @e2 "user@example.com"
agent-browser fill @e3 "password123"

# Submit
agent-browser click @e4

# Wait for navigation
agent-browser wait 2000

# Verify login
agent-browser get url --json | jq -r '.url'
```

### Data Extraction

```bash
#!/bin/bash
# Scrape product data

agent-browser open https://shop.com/products

# Get page content
agent-browser snapshot --json > snapshot.json

# Extract specific element text
agent-browser get text '[data-testid="price"]' --json

# Screenshot for verification
agent-browser screenshot products.png
```

### Multi-Page Workflow

```bash
#!/bin/bash
SESSION="checkout-flow"

# Step 1: Add to cart
agent-browser --session $SESSION open https://shop.com/product/123
agent-browser --session $SESSION click @add-to-cart-button
agent-browser --session $SESSION wait 1000

# Step 2: Go to checkout
agent-browser --session $SESSION open https://shop.com/checkout
agent-browser --session $SESSION snapshot -i

# Step 3: Fill shipping
agent-browser --session $SESSION fill @shipping-name "John Doe"
agent-browser --session $SESSION fill @shipping-address "123 Main St"

# Cleanup
agent-browser --session $SESSION close
```

## Options Reference

| Option | Description |
|--------|-------------|
| `--session <name>` | Isolated browser session |
| `--json` | JSON output format |
| `--headed` | Show browser window (not headless) |
| `--cdp <port>` | Connect via Chrome DevTools Protocol |
| `--headers <json>` | HTTP headers for requests |
| `--proxy <url>` | Proxy server |
| `--executable-path <path>` | Custom browser executable |
| `--extension <path>` | Load browser extension |
| `--full, -f` | Full page screenshot |
| `--debug` | Debug output |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AGENT_BROWSER_SESSION` | Default session name |
| `AGENT_BROWSER_EXECUTABLE_PATH` | Custom browser path |
| `AGENT_BROWSER_STREAM_PORT` | WebSocket streaming port |

## Examples

### Example 1: Simple Web Scraping

**User request:**
```
"Scrape the product title and price from https://example.com/product/123"
```

**Workflow:**
```bash
# 1. Navigate to page
agent-browser open https://example.com/product/123

# 2. Get accessibility snapshot
agent-browser snapshot -i --json > page.json

# 3. Identify elements (example output):
# @e5 heading "Premium Widget Pro"
# @e12 text "$49.99"

# 4. Extract data
agent-browser get text @e5 --json  # Returns: {"text": "Premium Widget Pro"}
agent-browser get text @e12 --json  # Returns: {"text": "$49.99"}
```

**Expected output:**
```json
{
  "title": "Premium Widget Pro",
  "price": "$49.99"
}
```

**Time:** 2-3 seconds

---

### Example 2: Form Submission with Verification

**User request:**
```
"Fill out the contact form at https://example.com/contact and verify submission"
```

**Workflow:**
```bash
# 1. Navigate and snapshot
agent-browser open https://example.com/contact
agent-browser snapshot -i

# Example snapshot output:
# @e1 textbox "Name"
# @e2 textbox "Email"
# @e3 textbox "Message"
# @e4 button "Send"

# 2. Fill form fields
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "john@example.com"
agent-browser fill @e3 "I have a question about your product"

# 3. Submit
agent-browser click @e4

# 4. Wait for response
agent-browser wait 2000

# 5. Verify success
agent-browser snapshot -i | grep "Thank you"
# Or take screenshot for manual verification
agent-browser screenshot success.png
```

**Expected outcome:**
- Form submitted successfully
- Page shows confirmation message
- Screenshot saved showing success state

**Time:** 4-6 seconds

---

### Example 3: Multi-Page Workflow with Session

**User request:**
```
"Add item to cart, proceed to checkout, and fill shipping info"
```

**Workflow:**
```bash
# Use session for state persistence across commands
SESSION="checkout-flow-$(date +%s)"

# 1. Add to cart
agent-browser --session $SESSION open https://shop.example.com/product/widget
agent-browser --session $SESSION snapshot -i | grep "Add to Cart"
agent-browser --session $SESSION click @add-to-cart  # Assuming @add-to-cart ref found
agent-browser --session $SESSION wait 1000  # Wait for cart update

# 2. Go to checkout
agent-browser --session $SESSION open https://shop.example.com/checkout
agent-browser --session $SESSION snapshot -i

# 3. Fill shipping form (refs from snapshot)
agent-browser --session $SESSION fill @shipping-name "Jane Smith"
agent-browser --session $SESSION fill @shipping-address "456 Oak Ave"
agent-browser --session $SESSION fill @shipping-city "Portland"
agent-browser --session $SESSION select @shipping-state "OR"
agent-browser --session $SESSION fill @shipping-zip "97201"

# 4. Take screenshot before submission
agent-browser --session $SESSION screenshot checkout-filled.png

# 5. Cleanup
agent-browser --session $SESSION close
```

**Expected outcome:**
- Item added to cart successfully
- Checkout form filled with shipping details
- Screenshot saved showing completed form
- Session cleaned up

**Time:** 8-12 seconds

---

### Example 4: Login and Data Extraction

**User request:**
```
"Log into dashboard, navigate to reports, and extract table data"
```

**Workflow:**
```bash
SESSION="dashboard-scrape"

# 1. Login
agent-browser --session $SESSION open https://app.example.com/login
agent-browser --session $SESSION snapshot -i

# Fill login form
agent-browser --session $SESSION fill @email "user@example.com"
agent-browser --session $SESSION fill @password "secretpass"
agent-browser --session $SESSION click @submit
agent-browser --session $SESSION wait 2000

# 2. Navigate to reports
agent-browser --session $SESSION open https://app.example.com/reports
agent-browser --session $SESSION wait 1000

# 3. Extract table data
agent-browser --session $SESSION snapshot --json > reports.json

# Parse JSON to extract table rows
# @e20 table
#   @e21 row "Q1 2024, $50,000, 15% growth"
#   @e22 row "Q2 2024, $62,000, 24% growth"

agent-browser --session $SESSION get text @e20 --json

# 4. Cleanup
agent-browser --session $SESSION close
```

**Expected output:**
```json
{
  "reports": [
    {"quarter": "Q1 2024", "revenue": "$50,000", "growth": "15%"},
    {"quarter": "Q2 2024", "revenue": "$62,000", "growth": "24%"}
  ]
}
```

**Time:** 6-10 seconds

---

## Troubleshooting

### Issue: Element Reference Not Found

**Symptoms:**
```
Error: Element @e5 not found
```

**Cause:** Element ref changed after page update or snapshot was stale

**Solution:**
```bash
# 1. Get fresh snapshot
agent-browser snapshot -i

# 2. Verify element ref in output
# Look for expected element in snapshot output

# 3. If element doesn't appear, try without -i flag
agent-browser snapshot  # Shows all elements, not just interactive

# 4. If still missing, check if page loaded completely
agent-browser wait 2000  # Wait for page to settle
agent-browser snapshot -i
```

---

### Issue: Timeout Waiting for Navigation

**Symptoms:**
```
Error: Navigation timeout after 30000ms
```

**Cause:** Page takes too long to load or network issues

**Solution:**
```bash
# 1. Check if page is accessible
agent-browser --headed open https://example.com  # Visual debugging

# 2. Increase wait time after navigation
agent-browser open https://slow-site.com
agent-browser wait 5000  # Wait 5 seconds

# 3. Check network requests
agent-browser network requests  # See what's loading

# 4. Use CDP connection for better control
agent-browser --cdp 9222 open https://example.com
```

---

### Issue: Click Not Working

**Symptoms:** Element click command runs but nothing happens

**Cause:** Element not visible, disabled, or covered by another element

**Solution:**
```bash
# 1. Check if element is visible
agent-browser is visible @e3
# Returns: true/false

# 2. Check if element is enabled
agent-browser is enabled @e3

# 3. Try scrolling to element first
agent-browser scroll down 500
agent-browser wait 500
agent-browser click @e3

# 4. Take screenshot to see page state
agent-browser screenshot debug.png

# 5. Try double-click instead
agent-browser dblclick @e3
```

---

### Issue: Form Input Not Registering

**Symptoms:** Text typed but form field remains empty

**Cause:** JavaScript framework requires special events or delays

**Solution:**
```bash
# 1. Focus element first
agent-browser focus @e2
agent-browser wait 200

# 2. Use fill instead of type (clears first)
agent-browser fill @e2 "text content"

# 3. Add delays between keystrokes
agent-browser type @e2 "slow"
agent-browser wait 100

# 4. Try pressing Tab after filling to trigger validation
agent-browser fill @e2 "email@example.com"
agent-browser press Tab
```

---

### Issue: Session Persistence Problems

**Symptoms:** Previous session state not available

**Cause:** Session wasn't properly named or browser closed unexpectedly

**Solution:**
```bash
# 1. Always use explicit session names
SESSION="my-workflow-$(date +%s)"  # Unique session ID
agent-browser --session $SESSION open https://example.com

# 2. Check active sessions
agent-browser --session $SESSION get url
# If error, session doesn't exist

# 3. Don't reuse session names across runs
# Each workflow should have unique session ID

# 4. Cleanup sessions when done
agent-browser --session $SESSION close
```

---

### Issue: Chromium Installation Failed

**Symptoms:**
```
Error: Failed to download Chromium
```

**Cause:** Network issues, disk space, or missing system dependencies

**Solution:**
```bash
# 1. Check disk space
df -h  # Ensure >2GB free

# 2. Retry installation with verbose output
agent-browser install --debug

# 3. On Linux, install system dependencies first
agent-browser install --with-deps

# 4. Use custom browser if needed
agent-browser --executable-path /usr/bin/chromium open https://example.com

# 5. Verify installation
agent-browser --version
ls ~/.cache/ms-playwright/  # Check if Chromium exists
```

---

### Issue: JSON Output Malformed

**Symptoms:** Can't parse JSON output from commands

**Cause:** Mixed text/JSON output or errors in JSON mode

**Solution:**
```bash
# 1. Use --json flag consistently
agent-browser get text @e5 --json  # Not: agent-browser get text @e5

# 2. Redirect stderr to separate stream
agent-browser snapshot --json 2>errors.log >output.json

# 3. Validate JSON output
agent-browser snapshot --json | jq .  # Will error if invalid

# 4. Check for error messages in output
agent-browser snapshot --json | grep -E '^{' | jq .
```

---

## Best Practices

- **Always snapshot first**: Get element refs before interacting
- **Use `--json` for parsing**: Machine-readable output for scripts
- **Session isolation**: Use `--session` for parallel workflows
- **Explicit waits**: Add `wait` commands after navigation/clicks
- **Interactive snapshots**: Use `-i` flag to reduce noise
- **Verify state**: Check element visibility before clicking
- **Screenshot on failure**: Capture state when automation fails
