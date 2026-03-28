---
name: writing-plans
description: Write structured implementation plans from specs or requirements before touching code. Use when given a spec, requirements doc, or feature description, when user says "plan this out", "write a plan for", "how should we implement", or before starting any multi-step coding task.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use the executing-plans skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Common Pitfalls

### 1. Plans Too Abstract (No Concrete Paths or Commands)

**Symptom:** Plan reads smoothly but lacks actionable details. Steps like "Add validation" or "Update the API handler" leave the engineer guessing which file, which function, or what commands to run.

**Why it fails:**
- Engineer wastes time hunting for the right file or inferring code structure
- Different engineers interpret abstract steps differently, leading to rework
- No way to verify the plan is complete until someone starts implementing

**How to fix:**
- Always include exact file paths: `src/handlers/user.ts` not `update the handler`
- Always include exact commands: `pytest tests/handlers/test_user.py -v` not `run tests`
- Always include complete code in fenced blocks, not pseudocode
- Provide line numbers when modifying existing files: `Modify: src/handlers/user.ts:45-62`

**Example (bad vs good):**
```
❌ BAD: "Update the validation logic to handle email addresses"
✅ GOOD: "Modify: src/validators/email.py:12-18. Replace the regex pattern with: re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')"
```

---

### 2. Task Granularity Wrong (Steps Too Large or Too Small)

**Symptom:** Steps are either vague epics ("Build the authentication system") or so granular they create friction ("Import the module", "Define the function signature", "Write the function body").

**Why it fails:**
- Large steps: engineer lacks guardrails; easy to implement wrong thing
- Small steps: excessive context switching; commits become noise; hard to trace intent
- Either way, progress becomes hard to measure and verify

**How to fix:**
- Target 2-5 minute steps: small enough to verify and commit independently, large enough to be meaningful
- Group related micro-steps under a single task heading, then break them into numbered steps
- Each step should produce a git-committable change
- Use this litmus test: "Can I understand and verify this single commit in isolation?"

**Example (bad vs good):**
```
❌ BAD:
  Step 1: Import json
  Step 2: Define function
  Step 3: Write body
  Step 4: Run test

✅ GOOD:
  Step 1: Write failing test for json parsing
  Step 2: Implement minimal function that passes test
  Step 3: Run test and verify PASS
  Step 4: Commit
```

---

### 3. Missing Verification Steps (No Way to Confirm Task Success)

**Symptom:** Plan describes what to do but never says how to verify it's done correctly. Engineer finishes a step and isn't sure if it actually worked.

**Why it fails:**
- Silent failures: code runs but produces wrong result; engineer doesn't catch it
- Wasted debugging time: engineer has to invent their own verification method
- Plan can't be reused reliably because success criteria are ambiguous

**How to fix:**
- Every step that changes behavior must include a verification command
- Verification command must include expected output or success indicator
- For tests: `Expected: PASS`. For commands: `Expected output: [actual output]`
- Include negative cases: "Run: `pytest tests/... -v`. Expected: Should fail with 'ValidationError'"

**Example (bad vs good):**
`````
❌ BAD:
  Step 3: Implement the validation function

✅ GOOD:
  Step 3: Implement the validation function
  
  ```python
  def validate_email(email):
      pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      return bool(re.match(pattern, email))
  ```

  Step 4: Run test to verify it passes
  
  Run: `pytest tests/validators/test_email.py::test_valid_email -v`
  Expected: `PASSED test_valid_email`
`````

---

### 4. DRY Violations (Repeated Instructions Across Tasks)

**Symptom:** Plan repeats the same instruction in multiple tasks ("Run the full test suite", "Import X module", "Follow the naming convention"). Same boilerplate appears in steps across different tasks.

**Why it fails:**
- Maintainability: updating the pattern requires editing multiple places
- Cognitive load: engineer has to understand the intent is the same across tasks
- Error-prone: same instruction might be subtly different in different places, causing confusion

**How to fix:**
- Capture repeated patterns in a "Setup" or "Prerequisites" section at the top of the plan
- Use consistent command syntax and structure across similar steps
- Link to shared instructions: "As per 'Testing' section above, run: `pytest ...`"
- If a pattern is truly repeated, ask: can these tasks be combined or is there a shared utility that would eliminate the duplication?

**Example (bad vs good):**
```
❌ BAD:
  Task 1: Write test, run `pytest tests/handlers/test_a.py -v`, commit
  Task 2: Write test, run `pytest tests/handlers/test_b.py -v`, commit
  Task 3: Write test, run `pytest tests/handlers/test_c.py -v`, commit

✅ GOOD:
  # Testing Pattern
  After each implementation, verify with: `pytest tests/handlers/test_<name>.py -v`
  Expected: All tests PASS
  
  Task 1: [test_a implementation]
  Task 2: [test_b implementation]
  Task 3: [test_c implementation]
```

---

### 5. Assumes Context Agent Won't Have (Framework Specifics, Conventions)

**Symptom:** Plan references "the standard pattern", "as we do it", or "use the company convention" without explaining what that actually means. Assumes engineer knows framework shortcuts, naming conventions, or project structure.

**Why it fails:**
- Fresh engineer or external contributor has no reference for "the pattern"
- Different projects have different conventions; agent may mix them up
- Engineer spends time reverse-engineering conventions instead of following a plan

**How to fix:**
- Explicitly state conventions in a "Context" or "Setup" section at the plan start
- Name the convention if it's framework-specific: "Django model naming: `class MyModel(models.Model)`"
- Provide an example: "All API handlers follow this pattern: [example file + code snippet]"
- If a pattern is specific to this codebase, explain it briefly instead of assuming knowledge

**Example (bad vs good):**
`````
❌ BAD:
  Step 1: Create a handler using the standard pattern
  Step 2: Follow our naming convention for tests

✅ GOOD:
  Context: This project uses Flask. All handlers live in src/handlers/ and follow the pattern:
  ```python
  @app.route('/endpoint', methods=['POST'])
  def handle_endpoint():
      # Handler logic
      return jsonify({...})
  ```
  
  Step 1: Create handler in src/handlers/my_handler.py following the pattern above
  Step 2: Create test in tests/handlers/test_my_handler.py. Naming: test_<function_name>_<scenario>
`````

---

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- Spawn a subagent per task, review results between tasks, fast iteration
- Stay in this session and orchestrate

**If Parallel Session chosen:**
- Guide them to open new session in the git worktree
- **REQUIRED SUB-SKILL:** New session uses the executing-plans skill
