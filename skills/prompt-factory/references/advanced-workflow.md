# Advanced Workflow: Custom Prompt Generation (8 Steps)

Detailed step-by-step process for generating custom prompts. Use this for Path 2 (custom prompts).

---

## Step 1: Intent Detection & Context Inference

Analyze user's request for trigger keywords and infer context.

### Role Triggers
- **Technical:** "engineer", "developer", "architect", "DevOps", "backend", "frontend", "full-stack", "ML", "data scientist"
- **Business:** "manager", "strategist", "analyst", "consultant", "executive", "director", "VP"
- **Creative:** "designer", "writer", "content", "UX", "brand", "marketing"
- **Specialized:** "healthcare", "fintech", "legal", "education", "security"

### Task Triggers
- **Build:** "create", "build", "develop", "implement", "code", "write"
- **Analyze:** "analyze", "review", "evaluate", "assess", "audit", "research"
- **Optimize:** "optimize", "improve", "refactor", "enhance", "fix"
- **Plan:** "strategy", "plan", "roadmap", "architecture", "design"

### Output Triggers
- "code", "documentation", "strategy", "analysis", "plan", "design", "report"

### Quick Inference Checklist
- [ ] Primary role identified?
- [ ] Domain/industry inferred?
- [ ] Task complexity assessed (basic/intermediate/advanced/expert)?
- [ ] Output type detected?
- [ ] Technical depth estimated?

---

## Step 2: Smart 7-Question Flow (MANDATORY)

**Critical Rule:** ALWAYS ask at least 5 questions before generating. Even if context seems clear, validation is essential.

### Questioning Rules
- **MINIMUM 5 questions** (even if context obvious)
- **MAXIMUM 7 questions** (skip only truly redundant ones)
- **Ask for confirmation** of inferred details
- **Purpose:** Validate assumptions, gather specifics, ensure quality

### When to Skip a Question
✅ ONLY if user explicitly provided that exact detail in their request
- Example: User says "React 18 with TypeScript" → skip tech stack question
- Still ask for domain, constraints, success criteria (always validate)

### Questions NEVER to Skip
- ✅ ALWAYS ask about domain/industry context (gets specifics)
- ✅ ALWAYS ask about constraints (budget, timeline, team size)
- ✅ ALWAYS ask about success criteria (measurable outcomes)
- ✅ Ask for confirmation: "I'm inferring [X], is that correct?"

### Smart Adaptation by Domain

**If technical/coding detected:**
- MUST ask: tech stack, constraints, success criteria
- SKIP: Anything about brand voice or audience personas

**If business detected:**
- MUST ask: KPIs, stakeholders, metrics, timeline
- SKIP: Technical implementation details

**If creative detected:**
- MUST ask: brand voice, audience, distribution, tone
- SKIP: Database schema or infrastructure questions

**If industry-specific:**
- MUST ask: compliance, regulations, standards
- SKIP: Generic best practices (assume they know them)

---

## Step 3: Question Bank (Select 5-7)

Adapt questions based on domain and skip truly redundant ones. Always ask for confirmation of inferred details.

### Category 1: Role & Domain (Ask 1-2)

**Q1: What role should the AI assume?**

*Examples:*
- "Senior Backend Engineer"
- "Product Manager"
- "Marketing Growth Strategist"
- "Data Analyst"
- "UX Designer"
- "Security Engineer"
- "Content Strategist"

> Your answer: `___`

**Q2: What domain or industry context?**

*Examples:*
- "FinTech / Payment Processing"
- "Healthcare SaaS"
- "E-commerce Platform"
- "B2B Marketing Agency"
- "Mobile Gaming"
- "Enterprise Software"
- "Regulated Manufacturing"

> Your answer: `___`

### Category 2: Use Case & Output (Ask 2)

**Q3: What is the primary task or goal?**

*Examples (Technical):*
- "Build REST APIs for payment processing"
- "Analyze performance bottlenecks in high-scale systems"
- "Design cloud infrastructure for global audience"

*Examples (Business):*
- "Create product strategy for new market"
- "Develop go-to-market plan for product launch"
- "Analyze competitive landscape"

*Examples (Creative):*
- "Develop content marketing strategy for B2B SaaS"
- "Create brand guidelines and visual identity"
- "Write thought leadership articles"

> Your answer: `___`

**Q4: What output format do you need?**

*Options:*
- `code` - Implementation code with tests and docs
- `documentation` - Technical/user docs or guides
- `strategy` - Strategic plans/roadmaps/frameworks
- `analysis` - Data analysis/insights/reports
- `design` - UI/UX designs or brand materials
- `plan` - Project/implementation plans

> Your answer: `___`

### Category 3: Context & Constraints (Ask 1-2)

