#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Setup AutoPredict: clone, install, and run a minimal smoke test.

Usage:
  bash skills/autopredict/scripts/setup.sh [OPTIONS]

Options:
  --dir DIR         Installation directory (default: ./autopredict)
  --repo URL        Git remote to clone or verify
  --python BIN      Python executable to use (default: python3)
  --skip-smoke      Skip the sample backtest smoke test
  --help, -h        Show this help text
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

DIR="autopredict"
REPO_URL="https://github.com/howdymary/autopredict.git"
PYTHON_BIN="python3"
SKIP_SMOKE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)
      [[ $# -ge 2 ]] || die "--dir requires a value"
      DIR="$2"
      shift 2
      ;;
    --repo)
      [[ $# -ge 2 ]] || die "--repo requires a value"
      REPO_URL="$2"
      shift 2
      ;;
    --python)
      [[ $# -ge 2 ]] || die "--python requires a value"
      PYTHON_BIN="$2"
      shift 2
      ;;
    --skip-smoke)
      SKIP_SMOKE=true
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

need_cmd git
need_cmd "$PYTHON_BIN"

echo "=== AutoPredict Setup ==="
echo "Repo: $REPO_URL"
echo "Dir:  $DIR"
echo "Python: $("$PYTHON_BIN" --version 2>&1)"
echo

if [[ -e "$DIR" && ! -d "$DIR" ]]; then
  die "$DIR exists but is not a directory"
fi

if [[ -d "$DIR/.git" ]]; then
  echo "Existing git checkout detected. Verifying remote..."
  current_remote="$(git -C "$DIR" remote get-url origin 2>/dev/null || true)"
  if [[ -n "$current_remote" && "$current_remote" != "$REPO_URL" ]]; then
    die "$DIR points at origin $current_remote, expected $REPO_URL"
  fi
  if ! git -C "$DIR" pull --ff-only; then
    echo "Warning: git pull --ff-only failed. Leaving existing checkout in place." >&2
  fi
elif [[ -d "$DIR" ]]; then
  die "$DIR already exists but is not a git checkout"
else
  echo "Cloning AutoPredict..."
  git clone "$REPO_URL" "$DIR"
fi

[[ -f "$DIR/predict.py" ]] || die "$DIR does not look like an AutoPredict repo (missing predict.py)"
[[ -f "$DIR/autopredict/cli.py" ]] || die "$DIR does not look like an AutoPredict repo (missing autopredict/cli.py)"

cd "$DIR"

echo
echo "Installing in editable mode..."
runtime_python="$PYTHON_BIN"
if ! "$runtime_python" -m pip install -e .; then
  echo "Editable install failed. Falling back to a repo-local virtualenv..." >&2
  if [[ ! -d ".venv" ]]; then
    "$PYTHON_BIN" -m venv .venv
  fi
  runtime_python="$(pwd)/.venv/bin/python"
  "$runtime_python" -m pip install --upgrade pip
  "$runtime_python" -m pip install -e .
fi

echo
echo "Verifying import and command entrypoints..."
"$runtime_python" -c "import autopredict; print('autopredict import OK')"
"$runtime_python" predict.py --help >/dev/null
"$runtime_python" -m autopredict.cli --help >/dev/null

sample_dataset="autopredict/_defaults/datasets/sample_markets.json"
if [[ "$SKIP_SMOKE" == false ]]; then
  if [[ -f "$sample_dataset" ]]; then
    echo "Running smoke backtest with bundled sample dataset..."
    "$runtime_python" -m autopredict.cli backtest --dataset "$sample_dataset" >/dev/null
    echo "Smoke backtest OK"
  else
    echo "Warning: bundled sample dataset missing at $sample_dataset; skipped smoke test." >&2
  fi
fi

echo
echo "Setup complete."
echo
echo "Recommended next steps:"
echo "  cd $DIR"
echo "  $runtime_python predict.py --top 5 --verbose"
echo "  $runtime_python predict.py --events --top 10"
echo "  $runtime_python -m autopredict.cli backtest --dataset $sample_dataset"
echo
echo "Important caveats:"
echo "  - Always pass --dataset to autopredict.cli backtest; repo default_dataset is null."
echo "  - predict.py --fair uses the default AgentConfig, not strategy_configs/*.json."
echo "  - learn tune/improve and live trading are scaffolds in the current upstream repo."
