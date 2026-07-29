#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python "$ROOT/scripts/verify_release.py"
python -m compileall -q "$ROOT/analysis" "$ROOT/scripts" "$ROOT/validation" "$ROOT/tests"
echo "Static release verification passed."
