#!/usr/bin/env python3
"""Shared utilities for the autoresearch skill scripts."""

from __future__ import annotations

import csv
import html
import json
import math
import os
import shlex
import statistics
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARTIFACTS_DIRNAME = ".autoresearch"


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def artifacts_dir(cwd: Path | None = None) -> Path:
    return (cwd or Path.cwd()) / ARTIFACTS_DIRNAME


def ensure_artifacts_dir(cwd: Path | None = None) -> Path:
    path = artifacts_dir(cwd)
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "session.json"


def results_path(cwd: Path | None = None) -> Path:
    return artifacts_dir(cwd) / "results.jsonl"


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
            f"Session file not found at {path}. Run scripts/init_experiment.py first."
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


def default_checks_command(cwd: Path | None = None) -> str | None:
    command = (cwd or Path.cwd()) / "autoresearch.checks.sh"
    if command.exists():
        return "./autoresearch.checks.sh"
    return None


def parse_metric_lines(text: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("METRIC "):
            continue
        payload = line[len("METRIC ") :].strip()
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


def format_command_for_markdown(command: str) -> str:
    if "\n" in command:
        return command
    return shlex.join(shlex.split(command)) if command else ""


def coerce_float(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def write_results_csv(
    results: list[dict[str, Any]], output_path: Path | None = None
) -> Path:
    path = output_path or csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "timestamp",
        "baseline",
        "disposition",
        "checks",
        "metric_name",
        "median",
        "mean",
        "min",
        "max",
        "improvement_pct",
        "candidate_ref",
        "files_touched",
        "hypothesis",
        "change_summary",
        "measured_trials",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in results:
            summary = record.get("summary", {})
            writer.writerow(
                {
                    "id": record.get("id", ""),
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
                        str(value) for value in record.get("measured_trials", [])
                    ),
                }
            )
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

    def point_x(index: int) -> float:
        if len(values) == 1:
            return width / 2
        return padding + index * (width - (padding * 2)) / (len(values) - 1)

    def point_y(value: float) -> float:
        scale = (value - min_value) / (max_value - min_value)
        return height - padding - (scale * (height - (padding * 2)))

    points = " ".join(
        f"{point_x(index):.1f},{point_y(value):.1f}"
        for index, value in enumerate(values)
    )

    circles = "\n".join(
        (
            f"<circle cx=\"{point_x(index):.1f}\" cy=\"{point_y(value):.1f}\" "
            f"r=\"4\" fill=\"#2563eb\">"
            f"<title>{html.escape(labels[index])}: {value:.4f} {html.escape(unit)}</title>"
            "</circle>"
        )
        for index, value in enumerate(values)
    )

    grid_lines = "\n".join(
        (
            f"<line x1=\"{padding}\" y1=\"{y:.1f}\" x2=\"{width - padding}\" "
            f"y2=\"{y:.1f}\" stroke=\"#e5e7eb\" stroke-width=\"1\"/>"
        )
        for y in (
            padding,
            padding + ((height - (padding * 2)) / 2),
            height - padding,
        )
    )

    return f"""
<section class="chart">
  <h3>{html.escape(title)}</h3>
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">
    {grid_lines}
    <polyline fill="none" stroke="#2563eb" stroke-width="3" points="{points}" />
    {circles}
    <text x="{padding}" y="20" fill="#111827" font-size="12">{min_value:.4f} {html.escape(unit)}</text>
    <text x="{padding}" y="{height - 10}" fill="#111827" font-size="12">{max_value:.4f} {html.escape(unit)}</text>
  </svg>
</section>
""".strip()


def svg_disposition_chart(results: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for record in results:
        disposition = record.get("disposition", "unknown")
        counts[disposition] = counts.get(disposition, 0) + 1
    if not counts:
        return "<section><h3>Disposition counts</h3><p>No data yet.</p></section>"

    order = ["keep", "discard", "checks_failed", "crash"]
    items = [(name, counts[name]) for name in order if name in counts]
    width = 760
    height = 220
    padding = 40
    max_count = max(count for _, count in items)
    bar_width = 100
    gap = 60
    x = padding
    bars: list[str] = []
    for name, count in items:
        usable_height = height - (padding * 2)
        bar_height = 0 if max_count == 0 else (count / max_count) * usable_height
        y = height - padding - bar_height
        bars.append(
            (
                f"<rect x=\"{x}\" y=\"{y:.1f}\" width=\"{bar_width}\" "
                f"height=\"{bar_height:.1f}\" fill=\"#10b981\" rx=\"6\" />"
                f"<text x=\"{x + (bar_width / 2):.1f}\" y=\"{height - 12}\" "
                f"text-anchor=\"middle\" fill=\"#111827\" font-size=\"12\">{html.escape(name)}</text>"
                f"<text x=\"{x + (bar_width / 2):.1f}\" y=\"{max(20, y - 8):.1f}\" "
                f"text-anchor=\"middle\" fill=\"#111827\" font-size=\"12\">{count}</text>"
            )
        )
        x += bar_width + gap

    return f"""
<section class="chart">
  <h3>Disposition counts</h3>
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="Disposition counts">
    {' '.join(bars)}
  </svg>
</section>
""".strip()


def svg_trial_strip_chart(results: list[dict[str, Any]], unit: str) -> str:
    valid = [
        record
        for record in results
        if record.get("measured_trials") and record.get("disposition") != "crash"
    ]
    if not valid:
        return "<section><h3>Trial distribution</h3><p>No completed measurements yet.</p></section>"

    width = 820
    row_height = 28
    padding_left = 150
    padding_right = 40
    padding_top = 30
    height = padding_top + (row_height * len(valid)) + 30
    values = [
        value for record in valid for value in record.get("measured_trials", [])
    ]
    min_value = min(values)
    max_value = max(values)
    if math.isclose(min_value, max_value):
        min_value -= 1
        max_value += 1

    def point_x(value: float) -> float:
        scale = (value - min_value) / (max_value - min_value)
        usable_width = width - padding_left - padding_right
        return padding_left + (scale * usable_width)

    rows: list[str] = []
    for index, record in enumerate(valid):
        y = padding_top + (index * row_height)
        label = record.get("id", f"exp-{index + 1}")
        rows.append(
            f"<text x=\"12\" y=\"{y + 4}\" fill=\"#111827\" font-size=\"12\">{html.escape(label)}</text>"
        )
        rows.append(
            f"<line x1=\"{padding_left}\" y1=\"{y}\" x2=\"{width - padding_right}\" y2=\"{y}\" stroke=\"#e5e7eb\" />"
        )
        for value in record.get("measured_trials", []):
            rows.append(
                (
                    f"<circle cx=\"{point_x(value):.1f}\" cy=\"{y:.1f}\" r=\"4\" fill=\"#f59e0b\">"
                    f"<title>{html.escape(label)}: {value:.4f} {html.escape(unit)}</title>"
                    "</circle>"
                )
            )

    rows.append(
        f"<text x=\"{padding_left}\" y=\"{height - 8}\" fill=\"#111827\" font-size=\"12\">{min_value:.4f} {html.escape(unit)}</text>"
    )
    rows.append(
        f"<text x=\"{width - padding_right - 60}\" y=\"{height - 8}\" fill=\"#111827\" font-size=\"12\">{max_value:.4f} {html.escape(unit)}</text>"
    )

    return f"""
<section class="chart">
  <h3>Measured trial distribution</h3>
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="Measured trial distribution">
    {' '.join(rows)}
  </svg>
</section>
""".strip()


def render_html_report(
    session: dict[str, Any],
    results: list[dict[str, Any]],
    output_path: Path | None = None,
) -> Path:
    path = output_path or report_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    metric_name = session.get("metric_name", "metric")
    unit = session.get("unit", "")
    medians = [
        float(record.get("summary", {}).get("median"))
        for record in results
        if record.get("summary", {}).get("median") is not None
    ]
    labels = [record.get("id", "unknown") for record in results if record.get("summary")]

    best_so_far: list[float] = []
    current_best: float | None = None
    direction = session.get("direction", "lower")
    for value in medians:
        if current_best is None:
            current_best = value
        elif direction == "lower":
            current_best = min(current_best, value)
        else:
            current_best = max(current_best, value)
        best_so_far.append(current_best)

    keep_count = sum(1 for record in results if record.get("disposition") == "keep")
    discard_count = sum(
        1 for record in results if record.get("disposition") == "discard"
    )
    failure_count = sum(
        1
        for record in results
        if record.get("disposition") in {"checks_failed", "crash"}
    )

    best_record = None
    for record in results:
        if record.get("disposition") != "keep":
            continue
        if best_record is None:
            best_record = record
            continue
        candidate = record.get("summary", {}).get("median")
        incumbent = best_record.get("summary", {}).get("median")
        if candidate is None or incumbent is None:
            continue
        if direction == "lower" and candidate < incumbent:
            best_record = record
        if direction == "higher" and candidate > incumbent:
            best_record = record

    summary_cards = f"""
<div class="summary-grid">
  <div class="summary-card"><strong>Goal</strong><span>{html.escape(session.get("goal", "unknown"))}</span></div>
  <div class="summary-card"><strong>Metric</strong><span>{html.escape(metric_name)} ({html.escape(unit)})</span></div>
  <div class="summary-card"><strong>Threshold</strong><span>{session.get("min_improvement_pct", 1.0)}%</span></div>
  <div class="summary-card"><strong>Experiments</strong><span>{len(results)}</span></div>
  <div class="summary-card"><strong>Keeps</strong><span>{keep_count}</span></div>
  <div class="summary-card"><strong>Discards / Failures</strong><span>{discard_count} / {failure_count}</span></div>
</div>
""".strip()

    best_summary = "<p>No kept result yet.</p>"
    if best_record is not None:
        best_value = best_record.get("summary", {}).get("median")
        best_summary = (
            f"<p><strong>{html.escape(best_record.get('id', 'unknown'))}</strong> "
            f"at {best_value:.4f} {html.escape(unit)}"
        )
        if best_record.get("improvement_pct") is not None:
            best_summary += (
                f" ({best_record['improvement_pct']:.2f}% vs current baseline)"
            )
        best_summary += "</p>"

    row_fragments: list[str] = []
    for record in results:
        improvement = record.get("improvement_pct")
        if improvement is None:
            improvement_text = ""
        else:
            improvement_text = f"{improvement:.2f}%"
        row_fragments.append(
            (
                "<tr>"
                f"<td>{html.escape(record.get('id', ''))}</td>"
                f"<td>{html.escape(record.get('disposition', ''))}</td>"
                f"<td>{html.escape(record.get('checks', ''))}</td>"
                f"<td>{record.get('summary', {}).get('median', '')}</td>"
                f"<td>{html.escape(improvement_text)}</td>"
                f"<td>{html.escape(record.get('hypothesis', ''))}</td>"
                f"<td>{html.escape(record.get('change_summary', ''))}</td>"
                f"<td>{html.escape(', '.join(record.get('files_touched', [])))}</td>"
                "</tr>"
            )
        )
    table_rows = "\n".join(row_fragments)

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Autoresearch report: {html.escape(session.get("goal", "session"))}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 24px auto;
      max-width: 1100px;
      padding: 0 20px 40px;
      color: #111827;
      background: #f8fafc;
    }}
    h1, h2, h3 {{ color: #0f172a; }}
    code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 18px 0 24px;
    }}
    .summary-card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px;
      display: grid;
      gap: 6px;
    }}
    .chart, .panel {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      background: white;
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #eff6ff;
    }}
  </style>
</head>
<body>
  <h1>Autoresearch report</h1>
  <p><strong>Generated:</strong> {html.escape(now_utc_iso())}</p>
  <p><strong>Command:</strong> <code>{html.escape(session.get("command", ""))}</code></p>
  {summary_cards}
  <section class="panel">
    <h2>Best result</h2>
    {best_summary}
  </section>
  {svg_line_chart(f"{metric_name} median by experiment", medians, labels, unit)}
  {svg_line_chart("Best-so-far trend", best_so_far, labels, unit)}
  {svg_trial_strip_chart(results, unit)}
  {svg_disposition_chart(results)}
  <section class="panel">
    <h2>All experiments</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Disposition</th>
          <th>Checks</th>
          <th>Median</th>
          <th>Improvement</th>
          <th>Hypothesis</th>
          <th>Change summary</th>
          <th>Files touched</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </section>
</body>
</html>
"""
    atomic_write_text(path, report)
    return path
