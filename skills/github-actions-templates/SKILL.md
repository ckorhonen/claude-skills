---
name: github-actions-templates
description: Create production-ready GitHub Actions workflows for automated testing, building, and deploying applications. Use when setting up CI/CD with GitHub Actions, automating development workflows, or creating reusable workflow templates.
---

# GitHub Actions Templates

Production-ready GitHub Actions workflow patterns for testing, building, and deploying applications.

## Purpose

Create efficient, secure GitHub Actions workflows for continuous integration and deployment across various tech stacks.

## When to Use

- Automate testing and deployment
- Build Docker images and push to registries
- Deploy to Kubernetes clusters
- Run security scans
- Implement matrix builds for multiple environments

## Common Workflow Patterns

### Pattern 1: Test Workflow

```yaml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
    - uses: actions/checkout@v4

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linter
      run: npm run lint

    - name: Run tests
      run: npm test

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage/lcov.info
```

**Reference:** See `assets/test-workflow.yml`

### Pattern 2: Build and Push Docker Image

```yaml
name: Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

**Reference:** See `assets/deploy-workflow.yml`

### Pattern 3: Deploy to Kubernetes

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2

    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --name production-cluster --region us-west-2

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
        kubectl rollout status deployment/my-app -n production
        kubectl get services -n production

    - name: Verify deployment
      run: |
        kubectl get pods -n production
        kubectl describe deployment my-app -n production
```

### Pattern 4: Matrix Build

```yaml
name: Matrix Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: pytest
```

**Reference:** See `assets/matrix-build.yml`

## Workflow Best Practices

1. **Use specific action versions** (@v4, not @latest)
2. **Cache dependencies** to speed up builds
3. **Use secrets** for sensitive data
4. **Implement status checks** on PRs
5. **Use matrix builds** for multi-version testing
6. **Set appropriate permissions**
7. **Use reusable workflows** for common patterns
8. **Implement approval gates** for production
9. **Add notification steps** for failures
10. **Use self-hosted runners** for sensitive workloads

## Reusable Workflows

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - run: npm ci
    - run: npm test
```

**Use reusable workflow:**
```yaml
jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: '20.x'
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Security Scanning

```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

    - name: Run Snyk Security Scan
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Deployment with Approvals

```yaml
name: Deploy to Production

on:
  push:
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com

    steps:
    - uses: actions/checkout@v4

    - name: Deploy application
      run: |
        echo "Deploying to production..."
        # Deployment commands here

    - name: Notify Slack
      if: success()
      uses: slackapi/slack-github-action@v1
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK }}
        payload: |
          {
            "text": "Deployment to production completed successfully!"
          }
```

## Common Pitfalls

This section documents real failure modes and anti-patterns that cause GitHub Actions workflows to fail silently or unexpectedly.

### 1. Workflow Syntax Errors

**Problem:** YAML indentation, quotes, and expression syntax are the most common sources of silent failures.

**Common Errors:**

#### Incorrect indentation
```yaml
# ❌ WRONG - Missing indentation
on: push
jobs:
test:
  runs-on: ubuntu-latest
  steps:
  - run: npm test

# ✅ CORRECT
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
```
**Error message:** `"unexpected mapping value" or "mapping values are not allowed here"`
**Fix:** YAML is 2-space indentation strict. Use a YAML linter like `yamllint` in your workflow.

#### Expression syntax confusion
```yaml
# ❌ WRONG - Using $ without github context
- run: echo ${{ matrix.node-version }}

# ❌ WRONG - Missing quotes on complex expressions
env:
  MY_VAR: ${{ github.event.pull_request.title }}

# ✅ CORRECT
- run: echo "${{ matrix.node-version }}"

# ✅ CORRECT with quotes for strings
env:
  MY_VAR: "${{ github.event.pull_request.title }}"
```
**Error message:** `"Unable to process template language"` or `"unrecognized named value"`
**Fix:** Always quote expressions that will be used in shell commands or as strings. GitHub Actions requires proper quoting for safe expansion.

#### Multiline strings without pipe syntax
```yaml
# ❌ WRONG - Multiline without | or >
- run: echo "Line 1
Line 2"

