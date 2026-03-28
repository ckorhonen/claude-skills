---
name: systematic-debugging
description: Systematic step-by-step debugging process for bugs, test failures, and unexpected behavior. Use when a test fails, something isn't working as expected, user says "this is broken", "why isn't X working", "help me debug", or when you encounter any error before proposing a fix.
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

5. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Use the `superpowers:test-driven-development` skill for writing proper failing tests

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with your human partner before attempting more fixes**

   This is NOT a failed hypothesis - this is a wrong architecture.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5)

## your human partner's Signals You're Doing It Wrong

**Watch for these redirections:**
- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultrathink this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**When you see these:** STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Common Pitfalls

These are anti-patterns observed in debugging practice. Recognize them and correct course immediately. See also: [Red Flags](#red-flags---stop-and-follow-process) and [Common Rationalizations](#common-rationalizations) for related guidance.

### 1. Jumping to Solutions Before Reproducing (Premature Fixes)

**Anti-pattern:**
```
Error log shows "timeout" → assume network issue → add retry logic
(But you never actually reproduced the timeout)
```

**Problem:**
- Fix addresses a symptom you haven't verified
- Real issue remains unfixed, masked by the "fix"
- When symptom recurs, you waste time debugging your own patch

**How to avoid:**
- **Phase 1 requirement:** Can you trigger the bug reliably with known steps?
- Document exact reproduction: "Run `npm test` with X set to Y" → bug happens
- If you can't reproduce it, you can't verify your fix works
- Reproducibility is non-negotiable — gather more data until you can trigger it

**Recovery:**
- Stop. Return to Phase 1.
- Find exact reproduction steps.
- THEN move to Phase 2.

---

### 2. Changing Multiple Things at Once (Can't Isolate Root Cause)

**Anti-pattern:**
```
Change 3 things:
  - Update dependency version
  - Refactor retry logic
  - Add fallback handler
Run tests → passes
```

**Problem:**
- Which change fixed it? Unknown.
- If one change introduces a subtle bug, you won't catch it for months
- Future bugs in that code path will be doubly confusing

**How to avoid:**
- **Phase 3 requirement:** "Test minimally. Make the SMALLEST possible change."
- ONE variable at a time
- Test after EACH change
- If you can't isolate what fixed it, the fix is incomplete knowledge

**Recovery:**
- Revert all changes. Start over.
- Change ONE thing. Test.
- Document: "This change alone fixed it because [reason]"
- Repeat for next hypothesis.

---

### 3. Assuming Bug Is in Recent Changes (Ignoring Environment/Data)

**Anti-pattern:**
```
Feature shipped 3 days ago → bug happened today → bug must be in that feature
(But you didn't verify the feature code against current data/environment)
```

**Problem:**
- Recent code LOOKS suspicious but environment changes are hard to see
- You waste days debugging code that's actually fine
- Real cause: data corruption, environment misconfiguration, dependency update

**How to avoid:**
- **Phase 1 requirement:** "Check Recent Changes" includes:
  - Git diffs in code? Yes.
  - Dependency updates? Yes.
  - Environment changes? Yes.
  - Data migrations? Yes.
  - Config changes? Yes.
- Test hypothesis: revert recent code change, see if bug persists
- If bug still happens without recent changes, it's environmental
- For multi-component systems, use diagnostic instrumentation (see Phase 1 Step 4)

**Recovery:**
- List ALL changes in last week: code, dependencies, config, environment, data
- Systematically rule out environment/data causes
- Only then focus on code

---

### 4. Not Documenting Reproduction Steps (Can't Verify Fix)

**Anti-pattern:**
```
"Fixed the bug" (but didn't write down how to trigger it)
Weeks later: "Wait, does this still happen? I don't remember how to trigger it"
```

**Problem:**
- You can't verify your fix actually works
- You can't tell colleagues how to test it
- You can't catch regression

**How to avoid:**
- **Phase 1 requirement:** "Reproduce Consistently"
  - Write down exact steps
  - Format: "To reproduce: [step 1], [step 2], [step 3]"
- Before moving to Phase 2, add these steps as a comment in your PR/issue
- After implementing fix, re-run exact steps to verify
- Convert reproduction steps to a test case (Phase 4, Step 1)

**Recovery:**
- Document reproduction steps NOW
- Don't claim fix is done until you've re-run exact steps
- If you documented reproduction steps and can no longer trigger the bug after the fix, that confirms the fix works

---

### 5. Debugging Without Logs/Observability (Flying Blind)

**Anti-pattern:**
```
Error happens in production
You: "Probably a race condition?"
You don't have logs showing what was happening at that moment
You guess at fixes for 3 hours
```

**Problem:**
- You're making decisions without evidence
- Guessing at fixes creates new bugs
- Same error will recur because you never understood cause

**How to avoid:**
- **Phase 1 requirement:** "Gather Evidence in Multi-Component Systems"
- Before debugging, ask: "What logs do we have?"
- If missing: add temporary logging, reproduce locally
- Don't propose fixes without evidence of what's happening
- For production issues: capture logs/metrics at time of failure

**Specific strategies:**
```bash
# Reproduce with logging
DEBUG=* npm test           # Enable all logs
strace node app.js         # System call tracing
tcpdump -i any -w dump     # Network tracing
```

**Recovery:**
- Pause. Add logging for key decision points.
- Reproduce the issue with enhanced logging.
- Now you have evidence to form hypothesis.
- THEN propose fix.

---

### 6. Testing Without a Failing Test Case (Verification Theater)

**Anti-pattern:**
```
Implement fix
Run manual test: "Looks good"
Commit and push
(No automated test proving bug existed)
```

**Problem:**
- You "fixed" something, but you never proved it was broken
- Regression testing later shows the bug still happens
- You can't distinguish between "I fixed it" and "I got lucky"

**How to avoid:**
- **Phase 4 requirement:** "Create Failing Test Case"
  - Test MUST fail before fix
  - Test MUST pass after fix
  - Test proves bug existed, fix eliminates bug
- Don't implement fix without a failing test
- Automated test (unit test, integration test, one-off script) > manual verification

**Recovery:**
- Revert your fix
- Write test that reproduces the bug
- Verify test fails
- Implement fix
- Verify test passes

---

### 7. Not Isolating the Failing Component (Blame Everything)

**Anti-pattern:**
```
Database slow? Maybe it's the query. Maybe it's the network. Maybe it's CPU.
Let me add caching, fix indexes, reduce batch size, and upgrade servers.
```

**Problem:**
- You waste resources fixing things that aren't broken
- You never understand the actual bottleneck
- Future optimization attempts fail because you're not sure what to optimize

**How to avoid:**
- **Phase 1 requirement:** "Gather Evidence in Multi-Component Systems"
  - For each component boundary, log data entering and exiting
  - Identify WHICH component is slow/failing
  - Focus investigation on that one component
  - Don't optimize 5 things, optimize the bottleneck

**Example:**
```bash
# API slow. Which part?
time curl /api/endpoint              # Total time
# Add logging to API entry point
# Add logging before DB query
# Add logging after DB returns
# Add logging before response

# Now you know: API fast (10ms), DB query slow (2s) → focus on DB
```

**Recovery:**
- Use diagnostic instrumentation to identify which component is actually failing
- Don't propose fixes until you've isolated the specific component

---

### 8. Assuming Your Fix Is Complete (Missing Edge Cases)

**Anti-pattern:**
```
Test case passes for happy path
Deploy without testing error cases
(Bug appears 2 weeks later under edge condition you didn't think to test)
```

**Problem:**
- Fix addresses one scenario but breaks others
- Edge cases are where 80% of bugs hide

**How to avoid:**
- **Phase 4 requirement:** "Verify Fix"
  - Test passing case
  - Test error cases
  - Test boundary conditions
  - Test with invalid/empty/extreme data
  - Test interaction with other components
- Comprehensive test coverage BEFORE deploying
- Regression tests for each bug you've fixed

**Recovery:**
- Add edge case tests
- Re-run comprehensive test suite
- Don't declare fix done until all cases pass

---

These pitfalls are patterns, not one-off mistakes. When you catch yourself in one, stop and realign to the process.

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

These techniques are part of systematic debugging and available in this directory:

- **`root-cause-tracing.md`** - Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** - Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** - Replace arbitrary timeouts with condition polling

**Related skills:**
- **superpowers:test-driven-development** - For creating failing test case (Phase 4, Step 1)
- **superpowers:verification-before-completion** - Verify fix worked before claiming success

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common
