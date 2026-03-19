---
name: "security-best-practices"
description: "Perform language and framework specific security best-practice reviews and suggest improvements. Trigger when the user requests: security review, security report, threat assessment, vulnerability scan, security audit, secure-by-default coding, hardening guidance, or security best practices guidance. Trigger only for supported languages (python, javascript/typescript, go). Do not trigger for general code review, debugging, or non-security tasks."
---

# Security Best Practices

## Overview

This skill provides a description of how to identify the language and frameworks used by the current context, and then to load information from this skill's references directory about the security best practices for this language and or frameworks.

This information, if present, can be used to write new secure by default code, or to passively detect major issues within existing code, or (if requested by the user) provide a vulnerability report and suggest fixes.

## Workflow

The initial step for this skill is to identify ALL languages and ALL frameworks which you are being asked to use or already exist in the scope of the project you are working in. Focus on the primary core frameworks. Often you will want to identify both frontend and backend languages and frameworks.

Then check this skill's references directory to see if there are any relevant documentation for the language and or frameworks. Make sure you read ALL reference files which relate to the specific framework or language. The format of the filenames is `<language>-<framework>-<stack>-security.md`. You should also check if there is a `<language>-general-<stack>-security.md` which is agnostic to the framework you may be using.

If working on a web application which includes a frontend and a backend, make sure you have checked for reference documents for BOTH the frontend and backend!

If you are asked to make a web app which will include both a frontend and backend, but the frontend framework is not specified, also check out `javascript-general-web-frontend-security.md`. It is important that you understand how to secure both the frontend and backend.

If no relevant information is available in the skill's references directory, think a little bit about what you know about the language, the framework, and all well known security best practices for it. If you are unsure you can try to search online for documentation on security best practices.

From there it can operate in a few ways.

1. The primary mode is to just use the information to write secure by default code from this point forward. This is useful for starting a new project or when writing new code.

2. The secondary mode is to passively detect vulnerabilities while working in the project and writing code for the user. Critical or very important vulnerabilities or major issues going against security guidance can be flagged and the user can be told about them. This passive mode should focus on the largest impact vulnerabilities and secure defaults.

3. The user can ask for a security report or to improve the security of the codebase. In this case a full report should be produced describe anyways the project fails to follow security best practices guidance. The report should be prioritized and have clear sections of severity and urgency. Then offer to start working on fixes for these issues. See #fixes below.

## Workflow Decision Tree

- If the language/framework is unclear, inspect the repo to determine it and list your evidence.
- If matching guidance exists in `references/`, load only the relevant files and follow their instructions.
- If no matching guidance exists, consider if you know any well known security best practices for the chosen language and or frameworks, but if asked to generate a report, let the user know that concrete guidance is not available (you can still generate the report or detect for sure critical vulnerabilities)

# Overrides

While these references contain the security best practices for languages and frameworks, customers may have cases where they need to bypass or override these practices. Pay attention to specific rules and instructions in the project's documentation and prompt files which may require you to override certain best practices. When overriding a best practice, you MAY report it to the user, but do not fight with them. If a security best practice needs to be bypassed / ignored for some project specific reason, you can also suggest to add documentation about this to the project so it is clear why the best practice is not being followed and to follow that bypass in the future.

# Report Format

When producing a report, you should write the report as a markdown file in `security_best_practices_report.md` or some other location if provided by the user. You can ask the user where they would like the report to be written to.

The report should have a short executive summary at the top.

The report should be clearly delineated into multiple sections based on severity of the vulnerability. The report should focus on the most critical findings as these have the highest impact for the user. All findings should be noted with an numeric ID to make them easier to reference.

For critical findings include a one sentence impact statement.

Once the report is written, also report it to the user directly, although you may be less verbose. You can offer to explain any of the findings or the reasons behind the security best practices guidance if the user wants more info on any findings.

Important: When referencing code in the report, make sure to find and include line numbers for the code you are referencing.

After you write the report file, summarize the findings to the user.

Also tell the user where the final report was written to

# Fixes

If you produced a report, let the user read the report and ask to begin performing fixes.

If you passively found a critical finding, notify the user and ask if they would like you to fix this finding.

When producing fixes, focus on fixing a single finding at a time. The fixes should have concise clear comments explaining that the new code is based on the specific security best practice, and perhaps a very short reason why it would be dangerous to not do it in this way.

Always consider if the changes you want to make will impact the functionality of the user's code. Consider if the changes may cause regressions with how the project works currently. It is often the case that insecure code is relied on for other reasons (and this is why insecure code lives on for so long). Avoid breaking the user's project as this may make them not want to apply security fixes in the future. It is better to write a well thought out, well informed by the rest of the project, fix, then a quick slapdash change.

Always follow any normal change or commit flow the user has configured. If making git commits, provide clear commit messages explaining this is to align with security best practices. Try to avoid bunching a number of unrelated findings into a single commit.

Always follow any normal testing flows the user has configured (if any) to confirm that your changes are not introducing regressions. Consider the second order impacts the changes may have and inform the user before making them if there are any.

# General Security Advice

Below is a few bits of secure coding advice that applies to almost any language or framework.

