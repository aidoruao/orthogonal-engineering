#!/usr/bin/env bash
# Verify the L1 ledger: types, tests, proof, and the falsifier.
#
# Every step is required. The last step is a negative control: a Lean file
# that must FAIL to compile. If it ever succeeds, the structural invariant is
# vacuous and this script fails the build.

set -euo pipefail

LEDGER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$LEDGER_DIR/.." && pwd)"

cd "$LEDGER_DIR"

echo "[1/5] typecheck (tsc --noEmit)"
npx tsc --noEmit

echo "[2/5] build + tests"
npx tsc
node --test dist/test/*.test.js

echo "[3/5] lean proof (L1_LEDGER.lean)"
cd "$ROOT"
lean L1_LEDGER.lean

echo "[4/5] negative control (must be rejected)"
TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

lean -o "$TMP_DIR/L1_LEDGER.olean" L1_LEDGER.lean

if LEAN_PATH="$TMP_DIR" lean "$LEDGER_DIR/negative/NEGATIVE_CONTROL.lean" >/dev/null 2>&1; then
  echo "FAIL: the negative control compiled. The invariant is vacuous." >&2
  exit 1
fi
echo "OK: negative control rejected, the invariant holds"

echo "[5/5] local corpus guard (L0 must not be tracked)"
cd "$ROOT"
tracked_raw="$(git ls-files 'evidence/fleites/*.pdf' 'evidence/fleites/*.txt' 'evidence/fleites/*.csv' 2>/dev/null || true)"
if [ -n "$tracked_raw" ]; then
  echo "FAIL: raw L0 material is tracked by git:" >&2
  echo "$tracked_raw" >&2
  exit 1
fi
echo "OK: no raw L0 material tracked"

echo
echo "ledger verified"
