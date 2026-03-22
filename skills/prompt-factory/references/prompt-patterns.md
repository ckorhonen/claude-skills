# Prompt Patterns & Best Practices Library

Contextual best practices from OpenAI, Anthropic, and Google for prompt engineering.

---

## By Output Type

### Code Generation Prompts

**OpenAI Best Practices:**
- Break down complex tasks into smaller steps with clear naming
- Include code examples showing desired patterns
- Specify error handling requirements upfront
- Define testing requirements and coverage targets

**Anthropic Best Practices:**
- Provide clear code structure expectations (separation of concerns)
- Include detailed comments explaining non-obvious decisions
- Specify edge cases and how to handle them
- Define logging and debugging requirements

**Google Best Practices:**
- Emphasize modular design and reusability
- Include performance considerations and optimization targets
- Specify security best practices relevant to the tech stack
- Define accessibility and internationalization requirements

**Domain-Specific:**
- **Backend:** Database indexing, connection pooling, async patterns, rate limiting
- **Frontend:** Component composition, state management, accessibility (WCAG), responsive design
- **DevOps:** Infrastructure as Code, monitoring, alerting, disaster recovery
- **ML:** Training/validation/test split, hyperparameter tuning, model evaluation metrics

---

### Documentation Prompts

**OpenAI Best Practices:**
- Use clear, progressive disclosure structure (overview → details → examples)
- Provide practical examples before abstract concepts
- Include troubleshooting sections for common issues
- Use consistent formatting and terminology throughout

**Anthropic Best Practices:**
- Create logical, hierarchical structure matching user mental models
- Include "why" explanations, not just "how"
- Provide context about when to use different approaches
- Flag limitations and edge cases clearly

**Google Best Practices:**
- Use visual elements (diagrams, tables, code snippets)
- Organize by user journey (getting started → advanced)
- Include real-world examples and use cases
- Provide quick reference guides alongside detailed explanations

**Domain-Specific:**
- **API Docs:** Clear endpoint descriptions, parameter definitions, response examples, error codes
- **Technical Guides:** Architecture diagrams, step-by-step tutorials, configuration examples
- **User Docs:** Task-based organization, screenshots, common questions, keyboard shortcuts
- **Release Notes:** What changed, why, migration path, known issues

---

### Strategy & Planning Prompts

**OpenAI Best Practices:**
- Start with clear problem statement and desired outcome
- Break strategy into measurable, time-bound goals
- Identify stakeholders and their success criteria
- Include contingency plans for key risks

**Anthropic Best Practices:**
- Define assumptions explicitly and validate them
- Provide decision frameworks for trade-offs
- Include success metrics and how to measure them
- Document rationale for strategic choices

**Google Best Practices:**
- Use data-driven approaches (metrics, benchmarks, research)
- Consider multiple scenarios and business models
- Include competitive analysis and market context
- Define OKRs (Objectives and Key Results) clearly

**Domain-Specific:**
- **Product Strategy:** Market analysis, user personas, feature prioritization, roadmap
- **Marketing Strategy:** Customer journey mapping, channel strategy, messaging pillars, metrics
- **Business Strategy:** Revenue model, unit economics, competitive positioning, growth drivers
- **Tech Strategy:** Architecture decisions, technology choices, debt management, roadmap

---

### Analysis & Insights Prompts

**OpenAI Best Practices:**
- Provide context about data source and methodology
- Include confidence levels or uncertainty ranges
- Support conclusions with specific evidence
- Provide actionable recommendations based on findings

**Anthropic Best Practices:**
- Show your working and reasoning process
- Highlight limitations of the analysis
- Consider alternative explanations
- Suggest follow-up questions or deeper analysis

**Google Best Practices:**
- Visualize data clearly (charts, tables, trends)
- Segment insights by importance and impact
- Include competitive/comparative benchmarks
- Provide forecasting or predictive analysis when relevant

**Domain-Specific:**
- **Financial Analysis:** Cash flow, profitability, ratios, valuation, risk assessment
- **Customer Analysis:** Segmentation, cohort analysis, churn drivers, LTV/CAC
- **Market Analysis:** Market sizing, growth rates, trends, competitive landscape
- **Technical Analysis:** Performance metrics, bottlenecks, scalability, reliability

---

### Design Prompts

**OpenAI Best Practices:**
- Include user research and user personas
- Define accessibility requirements (WCAG levels)
- Specify responsive design breakpoints
- Include design pattern examples

**Anthropic Best Practices:**
- Define design principles and philosophy
- Include constraint clarity (budget, timeline, technical limitations)
- Provide clear success criteria and design goals
- Reference existing design systems or brand guidelines

**Google Best Practices:**
- Use design thinking methodology (empathize → define → ideate → prototype → test)
- Include user testing and iteration guidelines
- Specify design tokens (colors, typography, spacing)
- Consider accessibility from the start (WCAG 2.1 AA minimum)

