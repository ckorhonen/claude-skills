---
name: Cloudflare Manager
description: Comprehensive Cloudflare account management for deploying Workers, KV Storage, R2, Pages, DNS, and Routes. Use when deploying cloudflare services, managing worker containers, configuring KV/R2 storage, or setting up DNS/routing. Requires CLOUDFLARE_API_KEY in .env and Bun runtime with dependencies installed.
---

# Cloudflare Manager

Comprehensive Cloudflare service management skill that enables deployment and configuration of Workers, KV Storage, R2 buckets, Pages, DNS records, and routing. Automatically validates API credentials, extracts deployment URLs, and provides actionable error messages.

## Initial Setup

Before using this skill for the first time:

1. **Install Dependencies**
   ```bash
   cd ~/.claude/skills/cloudflare-manager
   bun install
   ```

2. **Configure API Key**

   Create a `.env` file in your project root:
   ```bash
   CLOUDFLARE_API_KEY=your_api_token_here
   CLOUDFLARE_ACCOUNT_ID=your_account_id  # Optional, auto-detected
   ```

   **Getting your API token**:
   - Visit https://dash.cloudflare.com/profile/api-tokens
   - Click "Create Token"
   - Use "Edit Cloudflare Workers" template (or create custom token)
   - Required permissions:
     - Account > Workers Scripts > Edit
     - Account > Workers KV Storage > Edit
     - Account > Workers R2 Storage > Edit
     - Account > Cloudflare Pages > Edit
     - Zone > DNS > Edit (if using custom domains)

3. **Validate Credentials**

   Run validation to verify your API key and check permissions:
   ```bash
   cd ~/.claude/skills/cloudflare-manager
   bun scripts/validate-api-key.ts
   ```

   **Expected output**:
   ```
   ✅ API key is valid!
   ℹ️  Token Status: active
   ℹ️  Account: Your Account Name (abc123...)

   🔑 Granted Permissions:
     ✅ Workers Scripts: Edit
     ✅ Workers KV Storage: Edit
     ✅ Workers R2 Storage: Edit
   ```

   **Troubleshooting validation**:
   - If validation fails with 401/403: Check your API token is correct in `.env`
   - If validation fails with network error: Check internet connection
   - Use `--no-cache` flag to force fresh validation: `bun scripts/validate-api-key.ts --no-cache`

## Current API Permissions

<!-- PERMISSIONS_START -->
Run `bun scripts/validate-api-key.ts` to populate this section with your current permissions.
<!-- PERMISSIONS_END -->

## Examples

### Example 1: Deploy New Worker API

**User request:**
```
"Set up a Cloudflare worker for handling API requests and give me the URL"
```

**Workflow:**
1. Validate API credentials exist in .env
2. Deploy worker script:
   ```bash
   bun scripts/workers.ts deploy api-handler ./worker.js
   ```
3. Extract Cloudflare-generated URL from response
4. Return URL: `https://api-handler.username.workers.dev`

**Expected output:**
```
✅ Worker deployed successfully!
📍 URL: https://api-handler.username.workers.dev
🆔 Worker ID: abc123def456
```

**Time:** 2-5 seconds

---

### Example 2: Full Application Stack (Worker + KV + R2)

**User request:**
```
"Set up a complete Cloudflare application with worker, key-value storage, and file storage"
```

**Workflow:**
1. Create KV namespace for session caching:
   ```bash
   bun scripts/kv-storage.ts create-namespace app-sessions
   # Returns: namespace-id-123
   ```

2. Create R2 bucket for user uploads:
   ```bash
   bun scripts/r2-storage.ts create-bucket app-uploads
   # Returns: Bucket created: app-uploads
   ```

3. Deploy worker with bindings:
   ```bash
   bun scripts/workers.ts deploy app-api ./worker.js \
     --kv-binding SESSION_STORE=namespace-id-123 \
     --r2-binding UPLOADS=app-uploads
   ```

4. Configure custom domain route:
   ```bash
   bun scripts/dns-routes.ts create-route example.com \
     "api.example.com/*" app-api
   ```

