#!/usr/bin/env bash
set -euo pipefail
# Setup AutoPredict: clone, install, and verify.
#
# Usage:
#   bash scripts/setup.sh [--dir /path/to/install]
#
# Options:
#   --dir DIR   Installation directory (default: ./autopredict)

DIR="autopredict"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --help|-h) echo "Usage: $0 [--dir DIR]"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

echo "=== AutoPredict Setup ==="

# Clone if not present
if [[ -d "$DIR" ]]; then
  echo "Directory $DIR already exists, pulling latest..."
  cd "$DIR"
  git pull --ff-only 2>/dev/null || echo "Pull failed (may have local changes), continuing..."
else
  echo "Cloning howdymary/autopredict into $DIR..."
  git clone https://github.com/howdymary/autopredict.git "$DIR"
  cd "$DIR"
fi

# Install
echo "Installing in editable mode..."
python3 -m pip install -e . --quiet 2>&1 | tail -3

# Verify
echo ""
echo "=== Verification ==="
python3 -c "
import sys
print(f'Python: {sys.version}')
try:
    import autopredict
    print('autopredict package: OK')
except ImportError:
    print('autopredict package: FAILED')
    sys.exit(1)
"

echo ""
echo "=== Quick test ==="
python3 predict.py --help 2>&1 | head -5

echo ""
echo "Setup complete. Directory: $(pwd)"
echo ""
echo "Next steps:"
echo "  python3 predict.py                    # Scan live markets"
echo "  python3 predict.py --events           # Find structural edges"
echo "  python3 predict.py --fair 0.60 <ID>   # Test your prediction"
