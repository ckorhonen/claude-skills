---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

## Overview

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks.

---

# Process

## 🚀 High-Level Workflow

Creating a high-quality MCP server involves four main phases:

### Phase 1: Deep Research and Planning

#### 1.1 Understand Modern MCP Design

**API Coverage vs. Workflow Tools:**
Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose operations. Performance varies by client—some clients benefit from code execution that combines basic tools, while others work better with higher-level workflows. When uncertain, prioritize comprehensive API coverage.

**Tool Naming and Discoverability:**
Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.

**Context Management:**
Agents benefit from concise tool descriptions and the ability to filter/paginate results. Design tools that return focused, relevant data. Some clients support code execution which can help agents filter and process data efficiently.

**Actionable Error Messages:**
Error messages should guide agents toward solutions with specific suggestions and next steps.

#### 1.2 Study MCP Protocol Documentation

**Navigate the MCP specification:**

Start with the sitemap to find relevant pages: `https://modelcontextprotocol.io/sitemap.xml`

Then fetch specific pages with `.md` suffix for markdown format (e.g., `https://modelcontextprotocol.io/specification/draft.md`).

Key pages to review:
- Specification overview and architecture
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions

#### 1.3 Study Framework Documentation

**Recommended stack:**
- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad usage, static typing and good linting tools)
- **Transport**: Streamable HTTP for remote servers, using stateless JSON (simpler to scale and maintain, as opposed to stateful sessions and streaming responses). stdio for local servers.

**Load framework documentation:**

- **MCP Best Practices**: [📋 View Best Practices](./reference/mcp_best_practices.md) - Core guidelines

**For TypeScript (recommended):**
- **TypeScript SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - TypeScript patterns and examples

**For Python:**
- **Python SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python Guide](./reference/python_mcp_server.md) - Python patterns and examples

#### 1.4 Plan Your Implementation

**Understand the API:**
Review the service's API documentation to identify key endpoints, authentication requirements, and data models. Use web search and WebFetch as needed.

**Tool Selection:**
Prioritize comprehensive API coverage. List endpoints to implement, starting with the most common operations.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

See language-specific guides for project setup:
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - Project structure, package.json, tsconfig.json
- [🐍 Python Guide](./reference/python_mcp_server.md) - Module organization, dependencies

#### 2.2 Implement Core Infrastructure

Create shared utilities:
- API client with authentication
- Error handling helpers
- Response formatting (JSON/Markdown)
- Pagination support

#### 2.3 Implement Tools

For each tool:

**Input Schema:**
- Use Zod (TypeScript) or Pydantic (Python)
- Include constraints and clear descriptions
- Add examples in field descriptions

**Output Schema:**
- Define `outputSchema` where possible for structured data
- Use `structuredContent` in tool responses (TypeScript SDK feature)
- Helps clients understand and process tool outputs

**Tool Description:**
- Concise summary of functionality
- Parameter descriptions
- Return type schema

**Implementation:**
- Async/await for I/O operations
- Proper error handling with actionable messages
- Support pagination where applicable
- Return both text content and structured data when using modern SDKs

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### Phase 3: Review and Test

#### 3.1 Code Quality

Review for:
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool descriptions

#### 3.2 Build and Test

**TypeScript:**
- Run `npm run build` to verify compilation
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector`

**Python:**
- Verify syntax: `python -m py_compile your_server.py`
- Test with MCP Inspector

See language-specific guides for detailed testing approaches and quality checklists.

---

### Phase 4: Create Evaluations

After implementing your MCP server, create comprehensive evaluations to test its effectiveness.

**Load [✅ Evaluation Guide](./reference/evaluation.md) for complete evaluation guidelines.**

#### 4.1 Understand Evaluation Purpose

Use evaluations to test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

#### 4.2 Create 10 Evaluation Questions

To create effective evaluations, follow the process outlined in the evaluation guide:

1. **Tool Inspection**: List available tools and understand their capabilities
2. **Content Exploration**: Use READ-ONLY operations to explore available data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each question yourself to verify answers

#### 4.3 Evaluation Requirements

Ensure each question is:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time

#### 4.4 Output Format

Create an XML file with this structure:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# Common Pitfalls

MCP server development encounters several predictable failure modes. These gotchas represent real problems discovered during implementation.

## 1. Server Doesn't Start After Generation

**Symptoms:**
- `npm start` fails with exit code 1
- Process starts but immediately crashes
- Port already in use error

**Root Causes:**
- Missing dependencies (SDK version mismatch, incomplete npm install)
- Port conflict with existing process
- Incorrect environment variable configuration
- Invalid configuration in `.npmrc` or `tsconfig.json`

**Debugging Commands:**

```bash
# Verify dependencies are installed
npm list @modelcontextprotocol/sdk

