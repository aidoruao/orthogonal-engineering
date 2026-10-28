#!/usr/bin/env bash
# Verify the cage: TypeScript binds the process, Lean binds the gate.
set -euo pipefail
CAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$CAGE_DIR/.." && pwd)"
cd "$CAGE_DIR"
TSC_BIN="${TSC_BIN:-../ledger/node_modules/.bin/tsc}"
[ -x "$TSC_BIN" ] || { echo "FAIL: no tsc at $TSC_BIN" >&2; exit 1; }

echo "[1/6] typecheck (strict)"
"$TSC_BIN" --noEmit

echo "[2/6] build + gate tests (real subprocesses)"
"$TSC_BIN"
node --test dist/test/*.test.js

echo "[3/6] lean proof of the gate"
cd "$ROOT"
lean L4_CAGE.lean

echo "[4/6] the proof has no sorry and no trusted-compiler escape"
if grep -qE 'sorry|native_decide' L4_CAGE.lean; then
  echo "FAIL: L4_CAGE.lean contains sorry or native_decide" >&2
  exit 1
fi
echo "OK: L4_CAGE.lean is sorry-free and kernel-checked"

echo "[5/6] exactly one new Python file, and it is the registered worker"
cd "$CAGE_DIR"
py_files="$(find . -path ./node_modules -prune -o -name '*.py' -print 2>/dev/null | sort)"
expected="./worker/infer.py"
if [ "$py_files" != "$expected" ]; then
  echo "FAIL: expected exactly $expected, found:" >&2
  echo "$py_files" >&2
  exit 1
fi
echo "OK: one Python file, $expected"

# The worker must state its own untrusted status, or a future reader may mistake
# it for part of the proof layer.
for phrase in "It is not trusted" "not verified" "not part of the proof layer"; do
  grep -qF "$phrase" worker/infer.py || {
    echo "FAIL: worker/infer.py no longer states \"$phrase\"" >&2
    exit 1
  }
done
echo "OK: the worker states its own untrusted status"

echo "[6/6] the wire type cannot carry a verdict"
# L4_CAGE proves this structurally; this greps the runtime twin so a future edit
# adding a verdict field breaks the build here too.
if grep -nE 'verdict|admitted|isTrue|finding' src/protocol.ts | grep -vE '^\s*[0-9]+:\s*(//|\*|/\*)' | grep -q .; then
  echo "FAIL: src/protocol.ts mentions a verdict-shaped field outside a comment:" >&2
  grep -nE 'verdict|admitted|isTrue|finding' src/protocol.ts | grep -vE '^\s*[0-9]+:\s*(//|\*|/\*)' >&2
  exit 1
fi
echo "OK: no verdict-shaped wire field"

echo
echo "cage verified"
