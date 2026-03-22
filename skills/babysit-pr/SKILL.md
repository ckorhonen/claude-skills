---
name: babysit-pr
description: "Create, monitor, and shepherd a GitHub pull request end-to-end: respect repo PR templates, watch CI and reviews, fix branch-related failures, address valid comments, and validate post-merge deployment when possible."
---

# PR Lifecycle Operator

## Objective

Own the pull request from creation through post-merge validation with as little manual babysitting as possible.

Terminal outcomes:

- The PR is merged and the deployment looks healthy.
- The PR is merge-safe and waiting on humans.
- A blocker requires user help: ambiguous product intent, permissions, unrelated dirty worktree, external-only outage, or missing deployment visibility.

Do not stop at "PR created" or "CI is green once." Keep following the PR until one of the terminal outcomes is true.

## Common Failure Modes

These gotchas appear during real PR automation and require proactive handling:

**Watcher Script Exits Silently (Template Resolution)**
The watcher can exit unexpectedly if PR template resolution fails during preflight. Root cause: `resolve_pr_template.py` may fail to parse custom template syntax, or template file is unreadable. Mitigation: always run the resolver in `--json` mode first to validate template before starting the watcher. If resolution fails, fall back to the bundled default template at `assets/default_pr_template.md`.

**Multiple Watchers on Same PR (Duplicate Comments)**
Running multiple `gh_pr_watch.py` instances for the same PR causes duplicate comment processing and can result in duplicate bot comments or conflicting retry actions. This typically happens when the watcher is restarted without properly stopping the previous session. Mitigation: use one watcher session per PR. Verify no orphaned watcher processes exist before starting: `ps aux | grep gh_pr_watch`. Kill any stale sessions before resuming.

**CI Retry Logic Triggers on Non-Flaky Failures (Quota Waste)**
The retry logic may consume the CI retry budget on failures that are not actually transient (e.g., legitimate test failures from branch-specific issues). This wastes quota and can block progress on legitimate issues. Mitigation: always inspect CI logs with `gh run view <run-id> --log-failed` before retrying. Confirm the failure is truly flaky or unrelated to branch changes. Apply the heuristics in `references/heuristics.md` strictly before calling `--retry-failed-now`.

**Review Score Extraction Fails with Markdown Formatting**
When reviewers use markdown formatting in their score phrases (e.g., `**4/5** stars` or `` `4 out of 5` ``), the review score extraction regex may fail to match. This results in the watcher missing explicit scores and potentially merging PRs prematurely despite unfinished reviewer feedback. Mitigation: the score extractor looks for patterns like `5/5` and `5 out of 5`. If a reviewer uses markdown around the score, manually extract the numeric rating and document it in the PR thread before proceeding.

See references in each workflow section below for prevention strategies.

## Defaults

- Poll open PR state every 60 seconds.
- Use one watcher session per PR.
- Prefer fixing valid review feedback before retrying flaky CI.
- Treat reviewer scores as real requirements when explicitly stated.
- Use repo-native templates and signals before falling back to bundled defaults.

## Preflight

1. Confirm you are on the PR branch, not the default branch.
2. Confirm `gh auth status` works.
3. Check for unrelated uncommitted changes before editing.
4. Resolve the PR template before opening or rewriting the PR body.

## PR Template Handling

Use the resolver script first:

```bash
python3 skills/babysit-pr/scripts/resolve_pr_template.py --json
```

