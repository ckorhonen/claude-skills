---
name: mcp-tester
description: Test and evaluate MCP server tools in the current Claude Code session. Use when auditing MCP configurations, validating tool quality, testing MCP servers end-to-end, generating test cases, checking tool descriptions and schemas, analyzing tool efficiency and redundancy, or debugging MCP integration issues. Covers tool discovery, quality analysis, test generation with AAA pattern, execution, rating, and cross-tool redundancy analysis.
---

# MCP Tool Tester

A comprehensive skill for testing and evaluating MCP (Model Context Protocol) server tools available in the current Claude Code session.

## When to Use

Use this skill when:
- Auditing MCP server configurations
- Validating tool quality and descriptions
- Generating test cases for MCP tools
- Checking tool naming conventions and parameter efficiency
- Analyzing tool redundancy across servers
- Evaluating response quality and format efficiency
- Debugging MCP integration issues

## Prerequisites

MCP servers must be configured in your Claude Code settings. If the user asks to test tools that don't exist, guide them to add the MCP server to their configuration.

## Workflow

Execute these phases in order for comprehensive testing:

### Phase 1: Discovery

Identify all MCP tools available in the current session.

**Steps:**
1. List all tools with `mcp__` prefix
2. Group by server (namespace before second `__`)
3. Generate inventory table

**Output Format:**
```markdown
## Tool Inventory

| Server | Tool Name | Required Params | Optional Params | Description Preview |
|--------|-----------|-----------------|-----------------|---------------------|
| context7 | resolve-library-id | libraryName, query | - | Resolves package to Context7 ID... |
| context7 | query-docs | libraryId, query | - | Retrieves documentation... |
```

**Metrics to Report:**
- Total servers: [count]
- Total tools: [count]
- Tools per server breakdown

### Phase 2: Quality Analysis

Evaluate each tool's design quality.

#### Naming Convention Analysis

Check for:
- **Kebab-case consistency**: `get-user` not `getUser` or `get_user`
- **Verb-first naming**: `create-item`, `list-users`, `delete-record`
- **Clarity**: Can purpose be understood from name alone?
- **Namespace collisions**: Similar names across servers

#### Description Quality Scoring

| Score | Criteria |
|-------|----------|
| Excellent | Clear purpose, usage context, examples, input/output expectations |
| Good | Clear purpose, some context, basic expectations |
| Fair | Purpose stated but lacking context or examples |
| Poor | Vague, missing, or misleading description |

Evaluate:
- Does it explain WHAT the tool does?
- Does it explain WHEN to use it?
- Are there example scenarios?
- Are edge cases documented?

#### Parameter Efficiency Analysis

Check:
- **Required vs. optional balance**: Are required params truly necessary?
- **Type specificity**: `enum` vs generic `string` where applicable
- **Default values**: Are sensible defaults provided?
- **Naming clarity**: Can param purpose be understood from name?
- **Token cost**: Estimate description length impact on context

**Token Efficiency Formula:**
```
Efficiency = (Useful information conveyed) / (Token count)
```

Flag tools where description is verbose relative to complexity.

#### Severity Indicators

Use these indicators for findings:

- 🔴 **Critical**: Missing description, unclear purpose, broken schema
- 🟡 **Warning**: Overly verbose description, inefficient parameter schema, unclear naming
- 🔵 **Suggestion**: Minor naming improvements, optional enhancements
- ✅ **Positive**: Well-designed, clear, efficient

**Analysis Output Format:**
```markdown
### Tool: `mcp__server__tool-name`

**Naming**: ✅ Clear verb-first naming
**Description**: 🟡 Warning - Verbose (450 tokens), could be reduced to ~200
**Parameters**: 🔵 Suggestion - Consider enum for `format` param

**Detailed Findings:**
- [Specific observations]

**Recommendations:**
- [Actionable improvements]
```

### Phase 3: Test Design

