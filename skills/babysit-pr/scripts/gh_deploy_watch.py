#!/usr/bin/env python3
"""Watch post-merge deployment signals for a GitHub pull request."""

import argparse
import calendar
import sys
import time

from gh_pr_watch import (
    FAILED_RUN_CONCLUSIONS,
    GhCommandError,
    gh_api_list_paginated,
    gh_json,
    get_workflow_runs_for_sha,
    print_event,
    print_json,
    resolve_pr,
)

DEPLOYMENT_SUCCESS_STATES = {"success"}
DEPLOYMENT_PENDING_STATES = {"queued", "in_progress", "pending", "requested", "waiting"}
DEPLOYMENT_FAILED_STATES = {"failure", "error", "inactive"}
DEPLOYMENT_WORKFLOW_KEYWORDS = (
    "deploy",
    "deployment",
    "release",
    "publish",
    "production",
    "prod",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Normalize post-merge deployment signals for Codex PR babysitting and "
            "emit a concise action recommendation."
        )
    )
    parser.add_argument("--pr", default="auto", help="auto, PR number, or PR URL")
    parser.add_argument("--repo", help="Optional OWNER/REPO override")
    parser.add_argument("--poll-seconds", type=int, default=60, help="Watch poll interval")
    parser.add_argument(
        "--signal-grace-seconds",
        type=int,
        default=900,
        help="How long to wait for deployment signals after merge before stopping",
    )
    parser.add_argument("--once", action="store_true", help="Emit one snapshot and exit")
    parser.add_argument("--watch", action="store_true", help="Continuously emit JSONL snapshots")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    args = parser.parse_args()
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be > 0")
    if args.signal_grace_seconds < 0:
        parser.error("--signal-grace-seconds must be >= 0")
    if not args.once and not args.watch:
        args.once = True
    return args


def deployment_workflow_name(run):
    return str(run.get("name") or run.get("display_title") or "")


def is_deployment_workflow(run):
    lower_name = deployment_workflow_name(run).lower()
    return any(keyword in lower_name for keyword in DEPLOYMENT_WORKFLOW_KEYWORDS)


def get_pull_details(repo, pr_number):
    payload = gh_json(["api", f"repos/{repo}/pulls/{pr_number}"], repo=repo)
    if not isinstance(payload, dict):
        raise GhCommandError("Unexpected payload from pulls API")
    return {
        "merged_at": str(payload.get("merged_at") or ""),
        "merge_commit_sha": str(payload.get("merge_commit_sha") or ""),
        "base_branch": str(((payload.get("base") or {}).get("ref")) or ""),
    }


def get_deployments_for_sha(repo, sha):
    if not sha:
        return []
    deployments = gh_api_list_paginated(f"repos/{repo}/deployments?sha={sha}", repo=repo)
    out = []
    for deployment in deployments:
        if not isinstance(deployment, dict):
            continue
        deployment_id = deployment.get("id")
        if deployment_id in (None, ""):
            continue
        statuses = gh_api_list_paginated(
            f"repos/{repo}/deployments/{deployment_id}/statuses",
            repo=repo,
        )
        latest_status = statuses[0] if statuses else {}
        out.append(
            {
                "deployment_id": deployment_id,
                "environment": str(
                    deployment.get("environment")
                    or deployment.get("original_environment")
                    or ""
                ),
                "state": str(latest_status.get("state") or "unknown"),
                "updated_at": str(latest_status.get("updated_at") or deployment.get("updated_at") or ""),
                "url": str(
                    latest_status.get("environment_url")
                    or latest_status.get("log_url")
                    or deployment.get("statuses_url")
                    or ""
                ),
            }
        )
    out.sort(key=lambda item: (item.get("updated_at") or "", str(item.get("deployment_id") or "")))
    return out


def get_deployment_workflows(repo, merge_commit_sha):
    runs = get_workflow_runs_for_sha(repo, merge_commit_sha)
    deployment_runs = []
    for run in runs:
        if not isinstance(run, dict) or not is_deployment_workflow(run):
            continue
        deployment_runs.append(
            {
                "run_id": run.get("id"),
                "workflow_name": deployment_workflow_name(run),
                "status": str(run.get("status") or ""),
                "conclusion": str(run.get("conclusion") or ""),
                "html_url": str(run.get("html_url") or ""),
            }
        )
    deployment_runs.sort(key=lambda item: (item.get("workflow_name") or "", str(item.get("run_id") or "")))
    return deployment_runs


