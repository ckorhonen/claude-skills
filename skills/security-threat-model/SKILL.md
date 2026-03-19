---
name: "security-threat-model"
description: "Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdown threat model. Trigger only when the user explicitly asks to threat model a codebase or path, enumerate threats/abuse paths, or perform AppSec threat modeling. Do not trigger for general architecture summaries, code review, or non-security design work."
---

# Threat Model Source Code Repo

Deliver an actionable AppSec-grade threat model that is specific to the repository or a project path, not a generic checklist. Anchor every architectural claim to evidence in the repo and keep assumptions explicit. Prioritizing realistic attacker goals and concrete impacts over generic checklists.

## Quick start

1) Collect (or infer) inputs:
- Repo root path and any in-scope paths.
- Intended usage, deployment model, internet exposure, and auth expectations (if known).
- Any existing repository summary or architecture spec.
- Use prompts in `references/prompt-template.md` to generate a repository summary.
- Follow the required output contract in `references/prompt-template.md`. Use it verbatim when possible.

## Workflow

### 1) Scope and extract the system model
- Identify primary components, data stores, and external integrations from the repo summary.
- Identify how the system runs (server, CLI, library, worker) and its entrypoints.
- Separate runtime behavior from CI/build/dev tooling and from tests/examples.
- Map the in-scope locations to those components and exclude out-of-scope items explicitly.
- Do not claim components, flows, or controls without evidence.

### 2) Derive boundaries, assets, and entry points
- Enumerate trust boundaries as concrete edges between components, noting protocol, auth, encryption, validation, and rate limiting.
- List assets that drive risk (data, credentials, models, config, compute resources, audit logs).
- Identify entry points (endpoints, upload surfaces, parsers/decoders, job triggers, admin tooling, logging/error sinks).

### 3) Calibrate assets and attacker capabilities
- List the assets that drive risk (credentials, PII, integrity-critical state, availability-critical components, build artifacts).
- Describe realistic attacker capabilities based on exposure and intended usage.
- Explicitly note non-capabilities to avoid inflated severity.


### 4) Enumerate threats as abuse paths
- Prefer attacker goals that map to assets and boundaries (exfiltration, privilege escalation, integrity compromise, denial of service).
- Classify each threat and tie it to impacted assets.
- Keep the number of threats small but high quality.

### 5) Prioritize with explicit likelihood and impact reasoning
- Use qualitative likelihood and impact (low/medium/high) with short justifications.
- Set overall priority (critical/high/medium/low) using likelihood x impact, adjusted for existing controls.
- State which assumptions most influence the ranking.

### 6) Validate service context and assumptions with the user
- Summarize key assumptions that materially affect threat ranking or scope, then ask the user to confirm or correct them.
- Ask 1–3 targeted questions to resolve missing context (service owner and environment, scale/users, deployment model, authn/authz, internet exposure, data sensitivity, multi-tenancy).
- Pause and wait for user feedback before producing the final report.
- If the user declines or can’t answer, state which assumptions remain and how they influence priority.

### 7) Recommend mitigations and focus paths
- Distinguish existing mitigations (with evidence) from recommended mitigations.
- Tie mitigations to concrete locations (component, boundary, or entry point) and control types (authZ checks, input validation, schema enforcement, sandboxing, rate limits, secrets isolation, audit logging).
- Prefer specific implementation hints over generic advice (e.g., "enforce schema at gateway for upload payloads" vs "validate inputs").
- Base recommendations on validated user context; if assumptions remain unresolved, mark recommendations as conditional.

### 8) Run a quality check before finalizing
- Confirm all discovered entrypoints are covered.
- Confirm each trust boundary is represented in threats.
- Confirm runtime vs CI/dev separation.
- Confirm user clarifications (or explicit non-responses) are reflected.
- Confirm assumptions and open questions are explicit.
- Confirm that the format of the report matches closely the required output format defined in prompt template: `references/prompt-template.md`
- Write the final Markdown to a file named `<repo-or-dir-name>-threat-model.md` (use the basename of the repo root, or the in-scope directory if you were asked to model a subpath).


## Common Pitfalls

These are the most frequent failure modes encountered when threat modeling. Avoiding them makes threat models actionable and credible.

### 1. Threat Model Too Abstract (No Concrete Attack Vectors)
**Problem:** Threat descriptions read like generic security checklist items rather than specific abuse paths anchored to actual code, configurations, or deployment architecture.

**Example of bad:** "Attacker gains unauthorized access to sensitive data"  
**Example of good:** "An attacker without authentication can exfiltrate API keys from `config.json` if the process is deployed with filesystem permissions allowing world-read access, enabling privilege escalation to AWS"

**How to avoid:** For every threat, ask: *Which component? Which entry point? What specific code path or boundary does the attacker exploit?* If you can't answer, go back to the repo and find the concrete evidence (code, config template, deployment docs).

### 2. Missing Threat Actors and Motivations (Generic Adversaries)
**Problem:** Threat model lists threats without defining who the attacker is, what they want, and what resources they have. This makes prioritization meaningless because you can't assess likelihood.

**Example of bad:** "Attacker compromises the system"  
**Example of good:** "A disgruntled employee with internal API access steals PII to sell on a darknet market. Likelihood: medium (few employees have access; audit logs exist but aren't monitored in real-time)"