# Check if port is in use
lsof -i :3000  # Replace 3000 with your port
netstat -an | grep LISTEN | grep 3000

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Run with verbose output to see initialization errors
npm start -- --debug
NODE_DEBUG=* npm start  # Maximum verbosity for Node.js internals

# For TypeScript, verify compilation first
npm run build
npx tsc --noEmit  # Check for type errors without building

# Check for missing env variables
env | grep MCP  # See what MCP-related vars are set
```

**Prevention:**
- Always run `npm install` after generating project
- Use explicit port numbers in configuration files
- Document required environment variables in `.env.example`
- Test compilation before starting: `npm run build`

---

## 2. Tool Schemas Don't Validate

**Symptoms:**
- MCP Inspector shows "Invalid schema" error
- Client rejects tool with 422 error
- Tool works in one SDK version but not another

**Root Causes:**
- JSON Schema violations in Zod/Pydantic definitions
- Missing required fields in schema objects
- Incorrect `type` annotations
- Circular schema references
- Invalid constraints (pattern regex, min/max without number type)

**Debugging Commands:**

```bash
# Validate schema syntax
npx @modelcontextprotocol/inspector  # GUI debugger, shows schema errors clearly

# Test schema compilation directly (TypeScript)
cat > test-schema.ts << 'EOF'
import { z } from 'zod';
const schema = z.object({
  // your schema here
});
console.log(JSON.stringify(schema.safeParse({}), null, 2));
EOF
npx ts-node test-schema.ts

# For Python, test Pydantic directly
python3 << 'EOF'
from pydantic import BaseModel
class MyTool(BaseModel):
    # your fields here
    pass
print(MyTool.model_json_schema())
EOF

# Print actual schema being sent to client
# In your server code, log before registration:
console.log(JSON.stringify(toolSchema, null, 2));

# Test with invalid inputs to see error messages
# In MCP Inspector, try calling tool with:
# - Missing required fields
# - Wrong types (string instead of number)
# - Values outside constraints
```

**Prevention:**
- Use TypeScript with strict mode enabled (`strict: true` in tsconfig.json)
- Test each schema change: `npm run build`
- Print schema JSON to console during development
- Use MCP Inspector's schema validation (it's the source of truth)
- Keep schemas simple; break complex tools into smaller ones
- Document constraints in field descriptions (min/max values, regex patterns)

---

## 3. Authentication Flows Fail

**Symptoms:**
- "Unauthorized" or "403 Forbidden" errors
- API key not being sent with requests
- OAuth token expired or invalid
- Credentials work locally but fail when deployed

**Root Causes:**
- Environment variables not set in deployment environment
- Credentials expired or revoked
- Wrong header format for API authentication (Bearer vs Basic)
- OAuth redirect URI doesn't match registration
- Missing scopes in OAuth request
- Credentials accidentally hardcoded instead of using env vars

**Debugging Commands:**

```bash
# Verify environment variables are accessible
node -e "const k = process.env.API_KEY; console.log('Key set:', !!k, '| Length:', k?.length, '| Prefix:', k?.substring(0, 4) + '***')"

# Check if file-based credentials exist
test -f ~/.aws/credentials && echo "AWS creds found" || echo "AWS creds missing"
test -f ~/.config/github-cli/hosts.yml && echo "GitHub token found" || echo "GitHub token missing"

# Validate API key format before use
node -e "const key = process.env.API_KEY; console.log('Key length:', key?.length); console.log('Key prefix:', key?.substring(0, 10));"

# Test API authentication directly
curl -H "Authorization: Bearer $API_KEY" https://api.example.com/v1/test
curl -H "X-API-Key: $API_KEY" https://api.example.com/v1/test  # Alternative header

# Check OAuth token expiration
node -e "const payload = JSON.parse(Buffer.from(process.env.OAUTH_TOKEN.split('.')[1], 'base64url').toString()); console.log('Expires:', new Date(payload.exp * 1000));"