**Q5: Tech stack, tools, or methodologies to use/follow?**

*Examples (Technical):*
- "Python, FastAPI, PostgreSQL, AWS"
- "React, TypeScript, Next.js, Node.js"
- "Kubernetes, Terraform, monitoring stack"

*Examples (Business):*
- "Agile/Scrum methodology"
- "Data-driven approach (metrics-first)"
- "OKR framework"

*Examples (Creative):*
- "SEO best practices, Google Analytics"
- "Figma, Design Systems, WCAG 2.1"
- "Brand guidelines (company colors, tone)"

> Your answer: `___`

**Q6: Any critical constraints or requirements?**

*Examples (Technical):*
- "HIPAA compliant, healthcare regulations"
- "Must support 10k+ concurrent users"
- "PCI-DSS compliance for payments"

*Examples (Business):*
- "Budget < $10k, 2-week timeline"
- "Stakeholder alignment from sales + product"
- "Measurable ROI required"

*Examples (Creative):*
- "Mobile-first, accessibility AA"
- "Target audience: CTOs in enterprise"
- "3-month content calendar"

> Your answer: `___`

### Category 4: Style & Success (Ask 1-2)

**Q7a: Communication style and response format?**

*Options:*
- **Tone:** Professional / Technical / Casual / Academic / Inspirational
- **Style:** Concise / Detailed / Step-by-step / Conceptual / Example-heavy
- **Format:** Prose / Bullets / Mixed / Code-heavy
- **Depth:** High-level overview / Moderate detail / Deep-technical / Implementation-ready

*Example answer:* "Technical tone, detailed style, mixed format, implementation-ready depth"

> Your answer: `___`

**Q7b: Core or Advanced mode?**

*Options:*
- **Core** (default) - Prompt + usage instructions + 2-3 examples (~4-6K tokens)
- **Advanced** - Core + testing scenarios + variations + optimization tips (~10K tokens)

> Your choice: `___` (press enter for Core)

---

## Step 4: Output Format Selection

Ask user to choose format if not obvious from context:

**Select output format:**
1. `xml` - XML-structured markdown (optimal for LLM parsing) [DEFAULT]
2. `claude` - Claude-optimized system prompt format
3. `chatgpt` - ChatGPT custom instructions format
4. `gemini` - Google Gemini format
5. `all` - Generate all 4 formats

> Your choice: `___` (or press enter for default XML)

---

## Step 5: Template Matching & Synthesis

### Check Quick-Start Presets
- Read `references/presets.md` for matching templates
- Match criteria:
  - Role match: >80% (same or very similar role)
  - Domain match: >70% (same or adjacent industry)
  - Output type: exact match preferred

### Decision Logic

**High Match (>85%):**
- Use preset template directly
- Customize variables from user answers
- Example: User needs "Product Manager prompt for SaaS" → Use PM preset, customize for specific domain

**Moderate Match (60-85%):**
- Use preset as base
- Significant modifications needed
- Example: User needs "Product Manager for hardware company" → Start with PM preset, add hardware-specific considerations

**Low Match (<60%):**
- Synthesize custom template using:
  - `references/prompt-patterns.md` (best practices, patterns)
  - User's specific answers from questions
  - Contextual best practices for role/domain/task
- Example: User needs unique role not in presets → Build custom from scratch

### Synthesis Approach (when low match)

1. **Pull relevant best practices** from `references/prompt-patterns.md`
2. **Incorporate user-specific context** from their answers
3. **Structure using XML template** from `references/examples.md`
4. **Fill sections:** role, mission, context, workflow, output specs, best practices
5. **Validate completeness** before proceeding

---

## Step 6: Quality Validation (7-Point Gates)

**Before delivery, validate all 7 gates:**

### Gate 1: XML Structure
- [ ] All tags properly opened and closed (if XML format)
- [ ] No malformed elements
- [ ] Proper nesting

### Gate 2: Completeness
- [ ] All user questionnaire responses incorporated
- [ ] All context questions addressed
- [ ] No information gaps

### Gate 3: Token Count
Verify within optimal ranges:
- **Core mode:** 3,000-6,000 tokens (ideal ~4,500)
- **Advanced mode:** 8,000-12,000 tokens (ideal ~10,000)
- **Warning if:**
  - Core > 8K tokens
  - Advanced > 15K tokens
- **Action:** If over, trim or consolidate sections; never deliver bloated prompts

### Gate 4: No Placeholders
- [ ] All `[...]` or `{...}` filled with actual content
- [ ] No "TBD" or "TODO" remaining
- [ ] No generic examples

### Gate 5: Actionable Workflow
- [ ] Clear, numbered steps
- [ ] Executable (not abstract)
- [ ] Each phase has concrete deliverables

