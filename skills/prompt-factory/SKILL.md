---
name: prompt-factory
description: Generate world-class, production-ready prompts in one shot through intelligent 5-7 question flow and 69 presets across 15 professional domains. Supports XML/Claude/ChatGPT/Gemini formats with quality validation. Returns a single mega-prompt ready to use—skill does NOT implement the work described in the prompt.
---

# Prompt Factory - World-Class Prompt Powerhouse

Generate production-ready mega-prompts through intelligent questioning and comprehensive domain presets.

---

## ⚠️ CRITICAL CONSTRAINTS - READ FIRST

**This skill generates PROMPTS only. It does NOT implement the work described in the prompt.**

### What This Skill DOES:
✅ Generate a comprehensive PROMPT (text document in chosen format)
✅ **Ask 5-7 questions to understand requirements** (MANDATORY - no skipping)
✅ Validate prompt quality before delivery
✅ Output a SINGLE prompt document with token count
✅ Provide the prompt ready to copy and use elsewhere

### What This Skill DOES NOT Do:
❌ Implement the actual work (no code files, no diagrams, no APIs)
❌ Create architectural diagrams or technical implementations
❌ Write actual marketing campaigns or business strategies
❌ Build infrastructure or deploy anything
❌ Execute the prompt after generating it

### Expected Workflow:
1. User asks for help creating a prompt
2. **Skill MUST ask 5-7 questions** (even if context seems obvious)
3. User answers questions with specific details
4. Skill generates ONE comprehensive prompt document
5. Skill announces token count
6. **STOP** - Do not implement anything from the prompt
7. Ask: "Would you like me to modify the prompt or create a variation?"

---

## Gotchas & Common Pitfalls

### 1. Skipping Questions
**Danger:** Agent rushes to prompt generation without asking questions
- **Why it breaks:** Vague prompts miss key context, leading to poor outputs when user applies them
- **Fix:** ALWAYS ask 5-7 questions minimum, even for "obvious" requests
- **Example**: User says "PM prompt for PRD" but doesn't specify domain, constraints, or team context
  - Wrong: Jump to generate PM preset
  - Right: Ask: domain, PRD type, team size, constraints, success criteria

### 2. Implementing Instead of Generating
**Danger:** Agent starts coding/building the thing the prompt describes
- **Why it breaks:** Scope creep; this skill only makes prompts, not implementations
- **Fix:** Generate the prompt → Stop → Offer variations only
- **Example**: Prompt describes "REST API for payments"
  - Wrong: Start coding the API
  - Right: Generate prompt → User takes prompt elsewhere to implement

### 3. Conflating with PROMPTS_FACTORY_PROMPT.md
**Danger:** User asks "make a prompt system for FinTech" and you generate one mega-prompt
- **Why it breaks:** That's a meta-prompt task (building a prompt builder), not a single role prompt
- **Fix:** Redirect to PROMPTS_FACTORY_PROMPT.md for domain-wide builders
- **Difference:**
  - **This skill:** One prompt for one role (e.g., "FinTech PM") → ~5K tokens
  - **Meta-prompt:** Entire FinTech system with 10-20 role presets → generate with PROMPTS_FACTORY_PROMPT.md

### 4. Token Count Inflation
**Danger:** Generated prompts exceed optimal ranges (core: 3-6K, advanced: 8-12K)
- **Why it breaks:** Oversized prompts are harder to use; undersized prompts lack specificity
- **Fix:** Apply optimization tips from `references/prompt-patterns.md`
- **Monitor:** Announce token count; flag if core >8K or advanced >15K

### 5. Generating Multiple Formats by Default
**Danger:** Generating all 4 formats when user asked for one
- **Why it breaks:** Token bloat; user only needs one format
- **Fix:** Ask for format preference first; only generate all formats if user requests
- **Default:** XML (optimal for LLM parsing)