def signal_counts(deployments, workflow_runs):
    pending = 0
    failed = 0
    success = 0

    for deployment in deployments:
        state = str(deployment.get("state") or "").lower()
        if state in DEPLOYMENT_PENDING_STATES:
            pending += 1
        elif state in DEPLOYMENT_FAILED_STATES:
            failed += 1
        elif state in DEPLOYMENT_SUCCESS_STATES:
            success += 1

    for run in workflow_runs:
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()
        if status and status != "completed":
            pending += 1
            continue
        if conclusion in FAILED_RUN_CONCLUSIONS:
            failed += 1
        elif conclusion == "success":
            success += 1

    return {
        "pending_count": pending,
        "failed_count": failed,
        "success_count": success,
        "signal_count": len(deployments) + len(workflow_runs),
    }


def recommend_actions(pr, details, counts, signal_grace_seconds):
    if not pr.get("merged") or not details.get("merged_at"):
        return ["stop_pr_not_merged"]

    if counts["failed_count"] > 0:
        return ["alert_deployment_failure"]
    if counts["pending_count"] > 0:
        return ["wait_deployment"]
    if counts["success_count"] > 0:
        return ["validate_production"]

    merged_at_epoch = None
    try:
        merged_at_epoch = calendar.timegm(time.strptime(details["merged_at"], "%Y-%m-%dT%H:%M:%SZ"))
    except (KeyError, TypeError, ValueError):
        merged_at_epoch = None

    if merged_at_epoch is not None and (time.time() - merged_at_epoch) < signal_grace_seconds:
        return ["wait_for_deployment_signal"]
    return ["no_deployment_signal"]


def collect_snapshot(args):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    details = get_pull_details(pr["repo"], pr["number"])
    deployments = get_deployments_for_sha(pr["repo"], details["merge_commit_sha"])
    workflow_runs = get_deployment_workflows(pr["repo"], details["merge_commit_sha"])
    counts = signal_counts(deployments, workflow_runs)
    actions = recommend_actions(pr, details, counts, args.signal_grace_seconds)
    return {
        "pr": {
            **pr,
            "merge_commit_sha": details["merge_commit_sha"],
            "base_branch": details["base_branch"],
            "merged_at": details["merged_at"],
        },
        "deployments": deployments,
        "deployment_workflows": workflow_runs,
        "signals": counts,
        "actions": actions,
    }


def snapshot_change_key(snapshot):
    pr = snapshot.get("pr") or {}
    signals = snapshot.get("signals") or {}
    return (
        str(pr.get("merge_commit_sha") or ""),
        int(signals.get("pending_count") or 0),
        int(signals.get("failed_count") or 0),
        int(signals.get("success_count") or 0),
        tuple(snapshot.get("actions") or []),
    )


def run_watch(args):
    last_change_key = None
    while True:
        snapshot = collect_snapshot(args)
        print_event(
            "snapshot",
            {
                "snapshot": snapshot,
                "next_poll_seconds": args.poll_seconds,
            },
        )
        actions = set(snapshot.get("actions") or [])
        if (
            "stop_pr_not_merged" in actions
            or "alert_deployment_failure" in actions
            or "validate_production" in actions
            or "no_deployment_signal" in actions
        ):
            print_event("stop", {"actions": snapshot.get("actions"), "pr": snapshot.get("pr")})
            return 0

        current_change_key = snapshot_change_key(snapshot)
        if current_change_key != last_change_key:
            last_change_key = current_change_key
        time.sleep(args.poll_seconds)


def main():
    args = parse_args()
    try:
        if args.watch:
            return run_watch(args)
        print_json(collect_snapshot(args))
        return 0
    except (GhCommandError, RuntimeError, ValueError) as err:
        print(f"gh_deploy_watch.py error: {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("gh_deploy_watch.py interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