### Gate 6: Best Practices Applied
- [ ] Contextually relevant practices included
- [ ] Practices match role/domain/task
- [ ] OpenAI/Anthropic/Google practices applicable

### Gate 7: Examples Present
- [ ] At least 2 examples provided
- [ ] Examples demonstrate expected behavior
- [ ] Examples match role and output type

### If Validation Fails
- [ ] Identify which gates failed
- [ ] Fix issues before delivery
- [ ] Re-validate before announcing

---

## Step 7: Generate Mega-Prompt

Choose based on user's selected format and mode (from Steps 3-4).

### Template: XML Core Mode

```xml
<mega_prompt>

<role>
[Role title with expertise and domain specialization]
</role>

<mission>
[Primary objective and success criteria]
</mission>

<context>
  <domain>[Industry/field context from Q2]</domain>
  <expertise>[Specialized knowledge areas]</expertise>
  <tech_stack>[Technologies from Q5 if applicable]</tech_stack>
  <constraints>[Limitations and requirements from Q6]</constraints>
  <avoidance_rules>[What NOT to do]</avoidance_rules>
</context>

<workflow>
  <phase_1>[Phase name] - [Steps]</phase_1>
  <phase_2>[Phase name] - [Steps]</phase_2>
  <phase_3>[Phase name] - [Steps]</phase_3>
  <phase_4>[Phase name] - [Steps]</phase_4>
</workflow>

<output_specifications>
  <format>[From Q4]</format>
  <structure>[How to organize output]</structure>
  <depth_level>[From Q7a]</depth_level>
  <quality_criteria>[Success metrics]</quality_criteria>
</output_specifications>

<communication_guidelines>
  <tone>[From Q7a]</tone>
  <audience>[Target reader level]</audience>
  <formatting>[From Q7a]</formatting>
  <examples_usage>[When/how to use examples]</examples_usage>
</communication_guidelines>

<best_practices>
[Contextually selected from references/prompt-patterns.md]

[From OpenAI:]
- [Relevant practice 1]
- [Relevant practice 2]

[From Anthropic:]
- [Relevant practice 1]
- [Relevant practice 2]

[From Google:]
- [Relevant practice 1]
- [Relevant practice 2]

[Domain-Specific:]
- [Specific practice for role/domain/task]
</best_practices>

<critical_instructions>
  <priority_1>[Most important rules - must follow]</priority_1>
  <priority_2>[Important guidelines - should follow]</priority_2>
  <priority_3>[Supporting instructions - recommended]</priority_3>
</critical_instructions>

<examples>
## Example 1: [Scenario Name]
**User Request:** [Typical request for this role]

**Expected Response Structure:**
[Show how to structure the response]

## Example 2: [Scenario Name]
**User Request:** [Another typical request]

**Expected Response Structure:**
[Show the response pattern]
</examples>

<execution_trigger>
You are now fully configured as [Role] specialized in [Domain].

When the user provides a request:
1. [First step in workflow]
2. [Second step]
3. [Third step]
4. [Apply best practices]
5. [Deliver output meeting quality criteria]

Begin assisting the user now with this configuration.
</execution_trigger>

</mega_prompt>
```

### Template: XML Advanced Mode

Add after `<examples>` section:

```xml
<testing_scenarios>
## Test Case 1: [Simple Case]
**Input:** [Test input]
**Expected Behavior:** [What should happen]
**Success Criteria:** [How to verify]

## Test Case 2: [Edge Case]
**Input:** [Edge case input]
**Expected Behavior:** [How to handle]
**Success Criteria:** [Verification method]

## Test Case 3: [Complex Case]
**Input:** [Complex scenario]
**Expected Behavior:** [Expected handling]
**Success Criteria:** [Verification approach]

## Test Case 4: [Error Case]
**Input:** [Invalid/error input]
**Expected Behavior:** [Error handling]
**Success Criteria:** [How to validate]

## Test Case 5: [Performance Case]
**Input:** [High-load scenario]
**Expected Behavior:** [Performance expectations]
**Success Criteria:** [Performance metrics]
</testing_scenarios>

<prompt_variations>
## Variation 1: Concise (~3K tokens)
[Minimal version focusing on essential instructions]

## Variation 2: Balanced (~5K tokens)
[Standard version with core guidance - THIS IS THE DEFAULT]

## Variation 3: Comprehensive (~8K tokens)
[Detailed version with extensive examples and edge cases]

**Recommendation:** Start with Variation 2 (Balanced).
- Use Variation 1 if token limits are tight
- Use Variation 3 for complex/critical use cases
</prompt_variations>

<optimization_tips>
## Token Optimization
- Current token count: [estimated count]
- Optimization opportunities:
  1. [Opportunity 1]
  2. [Opportunity 2]
  3. [Opportunity 3]

## Clarity Improvements
- Potential ambiguities:
  1. [Ambiguity] → [Clarification suggestion]
  2. [Ambiguity] → [Clarification suggestion]

## Effectiveness Enhancements
- Consider adding:
  1. [Enhancement 1]
  2. [Enhancement 2]

## Iteration Guidelines
After testing this prompt:
1. Track which responses meet expectations
2. Note any consistent issues or gaps
3. Refine specific sections (not wholesale rewrites)
4. Test refined version with same scenarios
5. Save successful versions for reuse
</optimization_tips>
```