Generate test cases for each tool using the AAA (Arrange-Act-Assert) pattern.

#### Test Categories

**1. Valid Inputs (Happy Path)**
- Minimal required parameters only
- All parameters with valid values
- Edge of valid ranges (max length strings, boundary numbers)

**2. Invalid Inputs (Error Handling)**
- Missing required parameters
- Wrong parameter types (string where number expected)
- Invalid values (negative IDs, malformed URLs)
- Malformed data structures

**3. Edge Cases**
- Empty strings `""`
- Very long strings (1000+ chars)
- Special characters and unicode
- Null-like concepts (`null`, `undefined`, `None`)
- Boundary values (0, -1, MAX_INT)
- Whitespace only strings

#### Test Case Template

```markdown
### Test: [Tool Name] - [Scenario Name]

**Category**: Valid / Invalid / Edge Case

**Arrange**:
- Context: [What setup is needed]
- Preconditions: [What must be true]

**Act**:
```json
{
  "param1": "value1",
  "param2": "value2"
}
```

**Assert**:
- Expected behavior: [What should happen]
- Expected response format: [Structure]
- Expected error (if invalid): [Error type/message]
```

#### Test Generation Guidelines

For each tool, generate at minimum:
1. 1 happy path test with minimal params
2. 1 happy path test with all params
3. 1 missing required param test
4. 1 wrong type test
5. 1 edge case test (empty/boundary)

### Phase 4: Test Execution

Execute generated tests and capture results.

#### Read-Only Tools
Execute immediately without confirmation:
- Tools that fetch/query data
- Tools that list/search resources
- Tools that analyze/inspect

#### Mutating Tools
**ALWAYS ask for confirmation before testing:**

```markdown
⚠️ **Mutating Tool Detected**

Tool: `mcp__server__create-item`
Operation: Creates new item in external system

**Test Parameters:**
```json
{
  "name": "test-item-12345",
  "type": "test"
}
```

**Potential Effects:**
- Will create a new item in the external system
- May trigger webhooks or notifications
- Item may need manual cleanup

**Proceed with this test?** (yes/no/skip)
```

Mutating operations include:
- `create`, `write`, `post`, `add`, `insert`
- `update`, `edit`, `modify`, `patch`, `put`
- `delete`, `remove`, `destroy`, `clear`
- `send`, `publish`, `trigger`, `execute`

#### Response Capture

For each test, capture:
- Full response content (truncate if > 2000 chars)
- Response time (if perceivable delay)
- Error messages and codes
- Unexpected warnings or notices

### Phase 5: Rating & Feedback

Rate each tool's test results and provide actionable feedback.

#### Rating Criteria

| Rating | Symbol | Criteria |
|--------|--------|----------|
| **Worked** | ✅ | Response matches expected format, no errors, useful output |
| **Partially Worked** | 🟡 | Response returned but incomplete, warnings present, or unexpected format |
| **Failed** | ❌ | Error returned, timeout, or completely wrong behavior |

#### Quality Assessment Dimensions

1. **Response Completeness** (High/Medium/Low)
   - Does it return all expected data?
   - Are there missing fields?

2. **Response Efficiency** (High/Medium/Low)
   - Token usage vs. value provided
   - Unnecessary verbosity in response?

3. **Error Handling** (Clear/Vague/Missing)
   - Are error messages helpful?
   - Do they indicate how to fix the issue?

4. **Format Consistency** (Consistent/Inconsistent)
   - Does response format match description?
   - Is format consistent across calls?

#### Feedback Template