**Expected output:**
```
✅ KV namespace created: app-sessions (namespace-id-123)
✅ R2 bucket created: app-uploads
✅ Worker deployed: https://app-api.username.workers.dev
✅ Route configured: api.example.com/* → app-api
```

**Time:** 8-12 seconds total

---

### Example 3: Deploy Static Site to Pages

**User request:**
```
"Deploy my static site to Cloudflare Pages"
```

**Workflow:**
1. Create Pages project (if doesn't exist):
   ```bash
   bun scripts/pages.ts deploy my-site ./dist
   ```

2. For first deployment with files, use Wrangler:
   ```bash
   npx wrangler pages deploy ./dist --project-name=my-site
   ```

3. Set environment variables:
   ```bash
   bun scripts/pages.ts set-env my-site API_URL https://api.example.com
   bun scripts/pages.ts set-env my-site DEBUG false --env production
   ```

**Expected output:**
```
✅ Pages project created: my-site
📍 URL: https://my-site.pages.dev
🚀 Deploying files... (via Wrangler)
✅ Deployment complete!
✅ Environment variables set
```

**Time:** 15-30 seconds (depends on site size)

---

## Quick Start Guide

### Deploy a Worker Container

To deploy a new worker container sandbox:

```bash
# Using the skill
bun scripts/workers.ts deploy worker-name ./worker-script.js
```

**What happens**:
- Creates new worker container
- Deploys JavaScript/TypeScript code
- Automatically extracts and returns Cloudflare-generated URL (e.g., `https://worker-name.username.workers.dev`)
- Returns worker ID and configuration

**Example conversation**:
```
User: "Set up and deploy a new cloudflare worker container sandbox named 'api-handler' and return the URL"
Claude: [Deploys worker using bun scripts/workers.ts deploy api-handler ./worker.js]
       Returns URL: https://api-handler.username.workers.dev
```

**Exit codes**:
- `0`: Success - worker deployed and URL returned
- `1`: Failure - check error message for details

**Performance**: Deployment typically completes in 2-5 seconds

## Common Pitfalls

⚠️ **Most Critical Issues** — Address these first if you encounter problems:

### 1. API Token Scoping (Most Common Cause of Failures)

**The Problem**: API tokens with insufficient or incorrectly scoped permissions fail silently with 403 errors, making debugging very difficult.

**How to Avoid**:
- When creating a token at https://dash.cloudflare.com/profile/api-tokens, use the **"Edit Cloudflare Workers"** template — don't use "Read All" or custom scopes without the right permissions
- **Required minimum scopes**:
  - Account > Workers Scripts > Edit
  - Account > Workers KV Storage > Edit
  - Account > Workers R2 Storage > Edit
  - Zone > DNS > Edit (only if using custom domains)
- **Verify your token** immediately after creation:
  ```bash
  bun scripts/validate-api-key.ts
  ```
  This shows exactly which permissions you have. **Do this every time you create or update a token.**

**Quick Diagnosis**:
```bash
# If you see "Insufficient permissions", stop and fix the token:
bun scripts/validate-api-key.ts
# If any required permission shows ❌, update token at:
# https://dash.cloudflare.com/profile/api-tokens
```

---

### 2. Wrangler OAuth Port Conflicts

**The Problem**: `wrangler login` uses port 8976 for the OAuth callback. If another `wrangler dev` or `wrangler pages dev` process is already running, the login flow will fail silently — the browser tab opens but never receives the OAuth redirect.

**How to Avoid**:
- Before running `wrangler login`, **kill all other Wrangler processes**:
  ```bash
  pkill -f wrangler
  ```
- Then run login:
  ```bash
  wrangler login
  ```
- Only start `wrangler dev` or Pages after login completes

**Why This Happens**: Wrangler doesn't queue OAuth callbacks — the first process to bind port 8976 gets the callback. If that's a dev server, login attempts silently fail.

---

### 3. Deployment Timeouts (Large Projects)

**The Problem**: Workers and Pages deployments timeout if the project is too large or network connectivity is unstable. Timeouts also occur during peak Cloudflare load.

**How to Avoid**:
- **Worker scripts**: Keep under 1MB (smaller = faster cold start)
- **Pages deployments**: 
  - Projects with >1000 files may take 5-10 minutes
  - Use `.cloudflare/` ignore patterns to exclude node_modules, build caches, etc.
  - For large deployments, use Wrangler CLI directly:
    ```bash
    npx wrangler pages deploy ./dist --project-name=my-app
    ```
- **Network**: Deploy from a stable connection. Retries use exponential backoff and should succeed automatically
- **If stuck in pending state**:
  ```bash
  bun scripts/pages.ts list-deployments my-app  # Check status
  # If truly stuck, delete and recreate the project
  ```

---

## Reference: Troubleshooting Guide

For detailed solutions to specific error messages, see the [Troubleshooting](#troubleshooting) section below.

### Create and Use KV Storage

To create a KV namespace and store data:

```bash
# Create namespace
bun scripts/kv-storage.ts create-namespace user-sessions
# Returns: Namespace ID (e.g., abc123def456)
# Save this ID for binding to workers

# Write key-value pair
bun scripts/kv-storage.ts write <namespace-id> "session:user123" '{"userId":"123","token":"abc"}'

# Read value
bun scripts/kv-storage.ts read <namespace-id> "session:user123"
# Returns: {"userId":"123","token":"abc"}

# List all keys (useful for debugging)
bun scripts/kv-storage.ts list-keys <namespace-id>

# Delete a key
bun scripts/kv-storage.ts delete <namespace-id> "session:user123"
```

**Important**: KV storage uses eventual consistency. Writes may take up to 60 seconds to propagate globally. For immediate reads, use the same edge location where you wrote the data.

### Create R2 Bucket and Upload Files

To create an R2 bucket and manage objects:

```bash
# Create bucket
bun scripts/r2-storage.ts create-bucket media-assets

# Upload file
bun scripts/r2-storage.ts upload media-assets ./images/logo.png logo.png

# List objects
bun scripts/r2-storage.ts list-objects media-assets

# Download object
bun scripts/r2-storage.ts download media-assets logo.png ./downloaded-logo.png
```

### Deploy to Cloudflare Pages

To deploy a static site or application to Pages:

```bash
# Create Pages project (or get existing project info)
bun scripts/pages.ts deploy my-app ./dist
# Returns: https://my-app.pages.dev

# Set environment variable
bun scripts/pages.ts set-env my-app API_URL https://api.example.com

# Set environment variable for specific environment
bun scripts/pages.ts set-env my-app DEBUG true --env preview

# Get deployment URL
bun scripts/pages.ts get-url my-app
```

**Auto-extracted URLs**: The Pages script automatically extracts and returns the Cloudflare-generated URL (e.g., `https://my-app.pages.dev`) from the deployment response.

**Note**: The API creates the project structure, but for actual file uploads, you'll need Wrangler CLI:
```bash
npx wrangler pages deploy ./dist --project-name=my-app
```

**Why this works**: The skill creates/verifies the Pages project and returns the URL. For the initial deployment with files, Wrangler handles the complex multipart upload process.

### Configure DNS and Routes

To create DNS records and configure worker routes:

```bash
# Create DNS A record
bun scripts/dns-routes.ts create-dns example.com A api 192.168.1.1

# Route pattern to worker
bun scripts/dns-routes.ts create-route example.com "*.example.com/api/*" api-handler
```

## Common Workflows

### Multi-Service Setup

To set up a complete application with worker, KV storage, and R2 bucket:

1. **Create KV namespace for caching**
   ```bash
   bun scripts/kv-storage.ts create-namespace app-cache
   ```

2. **Create R2 bucket for media**
   ```bash
   bun scripts/r2-storage.ts create-bucket app-media
   ```

3. **Deploy worker with bindings**
   ```bash
   bun scripts/workers.ts deploy app-worker ./worker.js --kv-binding app-cache --r2-binding app-media
   ```

4. **Configure route**
   ```bash
   bun scripts/dns-routes.ts create-route example.com "example.com/*" app-worker
   ```

### Update Worker Configuration

To update an existing worker's code or bindings:

```bash
# Update worker code
bun scripts/workers.ts update worker-name ./new-worker-script.js

# Get worker details
bun scripts/workers.ts get worker-name

# List all workers
bun scripts/workers.ts list
```

### Bulk KV Operations

To perform bulk operations on KV storage:

```bash
# Bulk write from JSON file
bun scripts/kv-storage.ts bulk-write namespace-name ./data.json

# Delete multiple keys
bun scripts/kv-storage.ts bulk-delete namespace-name key1 key2 key3
```

## Error Handling

### Missing API Key

If `.env` file is missing or `CLOUDFLARE_API_KEY` is not set:
```
Error: CLOUDFLARE_API_KEY not found in environment

Solution: Create .env file in project root:
  echo "CLOUDFLARE_API_KEY=your_token_here" > .env
```

### Invalid Permissions

If API token lacks required permissions:
```
Error: Insufficient permissions for Workers deployment

Required: Workers Scripts: Edit
Current: Workers Scripts: Read

Solution: Update token permissions at:
  https://dash.cloudflare.com/profile/api-tokens
```

### API Rate Limiting

If too many requests are made:
```
Error: Rate limit exceeded (429)

Solution: Retry automatically with exponential backoff (3 attempts)
```

### Network Issues

If API is unreachable:
```
Error: Failed to connect to Cloudflare API

Solution: Check internet connection and retry
```

## Best Practices

**Security**:
- Never commit `.env` files - always add to `.gitignore`
- Use token-based authentication (not API keys)
- Rotate tokens periodically (every 90 days recommended)
- Use least-privilege principle: only grant required permissions
- Store secrets via Wrangler CLI: `wrangler secret put SECRET_NAME`

**Performance**:
- Deploy workers to minimize latency (they run at Cloudflare edge)
- Use KV storage for frequently-read data (not frequently-written)
- Use R2 for large files (KV has 25MB limit per key)
- Enable caching with appropriate TTLs
- Keep worker scripts under 1MB for faster cold starts

**Development Workflow**:
- Test locally first: `wrangler dev` for local testing
- Use staging environment before production
- Validate credentials after token updates: `bun scripts/validate-api-key.ts`
- Monitor worker logs: `wrangler tail worker-name`
- Version your workers: use names like `api-v1`, `api-v2`

**Naming Conventions**:
- Workers: Use descriptive names (e.g., `user-auth-worker` not `worker1`)
- KV namespaces: Include purpose (e.g., `app-sessions`, `api-cache`)
- R2 buckets: Use lowercase with hyphens (e.g., `media-assets-prod`)
- Be consistent across your infrastructure

**Resource Management**:
- Delete unused workers, namespaces, and buckets
- Monitor usage in Cloudflare dashboard
- Free tier limits: 100,000 requests/day for Workers
- Set up billing alerts to avoid surprises

## Advanced Usage

For advanced scenarios including:
- Complex routing configurations
- Multi-region deployments
- Custom domain setup
- Worker-to-worker communication
- Durable Objects integration
- Bulk operations and migrations

See [examples.md](examples.md) for comprehensive examples and patterns.

## Script Reference

All scripts are located in `~/.claude/skills/cloudflare-manager/scripts/`:

- **validate-api-key.ts**: Validate API credentials and display permissions
- **workers.ts**: Deploy, update, and manage Workers
- **kv-storage.ts**: Create and manage KV namespaces and key-value pairs
- **r2-storage.ts**: Create and manage R2 buckets and objects
- **pages.ts**: Deploy and configure Cloudflare Pages projects
- **dns-routes.ts**: Configure DNS records and worker routes
- **utils.ts**: Shared utilities for API calls and error handling

## Templates

Starter templates are available in `~/.claude/skills/cloudflare-manager/templates/`:

- **worker-template.js**: Basic worker template with fetch handler
- **wrangler.toml.template**: Wrangler configuration template

## Troubleshooting

### Quick Link: High-Priority Issues

For the most critical problems encountered in production, see [Common Pitfalls](#common-pitfalls) above:
- **API token scoping issues** → [API Token Scoping](#1-api-token-scoping-most-common-cause-of-failures)
- **Wrangler OAuth failures** → [Wrangler OAuth Port Conflicts](#2-wrangler-oauth-port-conflicts)
- **Deployment timeouts** → [Deployment Timeouts](#3-deployment-timeouts-large-projects)

### Diagnostic Commands

**First steps when something fails:**
```bash
# 1. Validate API credentials and permissions
bun scripts/validate-api-key.ts

# 2. List existing resources to check state
bun scripts/workers.ts list
bun scripts/kv-storage.ts list-namespaces
bun scripts/r2-storage.ts list-buckets
bun scripts/pages.ts list-projects

# 3. Check specific resource details
bun scripts/workers.ts get worker-name
bun scripts/pages.ts list-deployments project-name
```

**When to use each:**
- Step 1 (validate): Always run this first if ANY command fails
- Step 2 (list): Check what resources actually exist
- Step 3 (get details): Investigate specific resource state

### Common Issues and Solutions

**Issue**: "Worker deployment failed with unknown error"

**Symptoms**: Deployment command exits with error code 1, no specific error message

**Solutions**:
1. Check script syntax: `node --check ./worker.js`
2. Verify file exists: `ls -lh ./worker.js`
3. Re-validate API key: `bun scripts/validate-api-key.ts --no-cache`
4. Check worker name is valid (alphanumeric, hyphens, underscores only)

---

**Issue**: "KV namespace not found"

**Symptoms**: Error when trying to read/write to namespace

**Solutions**:
1. List all namespaces: `bun scripts/kv-storage.ts list-namespaces`
2. Verify you're using namespace ID (not name) in commands
3. Check namespace wasn't deleted
4. Ensure API token has KV Storage permissions

---

**Issue**: "R2 bucket already exists" or "Bucket name taken"

**Symptoms**: Cannot create bucket with chosen name

**Solutions**:
1. Bucket names must be globally unique across all Cloudflare accounts
2. Try a more specific name: `my-app-media-2024` instead of `media`
3. Use existing bucket: `bun scripts/r2-storage.ts list-buckets`
4. Names must be 3-63 characters, lowercase letters/numbers/hyphens only

---

**Issue**: "Pages deployment timeout" or "Deployment pending"

**Symptoms**: Deployment doesn't complete, stays in pending state

**Solutions**:
1. Check deployment status: `bun scripts/pages.ts list-deployments project-name`
2. View in dashboard: https://dash.cloudflare.com/pages
3. Large deployments (>1000 files) may take 5-10 minutes
4. Cancel and retry if stuck: Delete project and recreate

---

**Issue**: "DNS record creation failed"

**Symptoms**: Cannot create DNS records or routes

**Solutions**:
1. Verify zone exists: `bun scripts/dns-routes.ts list-zones`
2. Ensure domain is added to Cloudflare and active
3. Check nameservers point to Cloudflare: `dig NS yourdomain.com`
4. Verify API token has Zone > DNS > Edit permission

---

**Issue**: "API rate limit exceeded (429)"

**Symptoms**: Commands fail with "Too many requests"

**Solutions**:
1. Scripts automatically retry with exponential backoff
2. Wait 1-2 minutes before retrying manually
3. Reduce concurrent operations
4. Rate limits: 1200 requests per 5 minutes

---

**Issue**: "CLOUDFLARE_API_KEY not found in environment"

**Symptoms**: Commands fail immediately with environment error

**Solutions**:
1. Create `.env` file in project root (not skill directory)
2. Verify file content: `cat .env | grep CLOUDFLARE_API_KEY`
3. Ensure no extra spaces: `CLOUDFLARE_API_KEY=token` (no spaces around `=`)
4. Run commands from project root where `.env` exists

**Quick Fix**:
```bash
cd /path/to/your/project
echo "CLOUDFLARE_API_KEY=your_token_here" > .env
bun scripts/validate-api-key.ts
```

## Security Notes

- API keys are never logged or displayed in output
- All API requests use HTTPS
- User inputs are validated before API calls
- Destructive operations (delete) require confirmation
- Permissions are cached for 24 hours to minimize token exposure

## Additional Resources

- Cloudflare API Documentation: https://developers.cloudflare.com/api/
- Workers Documentation: https://developers.cloudflare.com/workers/
- KV Storage Guide: https://developers.cloudflare.com/kv/
- R2 Storage Guide: https://developers.cloudflare.com/r2/
- Pages Documentation: https://developers.cloudflare.com/pages/
