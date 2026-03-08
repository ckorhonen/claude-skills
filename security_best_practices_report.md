# Skills Security Report

## Executive Summary

Reviewed 45 skill directories in `skills/`, excluding `babysit-pr`, with sub-agents plus local validation of the bundled scripts and templates.

- 19 skills contain code artifacts or runnable templates.
- Fast validation passed for the audited Python and shell scripts after fixes.
- `skills/cloudflare-manager` now installs cleanly with Bun and its CLI entrypoints load successfully.

This pass fixed the highest-confidence security and safety issues in `markdown-fetch`, `cloudflare-manager`, `opensea-api`, `poplar-direct-mail`, and `prompt-factory`. A few lower-risk findings remain open and are listed below.

## Fixed Findings

### SBP-001

**Severity:** High
**Status:** Fixed
**Location:** `skills/markdown-fetch/scripts/fetch.sh:9`, `skills/markdown-fetch/scripts/fetch.sh:19`, `skills/markdown-fetch/scripts/fetch.sh:101`

The request body was rebuilt with `jq -n` instead of shell string interpolation, eliminating JSON injection from untrusted URLs. Temporary files are now cleaned up reliably via `trap`, and the `jq` dependency check runs before first use.

### SBP-002

**Severity:** Medium
**Status:** Fixed
**Location:** `skills/cloudflare-manager/scripts/utils.ts:397`, `skills/cloudflare-manager/scripts/utils.ts:467`, `skills/cloudflare-manager/scripts/kv-storage.ts:258`, `skills/cloudflare-manager/scripts/r2-storage.ts:364`, `skills/cloudflare-manager/scripts/pages.ts:413`, `skills/cloudflare-manager/scripts/workers.ts:170`, `skills/cloudflare-manager/scripts/validate-api-key.ts:235`

`cloudflare-manager` now:

- preserves raw text request bodies instead of JSON-encoding them unconditionally
- encodes user-controlled path segments before inserting them into API URLs
- protects cached permission data with `0600` file mode
- writes worker temp files with restrictive permissions and removes them after upload
- blocks destructive commands in non-interactive shells unless `--force` is supplied

### SBP-003

**Severity:** Medium
**Status:** Fixed
**Location:** `skills/opensea-api/scripts/fetch_nft.sh:6`, `skills/opensea-api/scripts/fetch_nft.sh:35`, `skills/opensea-api/scripts/wallet_nfts.sh:6`, `skills/opensea-api/scripts/wallet_nfts.sh:47`, `skills/opensea-api/scripts/collection_stats.sh:6`, `skills/opensea-api/scripts/monitor_collection.sh:6`, `skills/opensea-api/scripts/monitor_collection.sh:48`

All OpenSea shell wrappers now run with `set -euo pipefail`, encode user-controlled path segments with `jq @uri`, and validate numeric inputs where appropriate (`limit`, `interval_seconds`).

### SBP-004

**Severity:** Low
**Status:** Fixed
**Location:** `skills/poplar-direct-mail/scripts/send_batch.py:36`, `skills/poplar-direct-mail/scripts/send_batch.py:153`, `skills/poplar-direct-mail/scripts/send_batch.py:180`, `skills/poplar-direct-mail/scripts/send_batch.py:194`

Batch-send logging no longer prints recipient names verbatim. Names are masked in dry runs, success logs, and error payloads to reduce PII exposure in local and CI logs.

### SBP-005

**Severity:** Low
**Status:** Fixed
**Location:** `skills/prompt-factory/scripts/validator.py:521`

The validation summary now handles empty result sets without dividing by zero.

## Open Findings

### SBP-006

**Severity:** Medium
**Status:** Open
**Location:** `skills/cloudflare-manager/scripts/workers.ts:175`, `skills/cloudflare-manager/scripts/workers.ts:178`, `skills/cloudflare-manager/scripts/r2-storage.ts:214`, `skills/cloudflare-manager/scripts/r2-storage.ts:217`, `skills/cloudflare-manager/scripts/r2-storage.ts:303`, `skills/cloudflare-manager/scripts/r2-storage.ts:306`

The Cloudflare bearer token is still passed to `curl` as a command-line header argument. That can expose the token to local process inspection (`ps`, `/proc`) on multi-user systems.

**Recommended remediation:** move the header out of argv entirely, either by switching these uploads/downloads to Bun-native `fetch`/`FormData` or by feeding headers through a protected temp config file or stdin.

### SBP-007

**Severity:** Low
**Status:** Open
**Location:** `skills/agent-browser/SKILL.md:270`, `skills/agent-browser/SKILL.md:295`, `skills/bird-fast/SKILL.md:344`, `skills/bird-fast/SKILL.md:354`, `skills/blockchain-auditor/SKILL.md:37`, `skills/blockchain-auditor/SKILL.md:201`, `skills/blockchain-auditor/SKILL.md:277`

Several documentation-only skills still demonstrate risky secret-handling patterns:

- literal bearer tokens and passwords in examples
- exporting long-lived session credentials directly in the shell
- passing private keys and API keys on command lines

**Recommended remediation:** rewrite examples to use env files, stdin, or secret managers, and explicitly call out process-listing and shell-history leakage risks.

### SBP-008

**Severity:** Low
**Status:** Open
**Location:** `skills/skill-finder/SKILL.md:97`, `skills/skill-finder/SKILL.md:177`, `skills/skill-finder/SKILL.md:195`

`skill-finder` recommends installing third-party skills directly from the registry without any integrity or provenance verification beyond basic popularity heuristics.

**Recommended remediation:** add a mandatory review step before install, prefer pinned commit SHAs or signed releases where available, and warn users when a skill will execute downloaded code locally.
