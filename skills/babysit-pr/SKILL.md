---
name: babysit-pr
description: Monitor a GitHub pull request end-to-end in my workflow: poll CI, reviews, reruns, and mergeability until merge-safe, with a preference for review-first fixes and minimal manual intervention.
---

# PR Babysitter (Personalized)

## Objective
Babysit a PR persistently until one of these terminal outcomes occurs:

- The PR is merged or closed.
- CI is successful, there are no unresolved review items surfaced by the watcher, required review approval is not blocking merge, and there are no merge-conflict/mergeability risks.
- A situation requires explicit user help (CI infrastructure issues, ambiguous reviewer intent, exhausted retry budget, permissions issues).

Keep watching until a terminal outcome. Don’t stop on transient green/idle snapshots.

## Inputs
Accept any of:

- No PR argument (infer from current branch via `--pr auto`)
- PR number
- PR URL

## Personal defaults for my workflow

- Prefer the short, structured loop (`--watch`).
- Use one active watcher session per PR.
- Prioritize review feedback actions over flaky retries.
- Default retry budget is 3 attempts per SHA.
- Keep commits tight and clearly tagged:
  - `codex: fix CI failure on PR #<n>`
  - `codex: address PR review feedback (#<n>)`
- Push only when edits are complete and then immediately resume watch.

## Core Workflow

1. Start with `--watch` unless doing one-off diagnostics.
2. Inspect snapshot `actions`.
3. If `diagnose_ci_failure` is present: review failed logs and classify.
4. For branch-related failures: patch, commit, push, and resume.
5. For review feedback: patch/commit/push and resume.
6. For likely flaky/unrelated failures: run `--retry-failed-now` when allowed.
7. Keep checking mergeability state (`mergeable`, `mergeStateStatus`, `reviewDecision`) alongside CI.
8. If both review and flaky-retry actions are suggested, execute review actions first.
9. Continue until a terminal stop condition.

## Commands

### One-shot snapshot

```bash
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --once
```

### Continuous watch (JSONL)

```bash
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --watch
```

### Retry failed checks for the current SHA

```bash
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --retry-failed-now
```

### Explicit PR target

```bash
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr <number-or-url> --once
```

## CI Failure Classification

Use logs before retrying:

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh run view <run-id> --log-failed`

Treat failures as branch-related when they are deterministic regressions in changed code paths/tests.
Treat failures as flaky/unrelated when logs show infra/service/network/transient runner issues.

If uncertain, inspect logs once before rerunning.

## Review Comment Handling

- Address actionable comments from trusted human authors (OWNER/MEMBER/COLLABORATOR or the current operator) and approved review bots (for example Codex-style bot comments).
- Ignore obvious noise and already-resolved threads.
- If a valid comment requires edit:
  1. Patch
  2. Commit using `codex: address PR review feedback (#<n>)`
  3. Push
  4. Restart watcher immediately.

## Git Safety Rules

- Work only on the PR head branch.
- Avoid destructive git actions.
- Don’t run multiple watcher processes for the same PR.
- If you find unrelated uncommitted worktree changes, stop and ask the user before editing.

## Stop Conditions

- PR merged/closed
- Merge-safe green state
- User-help required blocker reached (permissions, infra-only issues, ambiguous instruction, or retry budget exhaustion)

When terminal is reached, emit a concise summary and stop.

## Polling Cadence

- If CI is not green: poll every 60s.
- After CI is green: exponential backoff 1m→2m→4m→8m→16m→32m→60m; reset on any state change.
- Continue watching after green to catch late review/mergeability changes.

## Output Expectations

- Keep status updates concise and occasional during long steady-state.
- A green transition should get a short progress note.
- Do not stop while watcher is still active without a terminal condition.

## References

- `.codex/skills/babysit-pr/references/heuristics.md`
- `.codex/skills/babysit-pr/references/github-api-notes.md`