**Domain-Specific:**
- **UI/UX Design:** Wireframes, user flows, accessibility, responsive design, interaction patterns
- **Product Design:** User research, personas, jobs-to-be-done, iterative testing
- **Brand Design:** Design systems, color palettes, typography, brand guidelines, visual language
- **System Design:** Component library, design tokens, documentation, versioning

---

## By Domain

### Technical Domains

#### Backend Engineering
- Define API contract (OpenAPI 3.0 spec)
- Specify database schema and constraints
- Include authentication/authorization approach
- Define error handling and logging strategy
- Specify performance targets (latency, throughput)
- Include monitoring and alerting approach

#### Frontend Engineering
- Specify component architecture (composition, state management)
- Define accessibility requirements (WCAG 2.1)
- Include responsive design breakpoints
- Specify performance targets (Core Web Vitals)
- Define testing strategy (unit, integration, E2E)
- Include build and deployment process

#### DevOps / Infrastructure
- Define infrastructure as code approach (Terraform, CloudFormation)
- Include monitoring, logging, and alerting strategy
- Specify disaster recovery and backup procedures
- Define security controls and compliance requirements
- Include CI/CD pipeline configuration
- Specify scaling and performance requirements

#### Security
- Define threat model and attack vectors
- Specify security controls (preventative, detective, corrective)
- Include compliance requirements (SOC 2, ISO 27001, HIPAA)
- Define incident response procedures
- Include penetration testing approach
- Specify secure coding practices

#### Data Science / ML
- Define problem statement and success metrics
- Specify data source and quality requirements
- Include feature engineering approach
- Define model selection and evaluation strategy
- Specify hyperparameter tuning approach
- Include A/B testing or validation methodology

### Business Domains

#### Product Management
- Define problem statement and user research findings
- Include competitive analysis
- Specify success metrics and KPIs
- Define prioritization framework
- Include roadmap and timeline
- Specify stakeholder communication plan

#### Marketing
- Define target audience and personas
- Specify messaging framework and key messages
- Include channel strategy (owned, earned, paid)
- Define content pillars and themes
- Specify campaign timeline and metrics
- Include budget allocation approach

#### Sales
- Define buyer personas and buying journey
- Specify qualification criteria and sales process
- Include competitive positioning
- Define pricing strategy
- Specify sales enablement approach
- Include pipeline management approach

#### Finance
- Define financial model (revenue, costs, margins)
- Specify key metrics and dashboards
- Include forecasting methodology
- Define budget allocation approach
- Specify reporting cadence
- Include risk and scenario analysis

### Creative Domains

#### Content Strategy
- Define content pillars and themes
- Specify target audience and personas
- Include SEO strategy (keywords, topics)
- Define content calendar and publishing cadence
- Specify distribution channels
- Include engagement and conversion metrics

#### Brand Strategy
- Define brand positioning and values
- Specify tone of voice and messaging
- Include visual identity and design system
- Define brand guidelines
- Specify audience and communication channels
- Include competitive differentiation

#### Copywriting
- Define target audience and their pain points
- Specify tone of voice and brand voice
- Include key messages and value propositions
- Define CTA (call-to-action) approach
- Specify format and length requirements
- Include examples of desired style

---

## Prompt Pattern Templates

### Pattern 1: The "What/Why/How" Structure

**Use for:** Explaining concepts, strategies, or decisions

```
WHAT: [Define the thing]

WHY: [Why it matters / what problem it solves]

HOW: [Step-by-step approach / implementation]

WHEN: [When to use this / applicable contexts]

EXAMPLES: [Concrete examples demonstrating the concept]
```

### Pattern 2: The "Role + Workflow" Structure

**Use for:** Defining a role's responsibilities and workflow

```
ROLE: [Title and expertise level]

MISSION: [Primary objective]

WORKFLOW:
1. [Phase 1 with concrete steps]
2. [Phase 2 with concrete steps]
3. [Phase 3 with concrete steps]

SUCCESS CRITERIA: [How to measure success]

CONSTRAINTS: [Important limitations or rules]

EXAMPLES: [Examples of typical outputs]
```

### Pattern 3: The "Problem → Solution → Validation" Structure

**Use for:** Solving specific problems or making decisions

```
PROBLEM: [What's the issue?]

CONSTRAINTS: [Limitations affecting the solution]

SOLUTION APPROACH: [How to solve it]
- Step 1: [Action]
- Step 2: [Action]
- Step 3: [Action]

VALIDATION: [How to verify the solution works]

ALTERNATIVES: [Other approaches and trade-offs]
```

### Pattern 4: The "Requirements → Design → Implementation" Structure

**Use for:** Building or creating something

```
REQUIREMENTS: [What needs to be built]

CONSTRAINTS: [Technical, resource, timeline constraints]

DESIGN: [How to design it]
- Architecture: [System design]
- Components: [Key components]
- Interfaces: [How components interact]

IMPLEMENTATION: [How to build it]
- Phase 1: [Build X]
- Phase 2: [Build Y]
- Phase 3: [Build Z]

TESTING: [How to validate it works]

SUCCESS CRITERIA: [Definition of success]
```