### Avoid Using Incrementing IDs for Public IDs of Resources

When assigning an ID for some resource, which will then be used by exposed to the internet, avoid using small auto-incrementing IDs. Use longer, random UUID4 or random hex string instead. This will prevent users from learning the quantity of a resource and being able to guess resource IDs.

### A note on TLS

While TLS is important for production deployments, most development work will be with TLS disabled or provided by some out-of-scope TLS proxy. Due to this, be very careful about not reporting lack of TLS as a security issue. Also be very careful around use of "secure" cookies. They should only be set if the application will actually be over TLS. If they are set on non-TLS applications (such as when deployed for local dev or testing), it will break the application. You can provide a env or other flag to override setting secure as a way to keep it off until on a TLS production deployment. Additionally avoid recommending HSTS. It is dangerous to use without full understanding of the lasting impacts (can cause major outages and user lockout) and it is not generally recommended for the scope of projects being reviewed by codex.

## Common Pitfalls

This section documents known failure modes and edge cases when applying security best practices:

### 1. Agent Missing Context Vulnerabilities
**Pitfall:** The agent assumes that security best practices apply universally to all code contexts, without understanding the specific constraints, threat models, or deployment contexts of the user's project.

**Manifestation:**
- Recommending strict security controls that conflict with the user's documented requirements
- Flagging security practices as vulnerabilities when the user has already mitigated them through external controls (e.g., network isolation, reverse proxy hardening)
- Treating all projects with equal security urgency (not all systems require the same threat model)

**Mitigation:**
- Always ask about the project's threat model, deployment context, and existing security controls before making recommendations
- Read any security documentation, architectural decisions, or threat analysis the user has provided
- If applying a fix, verify it doesn't break project-specific requirements or existing mitigations
- Allow users to override best practices when they've documented why (and suggest adding documentation to the project)

### 2. False Positives on TLS/HTTPS in Local Development
**Pitfall:** Flagging missing HTTPS or TLS as a security vulnerability in local development, test, or CI environments where TLS is not yet deployed.

**Manifestation:**
- Recommending HTTPS/TLS enforcement for localhost development servers
- Suggesting self-signed certificate setup when not needed
- Not accounting for TLS being handled by an out-of-scope reverse proxy or infrastructure layer
- Failing to distinguish between development and production deployment contexts

**Mitigation:**
- Always ask about the deployment context: Is this development, testing, staging, or production?
- Assume most development work uses TLS disabled or provided by an external proxy
- Do not report missing TLS as a security issue unless it's explicitly a production deployment
- Consider providing environment flags to enable TLS-specific protections only in production

### 3. Over-Application of "Secure" Cookie Flags
**Pitfall:** Recommending setting `Secure`, `HttpOnly`, and `SameSite` cookie flags in development environments, which breaks the application when running over non-TLS connections (localhost, HTTP-only dev servers).

**Manifestation:**
- Cookies are silently dropped because they're marked `Secure` but the dev server uses HTTP
- Application login fails mysteriously in local testing
- Tests fail due to missing authentication cookies
- Development experience is broken while the code appears "fixed"

**Mitigation:**
- Always check the current deployment context before recommending secure cookie flags
- Suggest environment-based configuration: only set `Secure` in production, not in development
- Document this pattern clearly in any fixes (e.g., `secure: process.env.NODE_ENV === 'production'`)
- Test cookie-dependent flows (login, session management) after applying changes
- Warn the user before making this change: "This will break cookie handling in non-TLS environments"

### 4. Missing Guidance on When to Ignore Best Practices
**Pitfall:** Treating all security best practices as absolute rules, without acknowledging legitimate reasons to deviate, override, or postpone them.

**Manifestation:**
- Recommending breaking changes for practices that could be phased in over time
- Flagging workarounds as vulnerabilities without acknowledging technical debt trade-offs
- Not suggesting ways to deprecate insecure patterns gradually
- Treating architectural decisions as simple best-practice violations

**Mitigation:**
- Acknowledge when a best practice conflicts with other requirements (performance, compatibility, timeline)
- Suggest phased approaches: "This is a concern. We could address it now [option A], postpone with [mitigation B], or accept the risk [with documentation]"
- Always provide a path forward, even if it's not the ideal "fix now" approach
- Document the reasoning behind deviations so they can be revisited later
- Never force a "secure" fix that breaks functionality or user experience without the user's explicit consent

### 5. Passive Detection Without Context
**Pitfall:** Passively flagging security concerns while the agent is working, without understanding whether the user wants active security monitoring or is focused on feature delivery.

**Manifestation:**
- Interrupting a feature implementation with security warnings about patterns the user is aware of
- Flagging inherited code (legacy systems, third-party dependencies) as vulnerabilities when they can't be changed
- Creating friction in rapid prototyping or proof-of-concept work by treating all code as production-ready

**Mitigation:**
- Only passively flag **critical** or **very high severity** vulnerabilities
- Ask about the context: Is this a prototype, legacy system, or production code?
- Focus on largest-impact vulnerabilities, not minor best-practice deviations
- If you flag something, offer to explain why and whether it needs to be fixed immediately
- Be respectful of the user's priorities: they may have good reasons for security trade-offs