```markdown
## Tool: `mcp__server__tool-name`

### Test Results Summary
| Test | Category | Rating | Notes |
|------|----------|--------|-------|
| Minimal params | Valid | ✅ Worked | Response in 200ms |
| All params | Valid | ✅ Worked | - |
| Missing required | Invalid | 🟡 Partial | Error unclear |
| Wrong type | Invalid | ❌ Failed | No error, silent fail |
| Empty string | Edge | ✅ Worked | Handled gracefully |

### Overall Rating: 🟡 Partially Worked (4/5 tests passed)

### Quality Assessment
- **Completeness**: High - Returns all documented fields
- **Efficiency**: Medium - Response includes redundant metadata
- **Error Handling**: Vague - Errors don't indicate fix
- **Consistency**: Consistent

### Critical Issues
🔴 Silent failure on wrong type - should return validation error

### Improvement Suggestions
1. Add input validation with descriptive error messages
2. Remove redundant `metadata.internal_id` from response (saves ~50 tokens)
3. Consider pagination for list responses
```

### Phase 6: Cross-Tool Analysis

Analyze the tool set as a whole.

#### Redundancy Detection

Look for:
- Tools with overlapping functionality
- Similar operations across different servers
- Duplicate capabilities with different names

**Output Format:**
```markdown
## Redundancy Findings

| Tool A | Tool B | Overlap | Recommendation |
|--------|--------|---------|----------------|
| mcp__a__get-user | mcp__b__fetch-user | 90% same function | Consolidate to single tool |
| mcp__a__list-all | mcp__a__search | Search can replace list | Deprecate list-all |
```

#### Consolidation Opportunities

Identify tools that could be:
- **Merged**: Similar tools into one with mode parameter
- **Batched**: Individual operations into batch operations
- **Simplified**: Complex tools broken into focused ones

#### Missing Capabilities

Note gaps in tool coverage:
- CRUD operations incomplete (has create but no delete)
- Read operations without filtering
- No bulk/batch alternatives to individual operations

#### Efficiency Recommendations

```markdown
## Efficiency Recommendations

### High Impact
1. **Reduce description verbosity** - 3 tools have descriptions >500 tokens
   - Potential savings: ~800 tokens total

### Medium Impact
2. **Add enum constraints** - 5 parameters accept free text but have limited valid values
   - Improves: Validation, documentation, autocomplete

### Low Impact
3. **Standardize naming** - Mix of `get-X` and `fetch-X` patterns
   - Improves: Consistency, discoverability
```

## Output Report Template

Generate this report after completing all phases:

```markdown
# MCP Tool Test Report

**Generated**: [timestamp]
**Session ID**: [if available]

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Servers Tested | [N] |
| Tools Tested | [N] |
| Tests Executed | [N] |
| Pass Rate | [X]% |

### Results Overview
- ✅ **Passed**: [X] tools
- 🟡 **Partial**: [Y] tools
- ❌ **Failed**: [Z] tools

### Key Findings
- 🔴 [N] critical issues requiring immediate attention
- 🟡 [N] warnings to address
- 🔵 [N] suggestions for improvement

---

## Tool Inventory

[Phase 1 output]

---

## Quality Analysis

[Phase 2 output for each tool]

---

## Test Results

[Phase 5 output for each tool]

---

## Cross-Tool Analysis

[Phase 6 output]

---

## Recommendations

### 🔴 Critical (Must Address)
1. [Issue] - [Tool] - [Impact] - [Fix]

### 🟡 Warning (Should Address)
1. [Issue] - [Tool] - [Impact] - [Fix]

### 🔵 Suggestions (Consider)
1. [Improvement] - [Tool] - [Benefit]

---

*Report generated by mcp-tester skill*
```

## Common Pitfalls

This section documents real failure modes and anti-patterns encountered when testing MCP tools. These gotchas are non-obvious and often discovered through painful iteration.

### Test Coverage Incomplete (Missing Edge Cases & Error Paths)

**The Problem:**
Tests pass with happy-path inputs but fail in production with edge cases or error conditions. Missing error path testing creates blind spots in tool reliability.