### Pattern 5: The "Best Practices + Context" Structure

**Use for:** Establishing guidelines or standards

```
BEST PRACTICE: [The practice/standard]

WHY IT MATTERS: [Why follow this]

APPLICATION: [How to apply it in your context]
- For X: [Specific application]
- For Y: [Specific application]
- For Z: [Specific application]

PITFALLS TO AVOID: [Common mistakes]

EXAMPLES: [Good and bad examples]
```

---

## Quality Indicators (Check Before Delivery)

### Clarity Checklist
- [ ] Role and mission are crystal clear?
- [ ] Workflow steps are concrete and actionable?
- [ ] No ambiguous language or jargon without definition?
- [ ] Examples demonstrate expected behavior?
- [ ] Success criteria are measurable?

### Completeness Checklist
- [ ] All necessary context provided?
- [ ] All questions from user incorporated?
- [ ] Constraints and edge cases addressed?
- [ ] Best practices contextually applied?
- [ ] Both what to do AND why?

### Usability Checklist
- [ ] Can be understood by intended audience?
- [ ] Provides enough detail to execute?
- [ ] Not overly prescriptive (allows adaptation)?
- [ ] Well-organized and easy to navigate?
- [ ] Includes examples for key concepts?

---

## Common Patterns by Role

### Manager Prompts Should Include:
- Team structure and roles
- Decision-making authority and escalation paths
- Communication cadence and methods
- Success metrics for their area
- Stakeholder management approach
- Conflict resolution framework

### Engineer Prompts Should Include:
- Technical architecture and constraints
- Code quality standards
- Testing requirements and coverage
- Performance targets
- Deployment and monitoring process
- On-call and incident response procedures

### Analyst Prompts Should Include:
- Data sources and their definitions
- Methodology and assumptions
- Validation approach
- Visualization and presentation style
- Key metrics and how to calculate them
- Insight prioritization framework

### Designer Prompts Should Include:
- Design principles and philosophy
- Accessibility requirements
- Responsive design approach
- Component system / design tokens
- User research and personas
- Iteration and feedback process

### Strategist Prompts Should Include:
- Problem statement and context
- Stakeholders and their goals
- Constraints and trade-offs
- Decision-making framework
- Timeline and milestones
- Success metrics and measurement

---

## Token Optimization Tips

### Reduce Without Losing Quality
- Consolidate examples (show 2-3 instead of 5)
- Use bullet points instead of prose where possible
- Remove redundant explanations
- Condense repetitive sections
- Keep critical context, trim supporting details

### Check Token Count by Section
- Role/mission: 100-200 tokens
- Context: 200-300 tokens
- Workflow: 400-600 tokens
- Best practices: 300-500 tokens
- Examples: 300-500 tokens
- **Total core target: 3,500-4,500 tokens**

### When Exceeding Limits
1. Identify verbose sections
2. Condense without losing meaning
3. Move optional details to variations
4. Consolidate examples
5. Trim redundant context
6. Re-count and verify optimal range

---

## Prompt Iteration Process

### Testing Your Prompt

1. **Simple Request** — Does the LLM understand the role correctly?
2. **Typical Request** — Does it follow the workflow and best practices?
3. **Edge Case** — How does it handle ambiguity or complex scenarios?
4. **Boundary Condition** — What happens at constraints?

### Refinement Cycle

1. **Identify gap** — What didn't work as expected?
2. **Analyze root cause** — Was it a clarity issue or incomplete instructions?
3. **Refine section** — Update specific part (not whole rewrite)
4. **Re-test** — Verify fix works for original scenario
5. **Check for regressions** — Ensure other scenarios still work

### When to Major Revision vs. Minor Tweak

**Major Revision (rewrite):**
- Fundamental misunderstanding of role
- Workflow doesn't make sense
- Missing critical context

**Minor Tweak (edit):**
- Clarify ambiguous phrasing
- Add missing example
- Adjust tone or depth
- Fix specific instruction

---

## Reference Matrix: What to Include by Role Type

| Aspect | Technical | Business | Creative | Specialized |
|--------|-----------|----------|----------|-------------|
| Tech Stack | ✓ REQUIRED | Optional | Optional | ✓ REQUIRED |
| Success Metrics | ✓ Essential | ✓ Essential | ✓ Important | ✓ Essential |
| Examples | ✓ Code/API | ✓ Business models | ✓ Content samples | ✓ Domain-specific |
| Constraints | ✓ Important | ✓ Important | ✓ Budget/timeline | ✓ Compliance |
| Best Practices | OpenAI/Anthropic | Industry standards | Brand/creative | Domain-specific |
| Workflow Phases | 3-4 detailed | 3-4 strategic | 3-4 creative | Role-dependent |

---

**Use this library to ensure contextually appropriate, high-quality mega-prompts.**
