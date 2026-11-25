#!/usr/bin/env python3
"""
compare_conditions.py — Aggregate eval results and compute effect sizes between
with_breadcrumbs and without_breadcrumbs conditions.

Usage:
    python3 compare_conditions.py results/
    python3 compare_conditions.py results/ --dimension A
    python3 compare_conditions.py results/ --output report.md

Outputs a markdown report with:
- Per-condition metric means ± SD
- Effect sizes (Cohen's d) for each metric
- p-values (Welch's t-test)
- Visual comparison table
- Recommendation: "breadcrumbs add value" / "inconclusive" / "breadcrumbs hurt"
"""

import argparse
import json
import math
import sys
from pathlib import Path
from collections import defaultdict

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not installed. p-values will be omitted. Run: pip install scipy", file=sys.stderr)


def cohens_d(group1: list[float], group2: list[float]) -> float:
    """Compute Cohen's d effect size between two groups."""
    if len(group1) < 2 or len(group2) < 2:
        return float('nan')
    n1, n2 = len(group1), len(group2)
    mean1 = sum(group1) / n1
    mean2 = sum(group2) / n2
    var1 = sum((x - mean1) ** 2 for x in group1) / (n1 - 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / (n2 - 1)
    pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return (mean1 - mean2) / pooled_sd


def mean_sd(values: list[float]) -> tuple[float, float]:
    if not values:
        return float('nan'), float('nan')
    m = sum(values) / len(values)
    if len(values) < 2:
        return m, 0.0
    sd = math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))
    return m, sd


def interpret_effect_size(d: float) -> str:
    if math.isnan(d):
        return "N/A"
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def load_results(results_dir: Path, dimension: str = None) -> list[dict]:
    """Load all result JSON files from directory."""
    results = []
    for f in sorted(results_dir.glob("result_*.json")):
        try:
            data = json.loads(f.read_text())
            if dimension and data.get("dimension") != dimension:
                continue
            results.append(data)
        except Exception as e:
            print(f"WARNING: Could not load {f}: {e}", file=sys.stderr)
    return results


def group_by_condition(results: list[dict]) -> dict[str, list[dict]]:
    """Group results by condition."""
    groups = defaultdict(list)
    for r in results:
        condition = r.get("condition", "unknown")
        groups[condition].append(r)
    return dict(groups)


def extract_metric(results: list[dict], metric: str) -> list[float]:
    """Extract a metric value from a list of results."""
    values = []
    for r in results:
        v = r.get("metrics", {}).get(metric)
        if v is not None:
            values.append(float(v))
    return values