⚠️ **Related gotcha:** See "Watcher Script Exits Silently (Template Resolution)" under [Common Failure Modes](#common-failure-modes). Always validate template resolution before starting the watcher.

Rules:

- If the repo has a pull request template, preserve its section structure and fill it thoughtfully.
- If no repo template exists, use the bundled fallback at `assets/default_pr_template.md`.
- Prefer `gh pr create --body-file` or `gh pr edit --body-file` with a prepared body that mirrors the resolved template.
- Do not discard checklist items unless they are clearly irrelevant and leaving them blank would be misleading.

## Creation Workflow

1. Resolve the template.
2. Write a tight PR title.
3. Build a PR body that includes summary, testing, and rollout notes.
4. Push the branch.
5. Create or update the PR.
6. Start the watcher immediately after the push succeeds.

Helpful commands:

```bash
gh pr create --base <default-branch> --title "<title>" --body-file <body-file>
gh pr edit <pr-number> --title "<title>" --body-file <body-file>
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --watch
```

## Watcher Workflow

The watcher emits snapshots and recommended actions. Start with:

```bash
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --watch
```

⚠️ **Related gotchas:** See [Common Failure Modes](#common-failure-modes) for "Multiple Watchers on Same PR" and "Watcher Script Exits Silently." Ensure no stale watcher processes are running before starting, and verify template resolution completes cleanly.

Key actions:

- `process_review_comment`: inspect the new comment or review and decide whether it is valid, relevant, and actionable on the current branch.
- `improve_review_score`: a trusted reviewer gave an explicit score below the maximum; do not treat the work as complete yet.
- `diagnose_ci_failure`: inspect failed logs and decide whether the failure is branch-related.
- `retry_failed_checks`: rerun failed checks only when the failure looks flaky or unrelated.
- `stop_ready_to_merge`: CI is green, no outstanding trusted review items remain, and mergeability is clean.
- `stop_pr_closed`: the PR merged or closed; if merged, transition to deployment monitoring.
- `stop_exhausted_retries`: flaky retry budget is exhausted; ask the user for help with evidence.

## CI Failure Policy

Use `references/heuristics.md` for the classification checklist.

⚠️ **Related gotcha:** See "CI Retry Logic Triggers on Non-Flaky Failures" under [Common Failure Modes](#common-failure-modes). Always inspect logs before retrying to avoid wasting quota on legitimate failures.

Default commands:

```bash
gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha
gh run view <run-id> --log-failed
python3 skills/babysit-pr/scripts/gh_pr_watch.py --pr auto --retry-failed-now
```

Rules:

- Branch-related failure: fix it, run the narrowest useful validation, commit, push, and restart the watcher.
- Flaky or unrelated failure: rerun only after one log inspection confirms it is probably transient.
- Infra-only failures, auth problems, or missing permissions: surface the blocker and stop.

## Comment And Review Handling

Apply feedback from trusted humans and approved bots when it is technically correct, actionable, and consistent with user intent.

When new feedback appears:

1. Validate that the feedback is relevant to the current PR.
2. If action is required, implement the smallest correct fix.
3. Run focused validation.
4. Commit and push.
5. Restart the watcher immediately.

Ignore or escalate feedback when it is:

- already resolved
- clearly noisy
- ambiguous
- contradictory with explicit user direction
- blocked by unrelated dirty changes or a wider product decision

## Review Scores

The watcher now extracts explicit score phrases such as `5/5` and `5 out of 5` from trusted comments and reviews.

⚠️ **Related gotcha:** See "Review Score Extraction Fails with Markdown Formatting" under [Common Failure Modes](#common-failure-modes). If reviewers use markdown around scores, manually extract ratings before proceeding.

Rules:

- If a reviewer gives an explicit score below the maximum, treat that as unfinished work even if the PR is technically mergeable.
- Aim for the highest score before calling the PR done.
- After making improvements, wait for updated reviewer feedback rather than assuming the score increased.

## Git Safety

- Work only on the PR head branch.
- Avoid destructive git actions.
- Do not run multiple watcher processes for the same PR. (See [Common Failure Modes](#common-failure-modes): "Multiple Watchers on Same PR")
- If you find unrelated uncommitted worktree changes, stop and ask the user before editing.

## Post-Merge Deployment Monitoring

After merge, start the deployment watcher:

```bash
python3 skills/babysit-pr/scripts/gh_deploy_watch.py --pr auto --watch
```

The deployment watcher uses GitHub deployment records and deployment-like workflow runs tied to the merge commit. It stops with one of these actions:

- `wait_deployment`: a deployment signal exists and is still running.
- `wait_for_deployment_signal`: the PR merged recently and the grace window has not expired yet.
- `alert_deployment_failure`: a deployment signal failed; inspect logs and decide whether to ship a fix.
- `validate_production`: deployment signals look successful; run the narrowest useful production validation.
- `no_deployment_signal`: no machine-readable deployment signal was found after the grace window.
- `stop_pr_not_merged`: the PR is not merged yet.

Use `references/deployment-monitoring.md` for provider-specific follow-up, smoke tests, logs, and metrics guidance.

## Output Expectations

- Keep progress updates concise during steady-state watching.
- When you push a fix, summarize the root cause and what changed.
- When you stop, report the terminal condition and the evidence behind it.

## References

- `references/heuristics.md`
- `references/github-api-notes.md`
- `references/deployment-monitoring.md`
