#!/usr/bin/env bash
# Verify the burden inverter: types, tests, proofs, falsifiers, determinism,
# ledger integrity, calibration, the detector's own falsifier, and the
# no-Python / no-tracked-node_modules boundaries.
#
# Every step is required. The negative controls must FAIL to compile; if any of
# them ever succeeds, the corresponding invariant is vacuous and this script
# fails the build.

set -euo pipefail

BURDEN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$BURDEN_DIR/.." && pwd)"

cd "$BURDEN_DIR"

TSC_BIN="${TSC_BIN:-../ledger/node_modules/.bin/tsc}"
if [ ! -x "$TSC_BIN" ]; then
  echo "FAIL: no TypeScript compiler at $TSC_BIN" >&2
  echo "      The toolchain is pinned to typescript 5.9.3 in package.json." >&2
  echo "      Install it in burden/ or point TSC_BIN at an existing tsc." >&2
  exit 1
fi

echo "[1/10] typecheck (strict, exactOptionalPropertyTypes, noUncheckedIndexedAccess)"
"$TSC_BIN" --noEmit

echo "[2/10] build + tests"
"$TSC_BIN"
node --test dist/test/*.test.js

echo "[3/10] lean proof"
cd "$ROOT"
lean L1_BURDEN.lean

echo "[4/10] negative controls (all must be rejected)"
OLEAN_DIR="$(mktemp -d)"
lean -o "$OLEAN_DIR/L1_BURDEN.olean" L1_BURDEN.lean

rejected=0
for control in \
  burden/negative/BURDEN_NO_FALSIFIER.lean \
  burden/negative/BURDEN_ANONYMOUS.lean \
  burden/negative/BURDEN_FALSIFIED_FETCHED.lean \
  burden/negative/BURDEN_SOURCELESS.lean \
  burden/negative/BURDEN_UNNAMED_GAP.lean \
  burden/negative/BURDEN_UPGRADE.lean \
  burden/negative/BURDEN_VACUOUS_RATE.lean \
  burden/negative/BURDEN_WEIGHT_COLLAPSE.lean
do
  if LEAN_PATH="$OLEAN_DIR" lean "$control" >/dev/null 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    exit 1
  fi
  rejected=$((rejected + 1))
  echo "OK: rejected $control"
done

if [ "$rejected" -ne 8 ]; then
  echo "FAIL: expected 8 negative controls, ran $rejected" >&2
  exit 1
fi

echo "[5/10] determinism (same audit twice, byte-identical)"
cd "$BURDEN_DIR"
PRECEDENT="$ROOT/The_Indictment_of_the_Watchers_Original_8-21-26.txt"
PRECEDENT_SHA="2764d1485a7c08133ae39510aff9eb277cf46b6f28cc1d2fa01e2558b6bb1499"
PRECEDENT_QUOTE="this file is the precedent of whatever taxonomy of objectives we are carrying out"
if [ -f "$PRECEDENT" ]; then
  node dist/src/cli.js audit \
    --id CLM-GATE-PRECEDENT-1 \
    --source "$PRECEDENT" \
    --quote "$PRECEDENT_QUOTE" \
    --sha256 "$PRECEDENT_SHA" \
    --bearing load_bearing \
    --actor verify-gate \
    > /tmp/burden-run-1.json 2>/dev/null
  node dist/src/cli.js audit \
    --id CLM-GATE-PRECEDENT-1 \
    --source "$PRECEDENT" \
    --quote "$PRECEDENT_QUOTE" \
    --sha256 "$PRECEDENT_SHA" \
    --bearing load_bearing \
    --actor verify-gate \
    > /tmp/burden-run-2.json 2>/dev/null
  if ! cmp -s /tmp/burden-run-1.json /tmp/burden-run-2.json; then
    echo "FAIL: two identical audits produced different bytes" >&2
    exit 1
  fi
  echo "OK: byte-identical across two runs"
else
  echo "SKIP: no indictment file at $PRECEDENT (determinism not exercised on the real corpus)"
fi

echo "[6/10] ledger chain, and the recorded falsifier reproduces the verdict"
node dist/src/cli.js verify --ledger ledger/receipts.jsonl
if [ -f ledger/receipts.jsonl ]; then
  FALSIFIER="$(node -e 'const fs=require("fs");const lines=fs.readFileSync("ledger/receipts.jsonl","utf8").trim().split("\n");const last=JSON.parse(lines[lines.length-1]);process.stdout.write(last.receipt.falsifier.command);')"
  SHIM_DIR="$(mktemp -d)"
  printf '#!/usr/bin/env bash\nexec node "%s" "$@"\n' "$BURDEN_DIR/dist/src/cli.js" > "$SHIM_DIR/burden"
  chmod +x "$SHIM_DIR/burden"
  if ! PATH="$SHIM_DIR:$PATH" bash -c "$FALSIFIER" > /dev/null 2>&1; then
    echo "FAIL: the recorded falsifier command did not reproduce the verdict:" >&2
    echo "  $FALSIFIER" >&2
    exit 1
  fi
  echo "OK: recorded falsifier reproduced the verdict"
fi

echo "[7/10] calibration (must never print a rate without a denominator)"
node dist/src/cli.js calibrate --ledger ledger/receipts.jsonl

echo "[8/10] adversarial-pattern scan self-test"
node dist/src/cli.js self-test

echo "[9/10] no Python in the new implementation"
python_files="$(find . -path ./node_modules -prune -o -name '*.py' -print 2>/dev/null || true)"
if [ -n "$python_files" ]; then
  echo "FAIL: Python files found in burden/:" >&2
  echo "$python_files" >&2
  exit 1
fi
echo "OK: no Python files"

echo "[10/10] no tracked node_modules under burden/"
cd "$ROOT"
tracked_modules="$(git ls-files 'burden/node_modules/*' 2>/dev/null || true)"
if [ -n "$tracked_modules" ]; then
  echo "FAIL: node_modules is tracked under burden/:" >&2
  echo "$tracked_modules" >&2
  exit 1
fi
echo "OK: node_modules is not tracked"

echo
echo "burden verified"
