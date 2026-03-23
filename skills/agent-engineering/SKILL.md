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
    tags: ["agents", "engineering", "best-practices", "workflow"]
---

# Agent Engineering Principles

Battle-tested principles for AI coding agents that produce reliable, high-quality work.

## 1. Plan Mode Default

- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

**When to skip:** Simple, single-file edits with obvious solutions.

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

**Key insight:** Context window pollution is the #1 cause of agent quality degradation. Subagents are cheap — use them.

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

**This is the most underused agent pattern.** Most agents make the same mistakes repeatedly because they have no feedback mechanism. A lessons file closes the loop.

## 4. Verification Before Done

- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

**Anti-pattern:** "I've made the changes" without evidence they work.

## 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

**The balance:** Elegance matters for code that will be maintained. For throwaway scripts, ship it.

## 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

**Rule of thumb:** If you can see the error and understand the codebase, fix it. Only ask when genuinely blocked.

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

## References

Inspired by community-shared agent engineering patterns (March 2026).
