---
name: agent-engineering
description: >-
  Battle-tested engineering principles for AI coding agents. Covers plan-first workflow,
  subagent delegation, self-improvement loops, verification gates, elegant solutions,
  autonomous bug fixing, and structured task management. Use when configuring agent
  behavior, writing AGENTS.md files, or improving agent reliability and code quality.
metadata:
  openclaw:
    emoji: "🏗️"
    tags: ["agents", "engineering", "best-practices", "workflow", "coding"]
---

# Agent Engineering Principles

Battle-tested principles for AI coding agents that produce reliable, high-quality work.

## When to Use This Skill

- Writing or reviewing an `AGENTS.md` / `CLAUDE.md` / `CURSOR.md` file for a project
- Configuring a new AI coding agent or subagent
- Diagnosing why an agent keeps making the same mistakes
- Reviewing agent output quality and identifying systemic issues
- Onboarding an agent to a complex codebase

## 1. Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

**When to skip:** Simple, single-file edits with obvious solutions.

**Example plan format (`tasks/todo.md`):**
```markdown
## Task: Migrate auth to JWT

### Plan
- [ ] Audit current session-based auth flow
- [ ] Design JWT payload schema (user_id, roles, expiry)
- [ ] Implement token generation in auth service
- [ ] Update middleware to validate JWT
- [ ] Write tests for edge cases (expired, invalid, revoked)
- [ ] Update docs

### Done
- [x] Audit complete — 4 routes need updating
```

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

**Key insight:** Context window pollution is the #1 cause of agent quality degradation. Subagents are cheap — use them.

**When to spawn a subagent vs. do it inline:**

| Use a subagent | Do inline |
|---|---|
| Research task (>10 files) | Simple 1-file edit |
| Independent parallel work | Quick config change |
| Long-running compilation or test run | Single command with clear output |
| Isolated experiment (risky change) | Trivial refactor |

## 3. Self-Improvement Loop

After ANY correction from the user:

1. Update `tasks/lessons.md` (or equivalent) with the pattern
2. Write rules for yourself that prevent the same mistake
3. Ruthlessly iterate on these lessons until mistake rate drops
4. Review lessons at session start for relevant project

### Lessons Format

```markdown
## Lesson: [Short title]
- **Trigger:** What went wrong
- **Rule:** What to do instead
- **Added:** [date]
```

**Example lesson:**
```markdown
## Lesson: Don't mutate shared config objects
- **Trigger:** Modified `config.defaults` directly, breaking other callers
- **Rule:** Always deep-clone config before modifying; treat config objects as read-only
- **Added:** 2026-03-15
```

**This is the most underused agent pattern.** Most agents make the same mistakes repeatedly because they have no feedback mechanism. A lessons file closes the loop.

## 4. Verification Before Done

- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

**Anti-pattern:** "I've made the changes" without evidence they work.

**Verification checklist before marking done:**
- [ ] Tests pass (`npm test` / `pytest` / `go test ./...`)
- [ ] No new lint errors
- [ ] Manual smoke test of the changed code path
- [ ] Diff reviewed for unintended changes
- [ ] Edge cases (empty input, error paths, concurrent access) considered

## 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

**The balance:** Elegance matters for code that will be maintained. For throwaway scripts, ship it.

**Elegance signals:** Code reads like prose. New engineers understand it without explanation. The abstraction boundaries are obvious. There's nothing to add, and nothing to remove.

**Over-engineering signals:** 3 abstraction layers for a 20-line problem. Generic framework for a one-time use. "We might need this later" reasoning.

## 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

**Rule of thumb:** If you can see the error and understand the codebase, fix it. Only ask when genuinely blocked.

**Blocked means:**
- The fix requires a product/UX decision (not a technical one)
- You need access/credentials you don't have
- Two reasonable fixes have significantly different tradeoffs and the owner should choose

## 7. Task Management Cycle

For any non-trivial task, follow this 6-step cycle:

1. **Plan First:** Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan:** Check in before starting implementation
3. **Track Progress:** Mark items complete as you go
4. **Explain Changes:** High-level summary at each step
5. **Document Results:** Add review section to `tasks/todo.md`
6. **Capture Lessons:** Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.
- **Prove It Works:** Tests, logs, evidence. Not just "it should work."
- **Learn From Mistakes:** Every correction becomes a permanent rule.
- **Respect Context:** Keep main context clean. Delegate ruthlessly.
- **Ship, Don't Discuss:** Bias toward action. Fix it, don't debate it.

## Common Failure Patterns (Anti-Patterns)

### The Endless Loop
Agent keeps retrying the same failing approach with minor variations. **Fix:** Stop, re-read the error, consult the lessons file, try a fundamentally different approach.

### Context Drift
After 20+ tool calls, the agent loses track of the original goal and starts solving adjacent problems. **Fix:** Re-read the original task at each major milestone.

### Premature Confidence
Agent marks a task done based on "the code looks right" without running it. **Fix:** Always run tests/commands, never assume.

### Scope Creep
Fixing a bug, agent also refactors unrelated code "while it's in there." **Fix:** One change, one commit. Refactors go in separate PRs.

### Silent Failure
Command exits with 0 but nothing actually changed (e.g., dry-run mode left on). **Fix:** Verify the change happened (check logs, diff, reload config).

## Applying These Principles

### For AGENTS.md / CLAUDE.md Files

Add the relevant principles directly to your project's agent configuration:

```markdown
## Engineering Standards

### Before Starting
- [ ] Read tasks/lessons.md for this project
- [ ] Plan non-trivial work in tasks/todo.md
- [ ] Verify plan before implementing

### While Working
- [ ] One task per subagent
- [ ] Verify each step works before moving on
- [ ] Track progress in todo.md

### Before Marking Done
- [ ] Run tests / check logs
- [ ] "Would a staff engineer approve this?"
- [ ] Update lessons.md if any corrections were made
```

### For CI/Review Integration

These principles map well to PR review automation:
- **Verification (#4)** → Require test evidence in PR descriptions
- **Elegance (#5)** → Code review checklist item
- **Lessons (#3)** → Post-merge retrospective notes

### Bootstrapping a New Project

For a new codebase with no `tasks/` directory:
```bash
mkdir tasks
echo "# Todo\n\n(empty)" > tasks/todo.md
echo "# Lessons\n\n(empty)" > tasks/lessons.md
```

Then add both files to `.gitignore` if they're agent-local, or track them if the team shares them.

## References

Inspired by community-shared agent engineering patterns (March 2026).
