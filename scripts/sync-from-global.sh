#!/usr/bin/env bash
# Sync catalog skills in ./skills/ from the live source of truth at ~/.agents/skills.
#
# Default mode is a dry run: prints what would change, writes nothing.
#   --apply   actually perform the rsync
#   --all     also copy global-only skills into the catalog (excluding symlinks);
#             without it, only skills present in BOTH trees are synced
#
# Repo-only skills (present only in ./skills) are never touched.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_SKILLS="${HOME}/.agents/skills"
REPO_SKILLS="${REPO_ROOT}/skills"

APPLY=0
ALL=0
for arg in "$@"; do
  case "$arg" in
    --apply)   APPLY=1 ;;
    --all)     ALL=1 ;;
    --dry-run) APPLY=0 ;;
    *) echo "Unknown argument: $arg" >&2; echo "Usage: $0 [--dry-run|--apply] [--all]" >&2; exit 2 ;;
  esac
done

[[ -d "$GLOBAL_SKILLS" ]] || { echo "Global skills dir not found: $GLOBAL_SKILLS" >&2; exit 1; }
[[ -d "$REPO_SKILLS" ]]   || { echo "Repo skills dir not found: $REPO_SKILLS" >&2; exit 1; }

RSYNC_FLAGS=(-a --delete --itemize-changes)
if [[ $APPLY -eq 0 ]]; then
  RSYNC_FLAGS+=(--dry-run)
  echo "== DRY RUN (pass --apply to write) =="
else
  echo "== APPLY mode: writing changes =="
fi

synced=0
changed=0
added=0
skipped_repo_only=0
skipped_global_only=0

# Sync skills present in BOTH trees.
for dir in "$REPO_SKILLS"/*/; do
  name="$(basename "$dir")"
  if [[ -d "$GLOBAL_SKILLS/$name" ]]; then
    out="$(rsync "${RSYNC_FLAGS[@]}" "$GLOBAL_SKILLS/$name/" "$REPO_SKILLS/$name/")"
    synced=$((synced + 1))
    if [[ -n "$out" ]]; then
      changed=$((changed + 1))
      echo "-- $name (differs):"
      echo "$out" | sed 's/^/   /'
    fi
  else
    skipped_repo_only=$((skipped_repo_only + 1))
    echo "-- $name: repo-only, left untouched"
  fi
done

# Optionally copy global-only skills (excluding symlinked skill dirs).
for dir in "$GLOBAL_SKILLS"/*/; do
  name="$(basename "$dir")"
  [[ -d "$REPO_SKILLS/$name" ]] && continue
  if [[ -L "${dir%/}" ]]; then
    echo "-- $name: global-only symlink, skipped"
    continue
  fi
  if [[ $ALL -eq 1 ]]; then
    added=$((added + 1))
    echo "-- $name: NEW from global"
    rsync "${RSYNC_FLAGS[@]}" "$GLOBAL_SKILLS/$name/" "$REPO_SKILLS/$name/" | sed 's/^/   /'
  else
    skipped_global_only=$((skipped_global_only + 1))
  fi
done

echo
echo "== Summary =="
echo "Skills in both trees synced:   $synced ($changed with differences)"
echo "Repo-only skills untouched:    $skipped_repo_only"
if [[ $ALL -eq 1 ]]; then
  echo "Global-only skills added:      $added"
else
  echo "Global-only skills skipped:    $skipped_global_only (pass --all to copy)"
fi
if [[ $APPLY -eq 0 ]]; then
  echo "No files were written (dry run)."
fi