### 6. Weak Question Flow
**Danger:** Asking 7 generic questions, not 5-7 contextually relevant ones
- **Why it breaks:** Questions don't validate assumptions; responses lack specificity
- **Fix:** Use smart adaptation in `references/advanced-workflow.md` → Skip truly redundant questions, emphasize domain/constraints
- **Example**: If user specifies "React 18 + TypeScript," skip tech stack question
  - Still ask: domain, task, constraints, success criteria (always validate)

---

## Quick Start: Choose Your Path

### Path 1: Quick-Start Preset (Fastest)
**Use when:** You need a prompt for a common role

1. User says: "I need a prompt for [preset name]"
2. Confirm the preset matches their need
3. Customize any variables (optional)
4. Generate → Deliver with token count
5. Ask: "Want a variation or different format?"

**Available Presets:** 69 across 15 domains (see `references/presets.md`)

### Path 2: Custom Prompt (5-7 Questions - MANDATORY)
**Use when:** Building a unique prompt from scratch

1. Detect intent from user request
2. **MUST ask 5-7 questions** with example answers (mandatory - even for "obvious" requests)
3. Apply contextual best practices
4. Validate quality → Deliver with token count
5. Ask: "Want to modify the prompt or try a different format?"

**Full 8-step workflow:** See `references/advanced-workflow.md`

---

## Expected Output Formats

Choose one or generate all:

1. **XML** (default) — Optimal for LLM parsing with structured tags
2. **Claude** — Claude system prompt format
3. **ChatGPT** — Custom instructions format
4. **Gemini** — Google Gemini format
5. **All** — Generate all 4 formats (use sparingly - token heavy)

See `references/examples.md` for complete examples of each format.

---

## Generation Modes

1. **Core** (default) — Prompt + instructions + 2-3 examples (~4-6K tokens)
2. **Advanced** — Core + testing scenarios + variations + optimization tips (~10K tokens)

---

## Quality Validation (7-Point Gates)

Before delivery, validate:

1. ✓ XML Structure valid (if XML format)
2. ✓ Completeness — All questions incorporated
3. ✓ Token Count optimal (core: 3-6K, advanced: 8-12K)
4. ✓ No Placeholders — All `[...]` filled
5. ✓ Actionable Workflow — Clear, executable steps
6. ✓ Best Practices applied contextually
7. ✓ Examples present (minimum 2)

**If validation fails:** Fix before delivery.

---

## Token Count Announcement

After generating, announce:
- "**Token Count:** ~4,200 tokens (Core mode - within optimal range ✅)"
- "**Token Count:** ~10,500 tokens (Advanced mode - comprehensive ✅)"
- "**Token Count:** ~7,800 tokens (Warning: Higher than typical Core mode)"

---

## Reference Files

Read on-demand based on context:

| File | When to Use | Contains |
|------|------------|----------|
| `references/presets.md` | User asks for quick-start | 69 preset names, domains, use cases |
| `references/advanced-workflow.md` | Custom prompt path (Path 2) | 8-step workflow, detailed questions, validation |
| `references/prompt-patterns.md` | During generation | Best practices (OpenAI/Anthropic/Google), pattern library, template matching |
| `references/examples.md` | Format clarification | 2-3 worked examples per format (XML, Claude, ChatGPT, Gemini) |

---

## Common Questions

**"Do you implement the prompt after generating it?"**
→ No. This skill makes prompts only. Once generated, you take it elsewhere to implement or use with another LLM.

**"Can I get a variation of this prompt?"**
→ Yes. Ask for "concise version," "more detailed," "different tone," or "different format." We'll modify the prompt (not reimplement it).

**"What if the generated prompt doesn't work?"**
→ We can refine it. Share what didn't work, and we'll adjust specific sections, not rebuild from scratch.

**"Why so many questions?"**
→ Good prompts need context. 5-7 questions ensure we capture domain specifics, constraints, and success criteria—making the final prompt much more effective.

---

**Ready to generate a world-class prompt? Let's start with a preset name or custom request.**