---

## Step 8: Delivery Message

Present generated prompt with clear context and usage instructions.

### Delivery Template

```markdown
✅ **Your [Core/Advanced] mega-prompt is ready!**

**Configuration:**
- **Role:** [Role name]
- **Domain:** [Domain/industry]
- **Output Type:** [Type]
- **Format:** [xml/claude/chatgpt/gemini]
- **Mode:** [core/advanced]
- **Template:** [Preset name or "Custom"]

**Quality Validation:** ✓ All 7 gates passed
**Token Count:** ~[X,XXX] tokens ([range])

---

**Generated Prompt:**

[INSERT COMPLETE GENERATED PROMPT HERE]

---

**Usage Instructions:**

[SELECT FORMAT-SPECIFIC INSTRUCTIONS]

**For XML format:**
1. Copy the entire `<mega_prompt>` block above
2. Paste into your LLM conversation (Claude, ChatGPT, Gemini, etc.)
3. Follow with your specific request
4. The AI will respond according to the defined role

**For Claude format:**
1. Copy the system configuration above
2. Use as your system prompt in Claude
3. Start your conversation
4. Claude will follow the configured behavior

**For ChatGPT format:**
1. Go to Settings → Personalization → Custom Instructions
2. Paste into the first box (What would you like...)
3. Paste into the second box (How would you like...)
4. Save and start using

**For Gemini format:**
1. Copy the role configuration
2. Paste at start of new Gemini conversation
3. Continue with your requests
4. Gemini will maintain the configured role

---

⚠️ **IMPORTANT - Prompt Generation Complete**

This skill has generated a PROMPT for you to use. It has NOT:
- ❌ Implemented any code or infrastructure
- ❌ Created architectural diagrams
- ❌ Built actual marketing campaigns
- ❌ Written business documents

**Next Steps:**
1. Copy the prompt above
2. Use it in a FRESH conversation or different tool
3. That conversation will then implement the actual work

---

[IF ADVANCED MODE:]

**📊 Testing Scenarios Included:**
- 5 test cases to validate prompt behavior
- Use these to ensure prompt works as expected before deployment

**🎛️ Prompt Variations:**
- Concise (~3K), Balanced (current, ~5K), Comprehensive (~8K)
- Switch based on token limits or detail needed

**⚡ Optimization Tips:**
- Token count: ~[X]K tokens
- [X] optimization opportunities identified
- Iteration guidelines included above

---

**Need to modify the PROMPT itself?**
- "Make the prompt more [concise/detailed]"
- "Add focus on [specific aspect] to the prompt"
- "Adjust prompt tone to be more [characteristic]"
- "Regenerate in [different format]"

**Want a different prompt?**
- "Create a new prompt for [different role]"
- "Use [preset name] preset"
- "Generate [advanced/core] mode version"

**Can't implement the prompt's instructions?**
→ This skill generates prompts only. To implement the work described in the prompt, paste the generated prompt into a fresh conversation or use a different tool/service.
```

---

## Decision Tree Reference

### When to Ask More Questions

```
User request seems clear?
├─ YES: "I'll need to ask a few questions to refine this..."
│       → Ask 5-7 questions anyway (validation is key)
└─ NO: Ask 5-7 questions to gather specifics
```

### When to Use Preset vs. Custom

```
Request mentions specific preset (e.g., "Product Manager")?
├─ YES: Check match in presets.md
│       ├─ High match (>85%): Use preset template
│       └─ Low match (<60%): Synthesize custom
└─ NO: Synthesize custom from scratch
```

### When to Generate Multiple Formats

```
User asks for specific format?
├─ YES: Generate only that format
└─ NO: Ask first: "XML (default) or would you prefer Claude/ChatGPT/Gemini format?"
       → Generate one format unless user requests "all"
```

---

## Quick Checklist Before Delivery

- [ ] All 5-7 questions asked and answered?
- [ ] Template matched or synthesized?
- [ ] All 7 validation gates passed?
- [ ] Token count announced?
- [ ] Format-specific usage instructions included?
- [ ] No implementation work attempted (prompt only)?
- [ ] Ready to offer variations or modifications?