**Anti-patterns to Avoid:**
- ❌ Only testing with minimal required parameters — tools may break with optional params
- ❌ Testing success paths exclusively — error handling is equally important
- ❌ Using realistic data only — unrealistic values expose schema validation gaps
- ❌ Not testing boundary conditions (max length strings, zero, negative numbers, empty collections)
- ❌ Skipping unicode/special character tests — often reveals encoding issues

**Pattern: Comprehensive Test Matrix**
```
For each tool, test:
✅ Happy path: minimal params
✅ Happy path: all params  
✅ Missing required param (each required param tested separately)
✅ Wrong param type (string to number, number to boolean, etc.)
✅ Invalid enum value (param expects ['active', 'inactive'], test 'disabled')
✅ Empty string / null-like values
✅ Very long strings (1000+ chars, 10K+ chars)
✅ Special characters: !@#$%^&*()_+-={}[]|:;"'<>?,./~`
✅ Unicode: emoji, CJK, RTL text
✅ Boundary values: 0, -1, MAX_INT, Float edge cases
✅ Malformed data: incomplete JSON, null objects, circular references
```

**Impact:** Incomplete test coverage → tools fail when actually used with real-world data

---

### Mocked Dependencies Have Wrong Behavior (Unrealistic Test Data)

**The Problem:**
Tests pass with mocked data but fail when calling real MCP servers. Mock behavior doesn't match actual server behavior — timeouts, error formats, response sizes, etc.

**Anti-patterns to Avoid:**
- ❌ Mocking responses that are too small (mock returns 10 items, real API returns 1000+)
- ❌ Mocking error responses in non-standard formats (real server returns different error shape)
- ❌ Assuming instant responses in mocks — real servers have latency
- ❌ Mocking success when real server requires authentication
- ❌ Not respecting rate limits in mock behavior
- ❌ Mocking null/empty responses when real server returns validation errors

**Pattern: Realistic Mock Behavior**
```
When mocking MCP tool responses:
✅ Return realistic response sizes (don't shrink large responses to 1-2 items)
✅ Match actual error response format (test against real API error docs)
✅ Add realistic latency (~100-500ms for network calls)
✅ Include rate limit headers/indicators in mock
✅ Mock pagination correctly (include next_page token, limits)
✅ Match response schema exactly, including optional fields that are usually present
✅ Test against actual MCP server output when possible (don't guess schema)
```

**Example mismatch:**
```json
// ❌ Mock (too clean)
{ "users": [{ "id": 1, "name": "Alice" }] }

// ✅ Real API (includes metadata, nulls, pagination)
{
  "data": [{ "id": 1, "name": "Alice", "email": null, "tags": [] }],
  "meta": { "total": 5000, "page": 1, "limit": 50, "next": "cursor-xyz" },
  "timing": { "ms": 234 }
}
```

**Impact:** Tests pass locally with mocks but fail against real MCP server

---

### Async Timing Issues (Race Conditions & Timeouts)

**The Problem:**
Tests pass when run individually but fail intermittently when run in parallel. Race conditions in setup/teardown, timeout assumptions that don't hold, or async operations that complete in unpredictable order.

**Anti-patterns to Avoid:**
- ❌ Assuming tools respond within a fixed timeout (e.g., "all tools respond in <1sec")
- ❌ Running tests in parallel without proper isolation
- ❌ Not awaiting async operations before assertions
- ❌ Reusing MCP server connections across tests without proper reset
- ❌ Assuming specific execution order in concurrent test runs
- ❌ Setting arbitrary timeout values without testing against real latency
- ❌ Not handling server warmup time (first request slower than subsequent)

**Pattern: Robust Async Testing**
```
✅ Set timeouts per tool (measure real response times first)
✅ Use proper async/await or .then() chains — no unhandled promises
✅ Isolate tests: each test gets fresh MCP server connection if possible
✅ Add explicit setup/teardown phases with proper waiting
✅ For concurrent tests: use semaphores/locks to prevent interference
✅ Test with real latency: add 100-500ms overhead to account for network
✅ Run tests multiple times to catch intermittent failures
✅ Use flake detection: run failing tests 5x to confirm it's not timing
```

**Example race condition:**
```javascript
// ❌ No await - assertion runs before operation completes
const test = () => {
  callMCPTool({ param: "value" });
  assert(responseReceived); // Fails! Call still pending
};

// ✅ Proper await
const test = async () => {
  const response = await callMCPTool({ param: "value" });
  assert(response.success); // Now it's safe to assert
};
```

**Impact:** Flaky tests that pass sometimes, fail others → low confidence in test results

---

### Tool Schema Validation Gaps (Invalid Parameters Accepted)

**The Problem:**
Tools accept invalid parameter values that should be rejected by schema validation. MCP schema validation is incomplete, allowing garbage input to propagate to the server, causing cryptic errors downstream.

**Anti-patterns to Avoid:**
- ❌ Not testing required parameter validation (missing required param should error)
- ❌ Assuming enum validation works (test that invalid enum values are rejected)
- ❌ Not checking type coercion (tool might accept string "123" where number 123 is required)
- ❌ Skipping length/pattern validation (string can be 1 char or 10K chars?)
- ❌ Not testing nested object schema (required fields in sub-objects)
- ❌ Assuming null is rejected when it should be (or vice versa)
- ❌ Not checking mutual exclusivity constraints (param A and B can't both exist)

**Pattern: Comprehensive Schema Testing**
```
For each parameter:
✅ Test missing (should fail if required)
✅ Test wrong type (if expects number, pass string)
✅ Test enum validation (if expects ['a','b','c'], test 'd')
✅ Test length constraints (min/max length for strings)
✅ Test pattern/format validation (regex patterns, URLs, emails)
✅ Test numeric bounds (min/max for numbers, negative values)
✅ Test nested object structure (all required fields present?)
✅ Test null vs undefined behavior
✅ Test special characters in string params
✅ Validate response schema (returned data matches documented format)
```

**Example validation gap:**
```javascript
// Tool spec says: name (required, string, max 255 chars)
// Test reveals:
callMCPTool({ name: 123 }) // ❌ Accepted! Should reject (not a string)
callMCPTool({ name: "a".repeat(1000) }) // ❌ Accepted! Should reject (>255 chars)
callMCPTool({ }) // ❌ Accepted! Should reject (required param missing)
```

**Impact:** Invalid requests accepted by tool → confusing errors from MCP server, hard to debug root cause

---

### Integration Test Failures (Server/Client Mismatch)

**The Problem:**
Tools work in unit tests against mocks but fail during integration testing against a real MCP server. The tool schema doesn't match server expectations, response format is different, or endpoint has changed.

**Anti-patterns to Avoid:**
- ❌ Only unit testing with mocks — skipping integration tests
- ❌ Testing tools in isolation without calling actual MCP server
- ❌ Not updating tests when MCP server API changes
- ❌ Assuming backward compatibility — old test data fails with new server version
- ❌ Not testing authentication/authorization in integration tests
- ❌ Skipping permission/scope validation (tool spec says it needs permission X)
- ❌ Testing happy path only in integration — not error scenarios

**Pattern: Integration Testing**
```
Separate unit tests (mocks) from integration tests (real server):

✅ Unit tests: test schema validation, parameter handling, response parsing
✅ Integration tests: call actual MCP server with real credentials/permissions
✅ Version your integration tests: document which server version they test
✅ Test error paths in integration: wrong credentials, missing permissions, server errors
✅ Validate response against schema in integration tests
✅ Test server downtime handling (timeouts, retries)
✅ Test against multiple server versions if applicable
✅ Use test fixtures: real-world data from actual server responses
```

**Example mismatch:**
```javascript
// Unit test passes
callMCPTool({ userId: 123 }) // ✅ Mock returns { user: { id: 123 } }

// Integration test fails  
callMCPTool({ userId: 123 }) // ❌ Real server expects { user_id: 123 } (different key!)
```

**Impact:** Tests pass locally but fail in CI/production against real MCP server

---

### Prevention Strategy

Use this checklist before finalizing tool tests:

- [ ] All parameters tested: required, optional, wrong type, invalid value, boundary
- [ ] Edge cases covered: empty, very large, unicode, special characters
- [ ] Error paths tested: every possible error condition
- [ ] Mocks match reality: response size, format, latency, errors
- [ ] Async operations properly awaited: no race conditions
- [ ] Timeouts reasonable: based on actual measurements, not guesses
- [ ] Schema validation tested: rejects invalid input appropriately
- [ ] Integration tests included: tests against real MCP server
- [ ] Version compatibility verified: tool works with current server version
- [ ] Tests run multiple times: confirms no flakiness or timing issues

---

## Examples

### Example 1: Test All Available Tools

**User**: "Test all my MCP tools"

**Response Flow**:
1. Discover 3 servers with 8 total tools
2. Present inventory table for confirmation
3. Analyze quality (2 warnings, 1 suggestion found)
4. Generate 40 test cases (5 per tool)
5. Identify 2 mutating tools, ask confirmation
6. Execute tests, capture results
7. Rate: 6 passed, 1 partial, 1 failed
8. Analyze cross-tool: 1 redundancy found
9. Generate full report

### Example 2: Test Specific Server

**User**: "Test just the context7 MCP tools"

**Response Flow**:
1. Filter to context7 server (2 tools)
2. Deep analysis of both tools
3. Generate 10 test cases
4. No mutating tools - execute all
5. Generate focused report

### Example 3: Quality Audit Only

**User**: "Audit my MCP tool descriptions without running tests"

**Response Flow**:
1. Discovery phase
2. Full quality analysis
3. Skip test execution
4. Provide quality-focused report with improvement recommendations

### Example 4: Missing MCP Server

**User**: "Test the notion MCP tools"

**Response**:
```markdown
I don't see any Notion MCP tools in the current session.

To add a Notion MCP server:

1. Install the server:
   ```bash
   npm install -g @notionhq/notion-mcp-server
   ```

2. Add to your Claude Code MCP config (`~/.claude/mcp_settings.json`):
   ```json
   {
     "mcpServers": {
       "notion": {
         "command": "notion-mcp-server",
         "env": {
           "NOTION_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

3. Restart Claude Code to load the new server

Would you like me to help you configure this?
```

## Error Recovery

If a test fails or times out:
1. Log the failure with available details
2. Continue testing remaining tools
3. Include failure in final report
4. Suggest debugging steps for failed tools

## MCP Inspector: Standalone Testing

For testing outside of Claude Code sessions, use the MCP Inspector:

```bash
# Launch MCP Inspector UI (browser-based)
npx @modelcontextprotocol/inspector

# Test a specific stdio server
npx @modelcontextprotocol/inspector stdio node /path/to/server.js

# Test a specific HTTP server
npx @modelcontextprotocol/inspector http http://localhost:3000/mcp

# With environment variables
MCP_API_KEY=your-key npx @modelcontextprotocol/inspector stdio node server.js
```

The MCP Inspector provides:
- Interactive tool calling UI
- Schema validation display
- Request/response inspection
- Server capability discovery

## Debugging MCP Connection Issues

```bash
# Check if MCP server process starts correctly
node dist/index.js  # Should hang waiting for input (stdio) or log port (HTTP)

# Test stdio protocol manually
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | node dist/index.js

# Check server logs (stderr for stdio servers)
node dist/index.js 2>server.log &
# Then interact, then cat server.log

# For HTTP servers
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Limitations

- Cannot test MCP tools not configured in current session
- Does not make direct HTTP requests to MCP server URLs
- Cannot test tools requiring interactive authentication mid-flow
- Response time measurements are approximate (based on perceived delay)
- MCP Inspector required for testing server startup issues and protocol compliance
