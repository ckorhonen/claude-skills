---
name: brainstorming
description: "Use before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation to prevent costly rework and misaligned assumptions."
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

## Why Design-First?

Presenting a design before implementation prevents several costly failure modes:
- **Misaligned assumptions** — Coding toward the wrong goal is expensive to unwind
- **Scope creep** — Design clarifies boundaries; implementation without it invites feature bloat
- **Architecture rework** — Early code often creates structural debt that compounds
- **Wasted specialization** — Implementation skills are powerful but wasteful without clear direction

This applies to every project, including simple ones. A todo list, single-function utility, or config change can all ship the wrong thing. The design can be concise for simple projects (a few sentences), but it should exist and be approved before implementation begins.

## Anti-Pattern: "This Is Too Simple To Need A Design"

"Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but presenting it and getting approval is essential. This small friction upfront prevents larger misalignment later.

## Workflow

Work through these phases systematically. Each step builds on the previous one:

1. **Explore project context** — check files, docs, recent commits to ground the conversation in reality
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation to show you've considered alternatives
4. **Present design** — in sections scaled to their complexity, get user approval after each section
5. **Write design doc** — save to `docs/plans/YYYY-MM-DD-<topic>-design.md` and commit to preserve decisions
6. **Transition to implementation** — invoke writing-plans skill to create the detailed implementation plan

## Process Flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write design doc" [shape=box];
    "Invoke writing-plans skill" [shape=doublecircle];

    "Explore project context" -> "Ask clarifying questions";
    "Ask clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write design doc" [label="yes"];
    "Write design doc" -> "Invoke writing-plans skill";
}
```

**The next step is invoking writing-plans** to move from design to detailed planning. Other implementation skills (frontend-design, mcp-builder, etc.) come after the plan is written. This sequencing ensures the implementation plan itself has been validated and can guide the work effectively.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation:**
- Invoke the writing-plans skill to create a detailed implementation plan
- Do NOT invoke any other skill. writing-plans is the next step.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense

## Common Pitfalls

### 1. Skipping Brainstorming for "Simple" Tasks

**What happens:** You recognize a task as straightforward (single component, small utility, config change) and proceed directly to implementation, planning to sort out details while coding.

**Why it backfires:** "Simple" tasks are where assumptions are most dangerous because they feel obvious. You code one behavior, the user expected another, and by the time you learn this the scaffolding is already in place and needs rework.

**How to avoid it:** Treat simplicity as a reason to make brainstorming *faster*, not to skip it. A 30-second conversation ("This is a single-file utility that does X, right?") prevents a 30-minute refactor. Even explicit agreement on what seems obvious is valuable.

### 2. Proceeding to Code Before Explicit User Approval

**What happens:** You present a design, the user asks a clarifying question, and you interpret that as mild interest and start writing code while "thinking about their feedback."

**Why it backfires:** The user is still evaluating. Code written before approval is often code that needs rewriting. You've signaled that you're moving forward when the design isn't locked down.

**How to avoid it:** Wait for explicit approval language ("Looks good," "Let's go with that," "Ship it") before invoking writing-plans. A single clarifying question means the design isn't final — revise and re-present.

### 3. Invoking Implementation Skills Directly Instead of Writing Plans

**What happens:** After design approval, you're tempted to jump straight to frontend-design, mcp-builder, or another implementation skill rather than invoke writing-plans first.

**Why it backfires:** Implementation skills are powerful but unstructured. They work best when given a detailed plan that specifies scope, acceptance criteria, and technical decisions. Skipping the plan means the skill has to reinvent it, leading to inefficient work and potential scope creep.

**How to avoid it:** Always invoke writing-plans as the bridge between brainstorming and implementation. Let it formalize the decisions from brainstorming into a concrete plan that implementation skills can follow.

### 4. Designs That Are Too Abstract to Implement

**What happens:** You present a design that's philosophically sound but lacks concrete details — "We'll have a responsive grid that shows items" without saying how many columns, what breakpoints, or how filtering works.

**Why it backfires:** Implementation starts with questions because the design doesn't answer them. You end up in a loop where the implementer has to guess at details, implement them wrong, and you have to revise.

**How to avoid it:** Make designs concrete enough that an implementer can start work without opening the design doc and asking questions. Include examples, specific numbers, edge cases, and trade-off decisions. If a detail feels unclear to you, it'll be unclear during implementation.
