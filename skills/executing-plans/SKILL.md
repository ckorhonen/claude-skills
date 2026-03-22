---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan
1. Read the plan file completely
2. Review it critically — this is where you catch flaws before they become expensive rework. Look for:
   - Steps that seem vague or contradictory
   - Missing dependencies or setup
   - Assumptions that don't hold in your actual codebase
   - Technical choices you'd question
3. If concerns exist: Raise them with your partner before proceeding. Getting alignment now saves many hours of wrong execution
4. If the plan looks solid: Create a todo tracker and proceed to Step 2

### Step 2: Execute Batch
**Default: First 3 tasks per batch**

The checkpoint-driven approach (3 tasks, pause for feedback, continue) gives your partner visibility and prevents you from building on a flawed foundation.

For each task in the batch:
1. Mark it as in_progress in your tracker
2. Follow the plan's steps exactly — they're designed to be small and verifiable
3. Run the specified verifications before marking done — this catches mistakes early
4. If verification fails: stop, report it, and wait for guidance
5. If verification passes: mark as completed and move to the next task

Keep focus tight. Executing 3 tasks well and getting feedback is faster than executing 10 tasks blind and discovering you went the wrong direction halfway through.

### Step 3: Report
When the batch is done, report clearly:
- Show what was implemented (what changed, new files, modified code)
- Show verification output (test results, error messages if any)
- Summarize any unexpected findings or minor deviations from the plan
- End with: "Ready for feedback."

This pause-to-report is critical. It gives your partner a chance to course-correct before you invest more work.

### Step 4: Continue
Your partner will respond. They might:
- Approve and ask you to continue (execute next batch)
- Point out an issue and ask for changes (go back to Step 1 or Step 2)
- Change the plan based on new information (return to Step 1)

Follow their guidance. The loop (Execute → Report → Feedback → Continue) prevents you from diverging.

Once you've completed all batches and your partner approves, move to Step 5 (Complete Development).

### Step 5: Complete Development

After all tasks complete and verified, use the superpowers:finishing-a-development-branch skill to wrap up. This skill handles the final verification and merge ceremony that you shouldn't do ad-hoc — it ensures tests pass, handles edge cases around main/master branches, and walks through proper cleanup.

- Announce: "I'm using the superpowers:finishing-a-development-branch skill to complete this work."
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

Execution should pause for clarification when:
- You hit a blocker mid-batch (missing dependency, test fails, instruction unclear) — continuing blind wastes effort
- The plan has critical gaps preventing starting — you can't execute what doesn't exist
- You don't understand an instruction — guessing is slower than asking
- Verification fails repeatedly — this signals the plan may have flawed assumptions

**Why this matters:** Stopping early prevents wasted work and lets your partner give you the right guidance. It's faster to pause and clarify than to build on a wrong foundation.

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Your partner updates the plan based on your feedback — old review isn't valid anymore
- Fundamental approach needs rethinking — new information changes strategy

**Forcing through blockers creates debt.** A pause to reconsider is faster than fixing mistakes later.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Between batches: just report and wait
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Common Pitfalls

### Agent Skips Review and Starts Executing Immediately
**The problem:** Jumping straight to Step 2 (Execute Batch) without doing Step 1 (Load and Review Plan). This skips your chance to catch plan flaws before wasting work.

**Why it happens:** Execution feels more productive than reading; the urge to "just start" is strong.

**How to avoid it:** Force yourself to read the plan, write down questions, and raise them before marking the first task in_progress. Your review step is the highest-leverage time to prevent rework.

### Batch Size Too Large Causes Confusion
**The problem:** Trying to execute 10+ tasks in a batch makes it hard to track what's done, what's blocked, and where verification failed. You lose the checkpoint benefit.

**Why it happens:** Wanting to move fast, or misunderstanding "default: first 3 tasks" as a minimum instead of a safe default.

**How to avoid it:** Stick to 3 tasks per batch unless the plan explicitly says otherwise. After you report and get feedback, you'll know if you should do bigger batches. Smaller batches = clearer reporting = faster feedback loops.

### Verification Failures Ignored
**The problem:** A verification fails (test doesn't pass, output doesn't match expected), but you mark the task completed anyway and move on. This compounds — later tasks depend on earlier ones working.

**Why it happens:** The temptation to "mark it done" and push forward. Verification feels like optional polish.

**How to avoid it:** If verification fails, that task is not done. Stop the batch, report the failure, and wait for guidance. The plan may have a flaw or you may have misunderstood a step. Your partner needs to know.

### Plan Becomes Stale Mid-Execution
**The problem:** You're halfway through executing, and your partner realizes the plan needs updating (scope changed, tech choice was wrong, new blocker discovered). But you keep executing the old plan.

**Why it happens:** You're focused on the tasks in front of you; you don't realize the plan has been superseded.

**How to avoid it:** After reporting each batch, read your partner's response carefully. If they mention plan changes, go back to Step 1 (Review) even if you're already partway through. Fresh context beats forward momentum.

## Integration

**Related workflow skills:**
- **superpowers:using-git-worktrees** — Sets up an isolated worktree before you execute. This prevents accidents on main and keeps your work sandboxed. You should create a worktree first (this skill guides that).
- **superpowers:writing-plans** — Generates the plan that this skill executes. This skill assumes a well-structured plan exists; if you need to create one, refer to that skill first.
- **superpowers:finishing-a-development-branch** — Completes development after all tasks are done. It handles testing, branch cleanup, and merge ceremony that you shouldn't improvise.
