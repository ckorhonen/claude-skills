# GitHub CLI / API Notes For `babysit-pr`

## Primary commands

- PR metadata: `gh pr view --json number,url,state,mergedAt,closedAt,headRefName,headRefOid,headRepository,headRepositoryOwner,mergeable,mergeStateStatus,reviewDecision`
- PR checks: `gh pr checks --json name,state,bucket,link,workflow,event,startedAt,completedAt`
- Workflow runs for SHA:
  - `gh api repos/{owner}/{repo}/actions/runs -X GET -f head_sha=<sha> -f per_page=100`
- Failed log inspection:
  - `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
  - `gh run view <run-id> --log-failed`
- Retry failed jobs: `gh run rerun <run-id> --failed`

## Review endpoints

- Issue comments: `gh api repos/{owner}/{repo}/issues/<pr>/comments?per_page=100`
- Inline review comments: `gh api repos/{owner}/{repo}/pulls/<pr>/comments?per_page=100`
- Reviews: `gh api repos/{owner}/{repo}/pulls/<pr>/reviews?per_page=100`

## JSON fields used

- `gh pr view`: number, url, state, mergedAt, closedAt, headRefName, headRefOid, mergeable, mergeStateStatus, reviewDecision
- `gh pr checks`: bucket, state, name, workflow, link
- Workflow run entries: id, name, status, conclusion, html_url, head_sha
