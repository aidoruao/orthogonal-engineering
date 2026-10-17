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

echo "[1/4] typecheck (tsc --noEmit)"
npx tsc --noEmit

echo "[2/4] tests"
npx tsc
node --test dist/test/*.test.js

echo "[3/4] lean proof (L1_LEDGER.lean)"
cd "$ROOT"
lean L1_LEDGER.lean

echo "[4/4] negative control (must be rejected)"
TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

lean -o "$TMP_DIR/L1_LEDGER.olean" L1_LEDGER.lean

if LEAN_PATH="$TMP_DIR" lean "$LEDGER_DIR/negative/NEGATIVE_CONTROL.lean" >/dev/null 2>&1; then
  echo "FAIL: the negative control compiled. The invariant is vacuous." >&2
  exit 1
fi

echo "OK: negative control rejected, the invariant holds"
echo
echo "ledger verified"