def generate_report(results: list[dict], output_path: str = None) -> str:
    """Generate a markdown comparison report."""
    lines = []
    lines.append("# Breadcrumb Eval: Results Report\n")

    groups = group_by_condition(results)

    # Key comparisons
    comparison_pairs = [
        ("with_breadcrumbs", "without_breadcrumbs", "Main comparison: WITH vs WITHOUT breadcrumbs"),
        ("inline_only", "autoresearch_md_only", "Format comparison: Inline comments vs control"),
        ("decision_md_only", "autoresearch_md_only", "Format comparison: DECISION.md vs control"),
        ("inline_and_decision_md", "autoresearch_md_only", "Format comparison: Both formats vs control"),
        ("misleading_breadcrumbs", "without_breadcrumbs", "Adversarial: Misleading vs no breadcrumbs"),
        ("stale_breadcrumbs", "with_breadcrumbs", "Decay: Stale vs accurate breadcrumbs"),
    ]

    lines.append("## Condition Counts\n")
    for cond, group in sorted(groups.items()):
        lines.append(f"- **{cond}**: {len(group)} runs")
    lines.append("")

    lines.append("## Metric Comparison\n")
    lines.append("| Comparison | Metric | Condition A | Condition B | Cohen's d | Effect | p-value |")
    lines.append("|------------|--------|-------------|-------------|-----------|--------|---------|")

    findings = []

    for cond_a, cond_b, label in comparison_pairs:
        if cond_a not in groups or cond_b not in groups:
            continue

        group_a = groups[cond_a]
        group_b = groups[cond_b]

        for metric in ["HNS", "RR"]:
            vals_a = extract_metric(group_a, metric)
            vals_b = extract_metric(group_b, metric)

            if not vals_a or not vals_b:
                continue

            mean_a, sd_a = mean_sd(vals_a)
            mean_b, sd_b = mean_sd(vals_b)
            d = cohens_d(vals_a, vals_b)
            effect = interpret_effect_size(d)

            p_val = "N/A"
            if HAS_SCIPY and len(vals_a) >= 2 and len(vals_b) >= 2:
                _, p = stats.ttest_ind(vals_a, vals_b, equal_var=False)
                p_val = f"{p:.3f}"

            lines.append(
                f"| {label} | {metric} | {mean_a:.3f}±{sd_a:.3f} (n={len(vals_a)}) | "
                f"{mean_b:.3f}±{sd_b:.3f} (n={len(vals_b)}) | "
                f"{d:.2f if not math.isnan(d) else 'N/A'} | {effect} | {p_val} |"
            )

            # For HNS: higher in A is better (A=with_breadcrumbs); d > 0 means A is better
            # For RR: lower in A is better; d > 0 means A has HIGHER RR (worse)
            if metric == "HNS" and not math.isnan(d):
                if d > 0.2:
                    findings.append(f"✅ {label}: breadcrumbs improve HNS by {effect} effect (d={d:.2f})")
                elif d < -0.2:
                    findings.append(f"❌ {label}: breadcrumbs hurt HNS (d={d:.2f})")
            if metric == "RR" and not math.isnan(d):
                if d < -0.2:
                    findings.append(f"✅ {label}: breadcrumbs reduce RR by {effect} effect (d={d:.2f})")
                elif d > 0.2:
                    findings.append(f"❌ {label}: breadcrumbs increase RR (d={d:.2f})")

    lines.append("")

    lines.append("## Key Findings\n")
    if findings:
        for f in findings:
            lines.append(f"- {f}")
    else:
        lines.append("- Insufficient data for conclusions. Run more scenarios.")
    lines.append("")

    lines.append("## Recommendation\n")
    positive_findings = sum(1 for f in findings if f.startswith("✅"))
    negative_findings = sum(1 for f in findings if f.startswith("❌"))

    if positive_findings > negative_findings * 2:
        lines.append("> **Breadcrumbs add significant value.** Add inline WHY comments and DECISION.md to the autoresearch skill.")
    elif negative_findings > positive_findings:
        lines.append("> **Breadcrumbs may hurt.** The existing ledger (autoresearch.md + results.jsonl) appears sufficient. Adding code comments may introduce noise without benefit.")
    else:
        lines.append("> **Inconclusive.** Results are mixed or insufficient. Increase N (run more scenarios) or test with a different model.")
    lines.append("")

    lines.append("## Token Overhead Summary\n")
    token_files = list(Path(results_dir if isinstance(results_dir, str) else ".").glob("token_counts_*.json"))
    if token_files:
        token_data = json.loads(token_files[-1].read_text())
        lines.append("| Condition | Total Tokens | Breadcrumb Tokens | TOR |")
        lines.append("|-----------|-------------|-------------------|-----|")
        for row in token_data:
            lines.append(f"| {row['condition']} | {row['total_tokens']} | {row['breadcrumb_tokens']} | {row['TOR']:.3f} |")
    else:
        lines.append("_Token counts not available. Run scenario 15 first._")
    lines.append("")

    report = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(report)
        print(f"Report saved: {output_path}", file=sys.stderr)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", help="Directory containing result JSON files")
    parser.add_argument("--dimension", help="Filter to specific dimension (A-F)")
    parser.add_argument("--output", help="Output path for markdown report")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"ERROR: Results directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    results = load_results(results_dir, args.dimension)
    if not results:
        print(f"No results found in {results_dir}", file=sys.stderr)
        sys.exit(0)

    print(f"Loaded {len(results)} results from {results_dir}", file=sys.stderr)
    report = generate_report(results, args.output)
    print(report)


if __name__ == "__main__":
    main()
