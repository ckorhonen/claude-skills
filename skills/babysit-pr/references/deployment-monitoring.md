# Deployment Monitoring

Use this after the pull request is merged and `gh_deploy_watch.py` says the PR is ready for production validation or needs intervention.

## Default order

1. Repository-native signals
2. Hosting/deployment provider signals
3. Production validation
4. Logs and metrics

## Repository-native signals

Start with the bundled watcher:

```bash
python3 skills/babysit-pr/scripts/gh_deploy_watch.py --pr auto --watch
```

If it reports `alert_deployment_failure`, inspect the linked workflow or deployment logs before making code changes.

If it reports `validate_production`, confirm the change in production with the narrowest useful smoke test for the feature.

## Hosting and deploy providers

Choose the provider that clearly exists in the repo or local toolchain.

### Cloudflare / Wrangler

Use when the repo contains `wrangler.toml`, `wrangler.json`, or `package.json` scripts that deploy Workers/Pages.

Useful commands:

```bash
wrangler deployments list
wrangler tail
```

### Vercel

Use when the repo contains `vercel.json`, `.vercel/`, or established Vercel CLI usage.

Useful commands:

```bash
vercel ls
vercel inspect <deployment-url-or-id>
```

### Other providers

Prefer the provider's official CLI or dashboard-oriented skill when one is already available in the environment. Do not invent provider-specific commands if there is no evidence the repo uses that platform.

## Logs and metrics

If observability tooling is available, check it after deployment succeeds:

- Datadog: look for error spikes, latency regressions, and new log patterns tied to the changed service.
- Provider logs: confirm the deployed version is serving requests without new exceptions.
- Synthetic or smoke tests: run the smallest production-safe validation that proves the changed behavior works.

## Failure policy

- Deployment or validation failure clearly tied to the merged change: fix it, push a follow-up branch, and open a new PR.
- Deployment failure unrelated to the merged change: alert the user with the evidence and avoid speculative fixes.
- No deployment signal exists after the grace window: report that the repo has no machine-readable deployment hook and list the checks you attempted.