# ✅ CORRECT using pipe (preserves newlines)
- run: |
  npm install
  npm run build
  npm test

# ✅ CORRECT using >  (folds newlines)
- name: Summary
  run: >
    This is a long
    command that spans
    multiple lines
```
**Error message:** `"expected '<block end>', but found '\\n'"`
**Fix:** Use `|` for literal blocks (preserves newlines) or `>` for folded blocks (folds newlines to spaces).

---

### 2. Secret Handling Mistakes

**Problem:** Secrets are the most frequently mishandled element. GitHub Actions has specific rules about when secrets are available.

**Critical Mistakes:**

#### Hardcoding secrets in workflow files
```yaml
# ❌ ABSOLUTELY WRONG - Secret is now in git history
- run: |
  aws s3 sync . s3://my-bucket \
    --aws-access-key-id AKIA1234567890ABCDEF \
    --aws-secret-access-key wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```
**Error message:** None initially, but this is a critical security vulnerability.
**Fix:** Always use `${{ secrets.SECRET_NAME }}` and define secrets in GitHub repository settings.

#### Accessing secrets in non-secret contexts
```yaml
# ❌ WRONG - Secrets not available in expressions before job runs
env:
  MESSAGE: ${{ secrets.MY_SECRET }}  # ← Undefined!

# ❌ WRONG - Secrets masked in logs but not available here
if: ${{ secrets.DEPLOY_KEY != '' }}

# ✅ CORRECT - Pass secret to step where it's needed
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        # Now DEPLOY_KEY is available here
        ./deploy.sh
```
**Error message:** Secret appears as `***` (masked) but is actually empty/undefined.
**Fix:** Define secrets at the step level where they're used, not at job level. Never use secrets in `if:` conditions.

#### Forgetting to mark outputs as sensitive
```yaml
# ❌ WRONG - Logs leak credentials
- name: Get credentials
  run: |
    TOKEN=$(curl -s https://api.example.com/token)
    echo "TOKEN=$TOKEN" >> $GITHUB_OUTPUT
    echo "Got token: $TOKEN"  # ← Logged!

# ✅ CORRECT - Mark as secret in action output
- name: Get credentials
  id: creds
  run: |
    TOKEN=$(curl -s https://api.example.com/token)
    echo "token=$TOKEN" >> $GITHUB_OUTPUT  # ← Set output
  # Then reference as:
  # ${{ steps.creds.outputs.token }}
```
**Error message:** Credentials appear in plain text in workflow logs.
**Fix:** Use `$GITHUB_OUTPUT` for sensitive values, and never `echo` them directly.

#### Wrong secret context in reusable workflows
```yaml
# ❌ WRONG - Parent secrets aren't automatically passed
jobs:
  call-workflow:
    uses: ./.github/workflows/deploy.yml
    # secrets: inherit not specified!

# ✅ CORRECT
jobs:
  call-workflow:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit  # ← Pass all parent secrets
```
**Error message:** Workflow runs but secrets are undefined in called workflow.
**Fix:** Include `secrets: inherit` when calling reusable workflows that need secrets.

---

### 3. Permission Issues

**Problem:** `GITHUB_TOKEN` has limited scopes by default, and permissions are easy to get wrong.

**Common Problems:**

#### Insufficient token permissions
```yaml
# ❌ WRONG - Trying to write packages with default permissions
- name: Push to Docker registry
  run: |
    docker push ghcr.io/${{ github.repository }}:latest
    # Fails with "permission denied" because GITHUB_TOKEN lacks 'packages: write'

# ✅ CORRECT - Explicitly grant permissions
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read        # Read repo code
      packages: write       # Write Docker images
      id-token: write       # For OIDC token exchange
    steps:
    - uses: actions/checkout@v4
    - name: Push to Docker registry
      run: docker push ghcr.io/${{ github.repository }}:latest
```
**Error message:** `"authentication failed, permission denied"` or `"Insufficient permissions"` from API
**Fix:** Always explicitly declare `permissions:` at job level with required scopes (contents, packages, id-token, pull-requests, issues, deployments, etc.)

#### Trying to use GITHUB_TOKEN for operations it can't do
```yaml
# ❌ WRONG - GITHUB_TOKEN can't trigger other workflows
- name: Trigger deployment
  run: |
    curl -X POST https://api.github.com/repos/${{ github.repository }}/dispatches \
      -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
      -d '{"event_type":"deploy"}'
    # Fails silently - GITHUB_TOKEN lacks workflow permissions

# ✅ CORRECT - Use a PAT (Personal Access Token) or GitHub App token
- name: Trigger deployment
  run: |
    curl -X POST https://api.github.com/repos/${{ github.repository }}/dispatches \
      -H "Authorization: token ${{ secrets.WORKFLOW_PAT }}" \
      -d '{"event_type":"deploy"}'
```
**Error message:** `"Resource not accessible by integration"` (HTTP 403)
**Fix:** GITHUB_TOKEN can't trigger workflows (`repository_dispatch`). Use a PAT stored in secrets for this.

#### Cross-repository access failures
```yaml
# ❌ WRONG - GITHUB_TOKEN only has access to current repo
- name: Clone another repo
  run: |
    git clone https://github.com/other-org/private-repo.git
    # Fails - GITHUB_TOKEN has no access

# ✅ CORRECT - Use a PAT with repo access
- name: Clone another repo
  run: |
    git clone https://x-access-token:${{ secrets.CROSS_REPO_PAT }}@github.com/other-org/private-repo.git
```
**Error message:** `"fatal: could not read Username for 'https://github.com': terminal prompts disabled"`
**Fix:** Use a Personal Access Token (PAT) with `repo` or `read:repo_hook` scope for cross-repository access.

---

### 4. Matrix Strategy Failures

**Problem:** Matrix builds are powerful but fail silently when combinations are wrong or when exclude/include are misused.

**Common Pitfalls:**

#### Undefined matrix context in steps
```yaml
# ❌ WRONG - Using matrix variables that don't exist
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    # No 'version' defined here

jobs:
  build:
    runs-on: ${{ matrix.os }}
    steps:
    - run: echo "Version is ${{ matrix.version }}"  # ← Empty!

# ✅ CORRECT - Define all matrix variables used
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    version: ['1.0', '2.0']
    
jobs:
  build:
    runs-on: ${{ matrix.os }}
    steps:
    - run: echo "Building for ${{ matrix.os }} v${{ matrix.version }}"
```
**Error message:** Matrix variable appears empty or undefined in logs.
**Fix:** All variables referenced in steps must be defined in `strategy.matrix`.

#### Broken exclude/include syntax
```yaml
# ❌ WRONG - Invalid exclude syntax
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node-version: ['18', '20']
  exclude:
    - os: windows-latest, node-version: '18'  # ← Comma not allowed here

# ✅ CORRECT - Proper exclude syntax
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node-version: ['18', '20']
  exclude:
    - os: windows-latest
      node-version: '18'

# ✅ Using include for specific combinations
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    include:
      - os: windows-latest
        node-version: '20'  # ← Only windows + node 20
```
**Error message:** Workflow fails to parse during validation phase.
**Fix:** `exclude` and `include` use YAML list syntax with separate lines for each property.

#### Cartesian product explosion
```yaml
# ❌ WRONG - Creates 4 × 3 × 2 × 5 = 120 jobs unexpectedly
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest, linux-arm64]
    node-version: ['16', '18', '20']
    npm-version: ['8', '9']
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    # This is excessive and wastes CI minutes

# ✅ CORRECT - Use include for specific combinations
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        node-version: '20'
        npm-version: '9'
      - os: macos-latest
        node-version: '20'
        npm-version: '9'
      - os: windows-latest
        node-version: '18'
        npm-version: '8'
```
**Error message:** None, but suddenly your CI spend quadruples.
**Fix:** Use `include` to define specific combinations instead of letting matrix create a Cartesian product.

---

### 5. Caching Mistakes

**Problem:** GitHub Actions caching is conservative—stale caches can persist for months and cause mysterious build failures.

**Critical Issues:**

#### Stale cache causing repeated failures
```yaml
# ❌ WRONG - Cache key doesn't change, stale deps stay cached
- uses: actions/cache@v3
  with:
    path: node_modules
    key: deps-${{ runner.os }}  # ← Never changes!
    restore-keys: |
      deps-${{ runner.os }}

# ✅ CORRECT - Include lockfile hash in cache key
- uses: actions/cache@v3
  with:
    path: node_modules
    key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      deps-${{ runner.os }}-
```
**Error message:** Build passes locally but fails in CI with cryptic module errors.
**Fix:** Always include a hash of your dependency lock file in the cache key: `${{ hashFiles('**/package-lock.json') }}` for npm, `${{ hashFiles('**/requirements.txt') }}` for pip.

#### Incorrect cache path for language runtimes
```yaml
# ❌ WRONG - Caching wrong path, cache misses happen
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '20.x'
- uses: actions/cache@v3
  with:
    path: /tmp/node_modules  # ← Wrong path!
    key: deps-${{ hashFiles('package-lock.json') }}

# ✅ CORRECT - Let action handle caching, or use right path
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '20.x'
    cache: 'npm'  # ← Let the action handle caching
    
# OR if manual caching:
- uses: actions/cache@v3
  with:
    path: ~/.npm  # ← Correct npm cache location
    key: npm-${{ hashFiles('package-lock.json') }}
```
**Error message:** Workflow runs slowly, repeatedly downloading dependencies.
**Fix:** Use the built-in `cache:` parameter in `setup-node@v4`, or cache the language runtime's official cache directory (e.g., `~/.npm`, `~/.pip-cache`).

#### Cache invalidation race conditions
```yaml
# ❌ WRONG - Multiple branches writing to same cache
branches:
  - main
  - develop
  - '*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/cache@v3
      with:
        path: dist
        key: build-${{ hashFiles('package.json') }}
        # develop branch builds with old deps, overwrites cache
        # main branch then gets develop's stale build artifacts

# ✅ CORRECT - Include branch in cache key or read-only on non-main
- uses: actions/cache@v3
  with:
    path: dist
    key: build-${{ github.ref }}-${{ hashFiles('package.json') }}
    restore-keys: |
      build-refs/heads/main-
      build-refs/heads/develop-
```
**Error message:** Mysterious test failures after merging (cache was poisoned from other branch).
**Fix:** Include `${{ github.ref }}` in cache key to isolate per-branch caches, or use read-only mode on non-main branches.

#### Docker layer cache not preserved
```yaml
# ❌ WRONG - Rebuilds every layer despite cache-from
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myimage:latest
    # cache-from: type=gha missing!

# ✅ CORRECT - Use GitHub Actions cache backend
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myimage:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```
**Error message:** Docker builds are extremely slow despite local caching working fine.
**Fix:** Always include `cache-from: type=gha` and `cache-to: type=gha,mode=max` in `docker/build-push-action` to cache layers across runs.

---

## Debugging Workflows

**Useful techniques when workflows fail:**

1. **Enable debug logging:** Set `ACTIONS_STEP_DEBUG=true` secret in repository settings to see detailed logs
2. **Check permissions:** Review job's `permissions:` block when API calls fail
3. **Validate YAML:** Run `yamllint` locally on workflow files before pushing
4. **Test matrix locally:** Simulate matrix combinations in local test script
5. **Inspect cache:** View cache entries in GitHub UI under "Actions" → "Caches"
6. **Review secrets:** Confirm all `${{ secrets.NAME }}` are defined in repository settings

## Reference Files

- `assets/test-workflow.yml` - Testing workflow template
- `assets/deploy-workflow.yml` - Deployment workflow template
- `assets/matrix-build.yml` - Matrix build template
- `references/common-workflows.md` - Common workflow patterns

## Related Skills

- `gitlab-ci-patterns` - For GitLab CI workflows
- `deployment-pipeline-design` - For pipeline architecture
- `secrets-management` - For secrets handling
