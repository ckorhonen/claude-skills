# What an Idea.md Is

`Idea.md` is not a universal software standard like `README.md` or `package.json`. In practice, it appears in several adjacent forms:

## Observed patterns

### 1. Freeform scratchpad

In [rxxuzi/hype](https://skills.sh/rxxuzi/hype/hype), `.hype/IDEA.md` is described as a **freeform idea scratchpad**. It is explicitly user-owned, append-only, and not part of the main execution cycle.

### 2. Early planning artifact

In [atrislabs/atris](https://github.com/atrislabs/atris), the README says the workflow creates `atris/features/[name]/idea.md` alongside `build.md` and `validate.md`. That makes `idea.md` an early artifact in a structured plan/build/review loop.

### 3. Input to downstream product docs

The [prd-generator skill](https://agentskills.so/skills/luongnv89-skills-prd-generator) treats `idea.md` as a required input containing product concept and technical context before generating `prd.md`.

### 4. Simple repository idea list

In [MrKumaran/macOS-Shortcut-Automations](https://github.com/MrKumaran/macOS-Shortcut-Automations), `Idea.md` is documented as a list of brainstormed automation ideas and notes.

## Working definition for this skill

For `claude-skills`, the most useful default is:

> A concise, structured concept brief that captures an idea clearly enough to validate, discuss, or turn into a PRD later.

That means the default `Idea.md` should usually include:

- the problem
- the target user
- the proposed solution
- why it might work
- how it fits the current repo or technical context
- what remains uncertain
- the next validation steps

## Boundary with adjacent docs

### Idea.md vs scratch notes

Scratch notes are allowed to be messy and fragmented. `Idea.md` should be readable by someone who was not present for the original brainstorm.

### Idea.md vs PRD

A PRD specifies requirements, scope, acceptance criteria, and delivery details. `Idea.md` should stop earlier, at concept definition and initial framing.

### Idea.md vs implementation plan

An implementation plan answers "how exactly do we build this?" `Idea.md` should answer "what is the idea, why does it matter, and what should we validate next?"