# For deployed servers, check what environment was actually loaded
# Add this to your server initialization:
console.error('Auth check:', {
  hasApiKey: !!process.env.API_KEY,
  keyLength: process.env.API_KEY?.length,
  keyPrefix: process.env.API_KEY?.substring(0, 10) + '***'
});
```

**Prevention:**
- Never hardcode credentials; always use environment variables
- Create `.env.example` with placeholder values for all required credentials
- Document which credentials are optional vs. required
- Use dotenv library to load `.env` file in development
- Log credential status at startup (without exposing actual values)
- Implement credential validation on server start that fails fast
- For deployed servers, use platform-native secrets management (GitHub Secrets, Fly.io Secrets, etc.)
- Test auth independently before testing tools: `curl` with credentials first

---

## 4. Client Connection Timeouts

**Symptoms:**
- "Connection timeout" error after 30 seconds
- Client can't find server
- Stdio transport works locally but not in MCP Inspector
- Streamable HTTP server never receives requests

**Root Causes:**
- Server process crashes before client connects
- Wrong port/hostname in client configuration
- Firewall blocking connections
- Server thread deadlocks during initialization
- Incorrect stdio transport setup (stdin/stdout not properly connected)
- Server takes too long to initialize (exceed default timeout)

**Debugging Commands:**

```bash
# For stdio transport, test directly
npx @modelcontextprotocol/inspector stdio node dist/index.js

# For HTTP transport, verify server is listening
lsof -i -n -P | grep LISTEN  # See all listening ports
curl http://localhost:3000/ -v  # Try to reach server directly

# Monitor server startup time
time npm start  # Measure total startup duration

# Check if process is using all CPU (deadlock indicator)
top -n1 | grep node  # See if CPU% is stuck at 100

# For stdio issues, run server directly to see output
node dist/index.js  # If it hangs here, initialization is blocking
# Try interrupt (Ctrl+C) to see if it's truly stuck

# Check for port binding issues
ss -tlnp | grep 3000  # Linux
netstat -tlnp | grep 3000  # Linux alternative
lsof -i TCP:3000  # macOS/BSD

# Test server connectivity with timeout
timeout 5 curl -v http://localhost:3000/ || echo "Connection failed or timeout"
```

**Prevention:**
- Add startup logging: log when server starts, log after each major initialization step
- Implement a health check endpoint: `GET /health` returns `200 OK`
- Use MCP Inspector for testing (it catches connection issues quickly)
- Keep server initialization lightweight; defer expensive operations to first request
- Set explicit timeouts on external API calls (don't leave them hanging indefinitely)
- Test stdio transport with `npx @modelcontextprotocol/inspector stdio <command>`
- For HTTP transport, expose `/health` and test it independently
- Monitor memory usage during startup (leaks indicate problems)

---

## Systematic Debugging Workflow

When your MCP server isn't working:

1. **Check logs first**: Most failures are logged. Run with verbose output:
   ```bash
   NODE_DEBUG=* npm start 2>&1 | head -50
   ```

2. **Use MCP Inspector**: Start it independently and select your server:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
   It shows schema errors, connection issues, and tool execution failures clearly.

3. **Test in isolation**: Before testing with a client, verify server works standalone:
   ```bash
   npm run build && node dist/index.js
   ```

4. **Check external dependencies**: Verify API credentials, network access, firewall:
   ```bash
   curl -v https://api.example.com/  # Does API respond?
   ```

5. **Add instrumentation**: When stuck, add logging to understand what's happening:
   ```typescript
   server.setRequestHandler(Tool, async (request) => {
     console.error('Tool called:', request.params.name);
     try {
       // implementation
       console.error('Tool succeeded');
     } catch (error) {
       console.error('Tool failed:', error);
       throw error;
     }
   });
   ```

---

# Reference Files

## 📚 Documentation Library

Load these resources as needed during development:

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with sitemap at `https://modelcontextprotocol.io/sitemap.xml`, then fetch specific pages with `.md` suffix
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
  - Server and tool naming conventions
  - Response format guidelines (JSON vs Markdown)
  - Pagination best practices
  - Transport selection (streamable HTTP vs stdio)
  - Security and error handling standards

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- **TypeScript SDK**: Fetch from `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`

### Language-Specific Implementation Guides (Load During Phase 2)
- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/FastMCP guide with:
  - Server initialization patterns
  - Pydantic model examples
  - Tool registration with `@mcp.tool`
  - Complete working examples
  - Quality checklist

- [⚡ TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide with:
  - Project structure
  - Zod schema patterns
  - Tool registration with `server.registerTool`
  - Complete working examples
  - Quality checklist

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts
