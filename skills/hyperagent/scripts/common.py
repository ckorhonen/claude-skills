#!/usr/bin/env python3
"""Shared utilities for the hyperagent skill scripts."""

from __future__ import annotations

import csv
import html
import json
import math
import os
import random
import shlex
import statistics
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARTIFACTS_DIRNAME = ".hyperagent"


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def artifacts_dir(cwd: Path | None = None) -> Path:
    return (cwd or Path.cwd()) / ARTIFACTS_DIRNAME


def ensure_artifacts_dir(cwd: Path | None = None) -> Path:
    path = artifacts_dir(cwd)
    path.mkdir(parents=True, exist_ok=True)
    (path / "variants").mkdir(exist_ok=True)
    return path


def session_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "session.json"


def archive_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "archive.jsonl"


def memory_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "memory.jsonl"


def csv_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "results.csv"


def report_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "report.html"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_session(cwd: Path | None = None) -> dict[str, Any]:
    path = session_path(cwd)
    session = load_json(path)
    if not session:
        raise FileNotFoundError(
            f"Session file not found at {path}. Run scripts/init_session.py first."
        )
    return session


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def detect_git_root(cwd: Path | None = None) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def ensure_git_exclude(pattern: str, cwd: Path | None = None) -> bool:
    git_root = detect_git_root(cwd)
    if git_root is None:
        return False
    exclude_path = git_root / ".git" / "info" / "exclude"
    existing = set()
    if exclude_path.exists():
        existing = {
            line.strip()
            for line in exclude_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
    if pattern in existing:
        return False
    with exclude_path.open("a", encoding="utf-8") as handle:
        if exclude_path.stat().st_size > 0:
            handle.write("\n")
        handle.write(f"{pattern}\n")
    return True


def git_status_files(cwd: Path | None = None) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    files: list[str] = []
    for raw_line in result.stdout.splitlines():
        if len(raw_line) < 4:
            continue
        entry = raw_line[3:]
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        files.append(entry)
    return files


def current_git_ref(cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "working-tree"
    return result.stdout.strip()


def parse_metric_lines(text: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("METRIC "):
            continue
        payload = line[len("METRIC "):].strip()
        if payload.startswith("{"):
            try:
                json_payload = json.loads(payload)
            except json.JSONDecodeError:
                continue
            for key, value in json_payload.items():
                try:
                    metrics[key] = float(value)
                except (TypeError, ValueError):
                    continue
            continue
        for token in payload.split():
            if "=" not in token:
                continue
            name, value = token.split("=", 1)
            value = value.rstrip(",")
            try:
                metrics[name] = float(value)
            except ValueError:
                continue
    return metrics


def summary_stats(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("Cannot summarize an empty list of values.")
    return {
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "min": min(values),
        "max": max(values),
    }


def compute_secondary_metrics(
    trial_metrics: list[dict[str, float]], primary_metric: str
) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    for trial in trial_metrics:
        for name, value in trial.items():
            if name == primary_metric:
                continue
            buckets.setdefault(name, []).append(value)
    return {
        name: statistics.median(values)
        for name, values in buckets.items()
        if values
    }


def compare_metric(
    candidate: float, baseline: float, direction: str
) -> tuple[bool, float | None]:
    if direction not in {"lower", "higher"}:
        raise ValueError(f"Unsupported direction: {direction}")
    if direction == "lower":
        better = candidate < baseline
        if baseline == 0:
            improvement_pct = None
        else:
            improvement_pct = ((baseline - candidate) / baseline) * 100.0
    else:
        better = candidate > baseline
        if baseline == 0:
            improvement_pct = None
        else:
            improvement_pct = ((candidate - baseline) / baseline) * 100.0
    return better, improvement_pct


def run_shell_command(
    command: str, cwd: Path | None = None, timeout_seconds: int | None = None
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd or Path.cwd(),
            shell=True,
            executable=os.environ.get("SHELL", "/bin/bash"),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(str(exc)) from exc


def stderr_tail(text: str, limit: int = 40) -> str:
    lines = text.splitlines()
    if len(lines) <= limit:
        return text.strip()
    return "\n".join(lines[-limit:]).strip()


# --- Archive & Parent Selection ---


def load_archive(cwd: Path | None = None) -> list[dict[str, Any]]:
    return read_jsonl(archive_path(cwd))


def get_best_variant(
    archive: list[dict[str, Any]], direction: str
) -> dict[str, Any] | None:
    kept = [r for r in archive if r.get("disposition") == "keep" and r.get("summary", {}).get("median") is not None]
    if not kept:
        return None
    best = kept[0]
    for record in kept[1:]:
        c = record["summary"]["median"]
        b = best["summary"]["median"]
        if direction == "lower" and c < b:
            best = record
        elif direction == "higher" and c > b:
            best = record
    return best


def select_parent_from_archive(
    archive: list[dict[str, Any]], direction: str
) -> dict[str, Any] | None:
    """Select a parent using performance-weighted, exploration-biased sampling.

    Probability ∝ normalized_score / (1 + children_count).
    This is the parent selection strategy from the Hyperagents paper.
    """
    candidates = [
        r for r in archive
        if r.get("disposition") == "keep" and r.get("summary", {}).get("median") is not None
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Count children for each candidate
    parent_ids = set(r.get("id") for r in candidates)
    children_counts: dict[str, int] = {pid: 0 for pid in parent_ids if pid}
    for r in archive:
        pid = r.get("parent_id")
        if pid and pid in children_counts:
            children_counts[pid] += 1

    # Compute selection weights
    scores = [float(r["summary"]["median"]) for r in candidates]
    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score if max_score != min_score else 1.0

    weights: list[float] = []
    for r in candidates:
        score = float(r["summary"]["median"])
        # Normalize score to [0.1, 1.0]
        if direction == "higher":
            norm = 0.1 + 0.9 * ((score - min_score) / score_range)
        else:
            norm = 0.1 + 0.9 * ((max_score - score) / score_range)
        # Exploration bonus: favor parents with fewer children
        children = children_counts.get(r.get("id", ""), 0)
        weight = norm / (1 + children)
        weights.append(weight)

    total = sum(weights)
    if total == 0:
        return random.choice(candidates)

    probs = [w / total for w in weights]
    chosen_index = random.choices(range(len(candidates)), weights=probs, k=1)[0]
    return candidates[chosen_index]


def detect_plateau(archive: list[dict[str, Any]], window: int = 3) -> bool:
    """Return True if the last `window` non-baseline variants were all discarded/crashed."""
    recent = [r for r in archive if not r.get("baseline")]
    if len(recent) < window:
        return False
    tail = recent[-window:]
    return all(r.get("disposition") != "keep" for r in tail)


def improvement_velocity(archive: list[dict[str, Any]], window: int = 5) -> float | None:
    """Compute average improvement % over last `window` kept variants."""
    kept = [r for r in archive if r.get("disposition") == "keep" and r.get("improvement_pct") is not None]
    if len(kept) < 2:
        return None
    recent = kept[-window:]
    improvements = [r["improvement_pct"] for r in recent if r.get("improvement_pct") is not None]
    if not improvements:
        return None
    return statistics.fmean(improvements)


# --- Memory ---


def append_memory(entry: dict[str, Any], cwd: Path | None = None) -> None:
    """Append a qualitative memory entry to the persistent memory log."""
    entry["timestamp"] = now_utc_iso()
    append_jsonl(memory_path(cwd), entry)


def load_memory(cwd: Path | None = None) -> list[dict[str, Any]]:
    return read_jsonl(memory_path(cwd))


# --- CSV & Report Rendering ---


def write_results_csv(
    results: list[dict[str, Any]], output_path: Path | None = None
) -> Path:
    path = output_path or csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "generation", "parent_id", "timestamp", "baseline", "disposition",
        "checks", "metric_name", "median", "mean", "min", "max",
        "improvement_pct", "candidate_ref", "files_touched",
        "hypothesis", "change_summary", "measured_trials",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in results:
            summary = record.get("summary", {})
            writer.writerow({
                "id": record.get("id", ""),
                "generation": record.get("generation", ""),
                "parent_id": record.get("parent_id", ""),
                "timestamp": record.get("timestamp", ""),
                "baseline": record.get("baseline", False),
                "disposition": record.get("disposition", ""),
                "checks": record.get("checks", ""),
                "metric_name": record.get("metric_name", ""),
                "median": summary.get("median", ""),
                "mean": summary.get("mean", ""),
                "min": summary.get("min", ""),
                "max": summary.get("max", ""),
                "improvement_pct": record.get("improvement_pct", ""),
                "candidate_ref": record.get("candidate_ref", ""),
                "files_touched": ";".join(record.get("files_touched", [])),
                "hypothesis": record.get("hypothesis", ""),
                "change_summary": record.get("change_summary", ""),
                "measured_trials": ",".join(
                    str(v) for v in record.get("measured_trials", [])
                ),
            })
    return path


def svg_line_chart(
    title: str, values: list[float], labels: list[str], unit: str
) -> str:
    width = 760
    height = 240
    padding = 36
    if not values:
        return f"<section><h3>{html.escape(title)}</h3><p>No data yet.</p></section>"

    min_value = min(values)
    max_value = max(values)
    if math.isclose(min_value, max_value):
        min_value -= 1
        max_value += 1

    def px(i: int) -> float:
        if len(values) == 1:
            return width / 2
        return padding + i * (width - padding * 2) / (len(values) - 1)

    def py(v: float) -> float:
        s = (v - min_value) / (max_value - min_value)
        return height - padding - s * (height - padding * 2)

    points = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(values))
    circles = "\n".join(
        f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="4" fill="#2563eb">'
        f"<title>{html.escape(labels[i])}: {v:.4f} {html.escape(unit)}</title></circle>"
        for i, v in enumerate(values)
    )

    return f"""
<section class="chart">
  <h3>{html.escape(title)}</h3>
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
    <polyline fill="none" stroke="#2563eb" stroke-width="3" points="{points}" />
    {circles}
    <text x="{padding}" y="20" fill="#111827" font-size="12">{max_value:.4f} {html.escape(unit)}</text>
    <text x="{padding}" y="{height - 10}" fill="#111827" font-size="12">{min_value:.4f} {html.escape(unit)}</text>
  </svg>
</section>
""".strip()


def svg_disposition_chart(results: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for r in results:
        d = r.get("disposition", "unknown")
        counts[d] = counts.get(d, 0) + 1
    if not counts:
        return "<section><h3>Disposition counts</h3><p>No data.</p></section>"
    order = ["keep", "discard", "checks_failed", "crash"]
    items = [(n, counts[n]) for n in order if n in counts]
    colors = {"keep": "#10b981", "discard": "#6b7280", "checks_failed": "#f59e0b", "crash": "#ef4444"}
    width = 760
    height = 220
    padding = 40
    max_c = max(c for _, c in items) or 1
    bw = 100
    gap = 60
    x = padding
    bars: list[str] = []
    for name, count in items:
        bh = (count / max_c) * (height - padding * 2)
        y = height - padding - bh
        color = colors.get(name, "#6b7280")
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{bh:.1f}" fill="{color}" rx="6"/>'
            f'<text x="{x + bw / 2:.1f}" y="{height - 12}" text-anchor="middle" font-size="12">{html.escape(name)}</text>'
            f'<text x="{x + bw / 2:.1f}" y="{max(20, y - 8):.1f}" text-anchor="middle" font-size="12">{count}</text>'
        )
        x += bw + gap
    return f"""
<section class="chart">
  <h3>Disposition counts</h3>
  <svg viewBox="0 0 {width} {height}" role="img">{" ".join(bars)}</svg>
</section>""".strip()


def build_lineage_tree(archive: list[dict[str, Any]]) -> str:
    """Build an HTML lineage tree showing parent→child relationships."""
    if not archive:
        return "<p>No variants in archive.</p>"

    children_map: dict[str, list[str]] = {}
    variant_map: dict[str, dict[str, Any]] = {}
    roots: list[str] = []
    for r in archive:
        vid = r.get("id", "unknown")
        variant_map[vid] = r
        pid = r.get("parent_id")
        if pid:
            children_map.setdefault(pid, []).append(vid)
        else:
            roots.append(vid)

    def render_node(vid: str, depth: int = 0) -> str:
        r = variant_map.get(vid, {})
        disp = r.get("disposition", "?")
        median = r.get("summary", {}).get("median")
        median_str = f"{median:.4f}" if median is not None else "N/A"
        icon = {"keep": "✅", "discard": "❌", "crash": "💥", "checks_failed": "⚠️"}.get(disp, "❓")
        indent = "&nbsp;" * (depth * 4)
        line = f'{indent}{icon} <strong>{html.escape(vid)}</strong> — {median_str} ({disp})'
        if r.get("hypothesis"):
            line += f' — <em>{html.escape(r["hypothesis"][:60])}</em>'
        lines = [f"<div>{line}</div>"]
        for child_id in children_map.get(vid, []):
            lines.append(render_node(child_id, depth + 1))
        return "\n".join(lines)

    html_parts = [render_node(r) for r in roots]
    return "\n".join(html_parts)


def render_html_report(
    session: dict[str, Any],
    results: list[dict[str, Any]],
    output_path: Path | None = None,
) -> Path:
    path = output_path or report_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    metric_name = session.get("metric_name", "metric")
    unit = session.get("unit", "")
    direction = session.get("direction", "lower")

    medians = [
        float(r.get("summary", {}).get("median"))
        for r in results if r.get("summary", {}).get("median") is not None
    ]
    labels = [r.get("id", "?") for r in results if r.get("summary")]

    best_so_far: list[float] = []
    current_best: float | None = None
    for v in medians:
        if current_best is None:
            current_best = v
        elif direction == "lower":
            current_best = min(current_best, v)
        else:
            current_best = max(current_best, v)
        best_so_far.append(current_best)

    keep_count = sum(1 for r in results if r.get("disposition") == "keep")
    discard_count = sum(1 for r in results if r.get("disposition") == "discard")
    fail_count = sum(1 for r in results if r.get("disposition") in {"checks_failed", "crash"})

    # Best variant
    best_record = get_best_variant(results, direction)
    best_html = "<p>No kept result yet.</p>"
    if best_record:
        bv = best_record.get("summary", {}).get("median")
        best_html = f'<p><strong>{html.escape(best_record.get("id", "?"))}</strong> at {bv:.4f} {html.escape(unit)}'
        if best_record.get("improvement_pct") is not None:
            best_html += f' ({best_record["improvement_pct"]:.2f}% improvement)'
        best_html += "</p>"

    # Table rows
    rows: list[str] = []
    for r in results:
        imp = r.get("improvement_pct")
        imp_str = f"{imp:.2f}%" if imp is not None else ""
        rows.append(
            f"<tr><td>{html.escape(r.get('id',''))}</td>"
            f"<td>{r.get('generation','')}</td>"
            f"<td>{html.escape(r.get('parent_id','') or '-')}</td>"
            f"<td>{html.escape(r.get('disposition',''))}</td>"
            f"<td>{r.get('summary',{}).get('median','')}</td>"
            f"<td>{html.escape(imp_str)}</td>"
            f"<td>{html.escape(r.get('hypothesis',''))}</td>"
            f"<td>{html.escape(r.get('change_summary',''))}</td></tr>"
        )

    lineage_html = build_lineage_tree(results)

    # Memory entries
    mem = load_memory()
    mem_html = ""
    if mem:
        mem_items = "\n".join(
            f'<li><strong>{html.escape(m.get("timestamp",""))}</strong>: {html.escape(m.get("insight",""))}</li>'
            for m in mem[-20:]  # Last 20 entries
        )
        mem_html = f'<section class="panel"><h2>Meta-Agent Memory (last 20)</h2><ul>{mem_items}</ul></section>'

    plateau = detect_plateau(results)
    velocity = improvement_velocity(results)
    status_note = ""
    if plateau:
        status_note = '<p style="color:#ef4444;font-weight:bold">⚠️ PLATEAU DETECTED — consider pivoting strategy or stopping</p>'
    if velocity is not None:
        status_note += f'<p>Improvement velocity (last 5 kept): {velocity:.2f}%</p>'

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Hyperagent: {html.escape(session.get("goal","session"))}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:24px auto;max-width:1100px;padding:0 20px 40px;color:#111827;background:#f8fafc}}
h1,h2,h3{{color:#0f172a}}
.summary-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0 24px}}
.summary-card{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;display:grid;gap:6px}}
.chart,.panel{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:18px}}
table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff}}
th,td{{border:1px solid #e5e7eb;padding:10px;text-align:left;vertical-align:top}}
th{{background:#eff6ff}}
.lineage{{font-family:monospace;font-size:13px;line-height:1.8}}
</style>
</head>
<body>
<h1>🧬 Hyperagent Report</h1>
<p><strong>Generated:</strong> {html.escape(now_utc_iso())}</p>
<p><strong>Goal:</strong> {html.escape(session.get("goal",""))}</p>
<p><strong>Task command:</strong> <code>{html.escape(session.get("task_command",""))}</code></p>
{status_note}

<div class="summary-grid">
<div class="summary-card"><strong>Metric</strong><span>{html.escape(metric_name)} ({html.escape(unit)}, {html.escape(direction)})</span></div>
<div class="summary-card"><strong>Generations</strong><span>{len(results)}</span></div>
<div class="summary-card"><strong>Kept</strong><span>{keep_count}</span></div>
<div class="summary-card"><strong>Discarded / Failed</strong><span>{discard_count} / {fail_count}</span></div>
<div class="summary-card"><strong>Threshold</strong><span>{session.get("min_improvement_pct",1.0)}%</span></div>
</div>

<section class="panel"><h2>Best Variant</h2>{best_html}</section>

{svg_line_chart(f"{metric_name} median by generation", medians, labels, unit)}
{svg_line_chart("Best-so-far trend", best_so_far, labels, unit)}
{svg_disposition_chart(results)}

<section class="panel lineage"><h2>Lineage Tree</h2>{lineage_html}</section>

{mem_html}

<section class="panel">
<h2>All Variants</h2>
<table>
<thead><tr><th>ID</th><th>Gen</th><th>Parent</th><th>Disposition</th><th>Median</th><th>Improvement</th><th>Hypothesis</th><th>Change</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
</section>
</body></html>"""

    atomic_write_text(path, report)
    return path
