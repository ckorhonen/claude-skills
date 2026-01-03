---
description: Commit, push, and create a PR to the default branch
allowed-tools: Bash(git:*), Bash(gh:*)
argument-hint: [commit message instructions]
---

# Create Pull Request

## Current State
- Branch: !`git branch --show-current`
- Default branch: !`gh repo view --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null || echo "main"`
- Git status: !`git status --short`

## Instructions

Create a pull request by following these steps exactly:

### 1. Prerequisites Check
- Verify we're not on the default branch (error if we are)
- Verify `gh auth status` succeeds

### 2. Handle Uncommitted Changes
- If there are uncommitted changes (shown above), commit them
- Follow any commit message instructions: $ARGUMENTS
- If no uncommitted changes, skip to step 3

### 3. Push to Origin
- Check if upstream branch exists with `git rev-parse --abbrev-ref @{u} 2>/dev/null`
- If no upstream: run `git push -u origin HEAD`
- If upstream exists: run `git push`

### 4. Review PR Diff
- Run `git diff origin/<default-branch>...HEAD` to see all changes that will be in the PR
- Summarize the changes

### 5. Create the PR
- Use `gh pr create --base <default-branch>`
- Title: Keep under 80 characters, be descriptive
- Description: Keep under 5 sentences summarizing the changes
- If the user gave specific instructions in $ARGUMENTS about the PR, follow them

### Error Handling
If any step fails, stop immediately and ask the user for help. Do not continue to the next step.