**How to avoid:** Define 2-3 realistic attacker profiles for your system:
- External unauthenticated attacker
- Authenticated user (internal, customer, or partner)
- Malicious insider with specific privilege level
- Supply chain actor (dependency or infrastructure provider)

For each threat, state which actor(s) can exploit it and why they would.

### 3. No Prioritization (Everything Is "Critical")
**Problem:** Every threat gets marked critical because the impact is theoretically severe. This makes the threat model unhelpful—teams can't focus because nothing is prioritized, and credibility erodes ("threat models are just scare tactics").

**Example of bad:** All 25 threats marked "Critical"  
**Example of good:** "Supply chain RCE via dependency: **Critical** (high likelihood pre-exploit patch, catastrophic impact). User brute-force of weak password: **Medium** (low likelihood with rate limiting and 2FA, but integrity impact is high if successful)."

**How to avoid:** Use the likelihood × impact grid. Adjust final priority based on existing controls. Ask:
- How hard is this to exploit? (code depth, required preconditions, attacker resources)
- How likely is an attacker to try? (is this an obvious vector? does it require persistence/insider knowledge?)
- Is there already a control that mitigates this? (rate limiting, encryption, audit logging)

Mark as "Conditional High" if priority depends on user assumptions you haven't confirmed yet.

### 4. Mitigations Without Implementation Details (Vague Recommendations)
**Problem:** Recommendations read like security platitudes ("add authentication," "encrypt data," "enable logging") rather than specific code locations or control mechanisms. Teams don't know where to start.

**Example of bad:** "Add input validation to prevent injection attacks"  
**Example of good:** "Enforce JSON schema validation on the `/api/upload` endpoint handler (src/handlers/upload.ts:42) before passing to the document parser. Use Zod or Ajv to reject payloads with > 10MB or disallowed MIME types."

**How to avoid:** For every mitigation:
1. Name the component or code location (file, function, boundary)
2. Specify the control type: schema enforcement, rate limiting, sandboxing, secrets rotation, audit logging, signature verification, etc.
3. Tie it to the threat you're mitigating
4. If you can't find a concrete location, ask the user to clarify the architecture

### 5. Missing Threat Model Maintenance Plan (One-Time Exercise)
**Problem:** Threat model is delivered as a snapshot but the system evolves. New entry points are added, dependencies are upgraded, team changes. The model stales within weeks and loses credibility.

**Example of bad:** "Here's your threat model, good luck!"  
**Example of good:** "Threat model is versioned in Git. Review schedule: after each major deployment, quarterly team review, and whenever a new dependency or integration is added. Update-trigger checklist: new user roles, new APIs, new data sources, infrastructure changes."

**How to avoid:** Before finalizing, agree on:
- **Version control:** Is the threat model in Git? Linked to architecture changes?
- **Review cadence:** Quarterly? Per-release? Incident-driven?
- **Update triggers:** What code/deployment changes require updating the threat model?
- **Ownership:** Who owns the threat model? Who updates it?

Mention this in the deliverable.

### 6. STRIDE/PASTA-Specific Failure Modes

#### STRIDE (if using as methodology)
- **Spoofing:** Threat model lists "attacker spoofs identity" but doesn't specify which auth mechanism is bypassable or how (weak cryptography, bad token validation, replay attack)
- **Tampering:** Identifies data in transit but omits the specific boundary and transport (does the API use TLS? Is there message signing for offline data?)
- **Repudiation:** Overestimates likelihood if audit logging is present; doesn't account for log retention and monitoring coverage
- **Information Disclosure:** Confuses "data at rest is not encrypted" (common) with "attacker will exfiltrate it" (depends on access control and network exposure)
- **Denial of Service:** Treats all DoS equally; in-process crashes are different from external rate limit exhaustion—separate by component
- **Elevation of Privilege:** Often misses the initial foothold; ask "how does the attacker get to this component in the first place?"

#### PASTA (if using as methodology)
- **Asset enumeration:** Lists technical assets but misses logical assets (data pipelines, reputation, availability). Ask "what does the business value most here?"
- **Threat analysis:** Often becomes a literature review of CVEs rather than application-specific abuse paths. Stay focused on *this system*.
- **Vulnerability analysis:** Conflates "code has a SQL injection pattern" with "attacker can reach it"—ask which entry points actually expose it
- **Risk analysis:** Uses templates for severity ratings without analyzing *likelihood in this context*. An RCE on an internal admin tool is lower risk than the same RCE on an internet-facing API

---

## Risk prioritization guidance (illustrative, not exhaustive)
- High: pre-auth RCE, auth bypass, cross-tenant access, sensitive data exfiltration, key or token theft, model or config integrity compromise, sandbox escape.
- Medium: targeted DoS of critical components, partial data exposure, rate-limit bypass with measurable impact, log/metrics poisoning that affects detection.
- Low: low-sensitivity info leaks, noisy DoS with easy mitigation, issues requiring unlikely preconditions.

## References

- Output contract and full prompt template: `references/prompt-template.md`
- Optional controls/asset list: `references/security-controls-and-assets.md`

Only load the reference files you need. Keep the final result concise, grounded, and reviewable.
