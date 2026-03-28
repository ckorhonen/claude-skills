# End-to-End Skill Test Results

**Date:** 2026-03-28  
**Tester:** Subagent (claude-sonnet-4-6)  
**Branch:** test/end-to-end-results

---

## Summary

| Skill | Scripts Work | SKILL.md Clear | Bugs Found | Rating |
|-------|-------------|----------------|-----------|--------|
| autoresearch | ✅ Yes | ✅ Yes | 1 bug (SVG labels swapped) | 4/5 |
| hyperagent | ✅ Yes | ✅ Yes | 1 cosmetic issue | 4/5 |
| mcp-tester | N/A (no scripts) | ✅ Yes | 0 bugs | 3/5 |

---

## Test 1: `skills/autoresearch`

### Setup
- Created `/tmp/fib-test` with a Fibonacci calculator (`fib.py`)
- Created `autoresearch.sh` that emits `METRIC elapsed_ms=<value>`

**Note:** Scripts must be run with `PYTHONPATH` pointing to the scripts directory (they use a relative `from common import ...` that doesn't work from arbitrary directories):
```bash
PYTHONPATH=/path/to/skills/autoresearch/scripts python3 /path/to/init_experiment.py ...
```
This is not documented in SKILL.md.

### Step-by-Step

1. **init_experiment.py** — Ran successfully:
   ```bash
   PYTHONPATH=skills/autoresearch/scripts python3 skills/autoresearch/scripts/init_experiment.py \
     --goal "Speed up fibonacci computation" \
     --metric-name elapsed_ms --unit ms --direction lower \
     --command /tmp/fib-test/autoresearch.sh --scope fib.py
   ```
   Output: `{"status": "ok", ...}` ✅ Created `.autoresearch/session.json` and `autoresearch.md`.

2. **run_experiment.py (baseline)** — Ran 2 warmups + 5 measured trials:
   - Correctly parsed `METRIC elapsed_ms=28.3` lines
   - Correctly computed `summary.median`, `mean`, `min`, `max`
   - Status: `ok`, checks: `skipped` (no checks command) ✅

3. **log_experiment.py (baseline)** — Appended to `results.jsonl`:
   - Disposition: `keep` (initial baseline) ✅
   - Generated `results.csv` and `report.html` ✅

4. **Experiment 1 (minor refactor)** — Median slightly worse → `discard` ✅ Decision logic correct.

5. **Experiment 2 (pre-allocated list)** — Median marginally better but below 1% threshold → `discard` ✅ Threshold enforcement works.

6. **render_report.py** — Generated HTML report with SVG charts ✅

### Bugs Found

**Bug 1: SVG chart labels swapped in `skills/autoresearch/scripts/common.py`, line 404**

In `svg_line_chart()`, the top/bottom axis labels are inverted. The SVG coordinate system has y=0 at the top, and `point_y(max_value)` maps to a small y (near top), but the label at `y="20"` (top of chart) shows `min_value`. It should show `max_value`.

**Affected file:** `skills/autoresearch/scripts/common.py`, lines 404-405  
**Compare with:** `skills/hyperagent/scripts/common.py`, lines 470-471 (correct)

Fix applied:
```python
# Before (wrong):
<text x="{padding}" y="20" ...>{min_value:.4f} ...
<text x="{padding}" y="{height - 10}" ...>{max_value:.4f} ...

# After (correct):
<text x="{padding}" y="20" ...>{max_value:.4f} ...
<text x="{padding}" y="{height - 10}" ...>{min_value:.4f} ...
```

### Suggestions for Improvement

1. **PYTHONPATH issue**: SKILL.md doesn't document that scripts need `PYTHONPATH` set. Either add a note, or change scripts to use `sys.path.insert(0, ...)` to find `common.py`.
2. **Working directory sensitivity**: `autoresearch.sh` runs relative to cwd of the calling process. If scripts are called from a different directory, `./autoresearch.sh` breaks. The SKILL.md example implies running from project root, but this should be explicit.
3. The `init_experiment.py` script helpfully adds `.autoresearch/` to `.git/info/exclude` — nice touch.

### Overall Rating: 4/5

Excellent conceptual design and solid implementation. Scripts work end-to-end. Minor usability gaps around PYTHONPATH and working directory assumptions. The SVG label bug is a cosmetic issue that makes charts misleading.

---

## Test 2: `skills/hyperagent`

### Setup
- Created `/tmp/str-test` with a string pattern matching script (`agent.py`)
- Created `task.sh` that runs agent.py and emits `METRIC score=<elapsed_ms>`

### Step-by-Step

1. **init_session.py** — Ran successfully ✅
   - Created `.hyperagent/session.json`, `hyperagent.md`, `.hyperagent/variants/`
   - Added `.hyperagent/` to `.git/info/exclude`

2. **run_task.py (gen-000 baseline)** — Measured 5 trials, median: 29.35ms ✅

3. **log_variant.py (gen-000)** — Disposition: `keep` ✅ Archive written.

4. **select_parent.py** — Selected `gen-000` with `children_count=0` ✅
   - Parent selection logic correctly weights by score × exploration bonus

5. **run_task.py (gen-001)** — Replaced `find()` loop with `str.count()`:
   - Median dropped from 29.35ms → 4.01ms (86.3% improvement) ✅

6. **log_variant.py (gen-001)** — Disposition: `keep`, improvement: 86.33% ✅

7. **select_parent.py (gen-001)** — Selected gen-000 again due to exploration randomness.
   - Over 20 runs: gen-001 selected 18/20, gen-000 selected 2/20 ✅
   - This is expected per the paper's exploration-exploitation balance.

8. **run_task.py (gen-002)** — Pre-lowering patterns optimization:
   - Median: 3.97ms (0.997% improvement — below 1% threshold)

9. **log_variant.py (gen-002)** — Disposition: `discard` ✅ Threshold enforcement correct.

10. **render_report.py** — Generated HTML with lineage tree, disposition chart, SVG charts ✅

### Parent Selection Verification

The `select_parent_from_archive()` function works correctly:
- Computes children counts dynamically from archive (not from stored `children_count`)
- Applies exploration bias via `weight = norm_score / (1 + children_count)`
- Correctly favors high performers with few children

### Archive Update Verification

Archive correctly stores all variants. The `children_count` field in each archived record is always `0` (a cosmetic issue described below).

### Issues Found

**Issue 1 (Cosmetic): `children_count` stored in archive is always 0**

`log_variant.py` line 116 sets `final["children_count"] = 0` but never increments it when later variants are added. The `select_parent_from_archive()` function correctly computes children counts dynamically from `parent_id` fields, so functionality is unaffected. However, the archive schema (documented in SKILL.md) implies `children_count` is a live count, which is misleading.

**Affected file:** `skills/hyperagent/scripts/log_variant.py`, line 116  
**Severity:** Cosmetic / documentation mismatch (does not affect behavior)

### Suggestions for Improvement

1. **Document PYTHONPATH requirement** (same issue as autoresearch)
2. **children_count in archive**: Either update the count when children are added (requires rewriting the whole archive entry, which is complex since JSONL is append-only), or rename the field to `initial_children_count` and document that the live count is computed dynamically.
3. **No generate_variant.py**: SKILL.md clearly documents this is intentional ("the meta-agent role is performed by the LLM agent itself") — this is well-explained.
4. **Plateau detection output**: When plateau is detected, the HTML report prominently shows a red warning. Good UX.

### Overall Rating: 4/5

Very well designed. Scripts work end-to-end without issues. Parent selection logic matches the paper's description. The lineage tree HTML is a nice addition. Minor cosmetic issue with `children_count` stored as always-0.

---

## Test 3: `skills/mcp-tester`

### Overview

mcp-tester is a **methodology skill only** — it has no bundled scripts. The entire workflow is executed by the LLM agent using its native tool access to `mcp__*` prefixed tools.

### Can You Follow the Instructions?

**Phase 1 (Discovery):** Actionable if MCP tools are configured. The skill instructs listing `mcp__` prefixed tools and grouping by server namespace. In this test environment, no MCP servers were configured, so this phase cannot be executed.

**Phase 2 (Quality Analysis):** Well-defined rubric (naming conventions, description quality, token efficiency). The severity indicators (🔴🟡🔵✅) are clear and consistently applied throughout.

**Phase 3 (Test Design):** The AAA pattern (Arrange-Act-Assert) and test category matrix (happy path, invalid, edge cases) are thorough and sensible. Minimum test count per tool (5 tests) is a reasonable default.

**Phase 4 (Test Execution):** The mutating vs. read-only distinction with explicit confirmation request is a good safety practice. The confirmation dialog template is clear.

**Phase 5 (Rating):** The rating rubric (Worked/Partially/Failed) with four quality dimensions is well-structured.

**Phase 6 (Cross-Tool Analysis):** Redundancy detection table format is practical.

### Gaps and Unclear Parts

1. **No way to test without live MCP servers**: The skill is entirely dependent on the session having configured MCP servers. There's no way to do a dry run or test the methodology against mock tools. Adding a `--dry-run` mode or an example mock server configuration would help onboarding.

2. **"Response time (if perceivable delay)" is vague**: The test execution phase says to capture response time "if perceivable delay" — no guidance on what threshold constitutes "perceivable" or how to measure it (there's no timing tool in Claude Code).

3. **MCP Inspector section is standalone**: The MCP Inspector section describes a standalone tool (`npx @modelcontextprotocol/inspector`) but provides no integration with the main workflow. When should you use it vs. testing within Claude Code? The boundary isn't clear.

4. **Common Pitfalls section targets test framework developers**: The pitfalls (race conditions, async timing, mock behavior) are written as if the agent is building a test framework, not using MCP tools interactively within Claude Code. For example, "use proper async/await chains" doesn't apply to Claude Code's interactive testing.

5. **No example of a complete run**: The Examples section (Phase 1-6) describes the workflow but doesn't show actual output. A concrete example with real tool names and sample outputs would significantly improve usability.

6. **Phases 1-6 are ambitious for one session**: The full workflow (discovery + quality analysis + test design + execution + rating + cross-tool analysis) could take 30-60 minutes for a server with 10+ tools. The skill doesn't suggest scope limiting (e.g., "test 3 tools first").

### Suggestions for Improvement

1. Add a prerequisite check: "Verify MCP tools are available by trying `mcp__<server>__<tool>`. If none exist, guide user to configure servers first."
2. Provide a concrete worked example with real output for one complete tool test cycle.
3. Rewrite the Common Pitfalls section to focus on Claude Code interactive testing pitfalls (e.g., "don't test destructive tools without confirmation", "large responses may be truncated") rather than test framework development pitfalls.
4. Add scope guidance: suggest starting with 1-2 tools for an initial audit pass before testing everything.

### Overall Rating: 3/5

The methodology is sound and well-documented. The quality analysis rubric, test design patterns, and safety practices (confirm before mutating) are all excellent. However, it's incomplete without live MCP servers and the Common Pitfalls section is misaligned with the actual use case. No scripts to test independently.

---

## Bugs Fixed

| # | File | Line | Description | Fix |
|---|------|------|-------------|-----|
| 1 | `skills/autoresearch/scripts/common.py` | 404-405 | SVG chart Y-axis labels are swapped (min shown at top, max at bottom, should be reversed) | Swapped `min_value`/`max_value` in `svg_line_chart()` to match `hyperagent/scripts/common.py` |

---

## Cross-Cutting Observations

### PYTHONPATH / Import Issue (Both Skills)

Both `autoresearch` and `hyperagent` scripts use `from common import ...` which requires the scripts directory to be in `PYTHONPATH`. This is not documented in either SKILL.md.

**Recommended fix:** Add to the top of each script:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

Or document the required invocation pattern in SKILL.md:
```bash
PYTHONPATH=skills/autoresearch/scripts python3 skills/autoresearch/scripts/init_experiment.py ...
```

### Design Quality

Both `autoresearch` and `hyperagent` are impressively well-designed:
- Scripts are non-interactive with `--help` support
- JSON output on stdout, diagnostics on stderr
- Atomic file writes prevent corruption
- `.gitinfo/exclude` management is thoughtful
- HTML reports are functional and include SVG charts

The `hyperagent` skill is a faithful implementation of the Facebook Research Hyperagents paper (arXiv:2603.19461) concepts.

### mcp-tester Design Quality

The skill is well-organized but primarily a methodology guide without executable components. It would benefit from a companion script (e.g., `scripts/audit_tools.py`) that automates the discovery and quality analysis phases.
