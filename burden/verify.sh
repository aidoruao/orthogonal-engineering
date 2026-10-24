#!/usr/bin/env bash
# Verify the burden inverter: types, tests, proofs, falsifiers, the TS/Lean bridge, determinism,
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

echo "[1/11] typecheck (strict, exactOptionalPropertyTypes, noUncheckedIndexedAccess)"
"$TSC_BIN" --noEmit

echo "[2/11] build + tests"
"$TSC_BIN"
node --test dist/test/*.test.js

echo "[3/11] lean proof"
cd "$ROOT"
lean L1_BURDEN.lean

echo "[4/11] negative controls (all must be rejected)"
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
  burden/negative/BURDEN_WEIGHT_COLLAPSE.lean \
  burden/negative/BURDEN_BRIDGE_DRIFT.lean
do
  if LEAN_PATH="$OLEAN_DIR" lean "$control" >/dev/null 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    exit 1
  fi
  rejected=$((rejected + 1))
  echo "OK: rejected $control"
done

if [ "$rejected" -ne 9 ]; then
  echo "FAIL: expected 9 negative controls, ran $rejected" >&2
  exit 1
fi

echo "[5/11] TypeScript/Lean bridge (generated tables must agree pair by pair)"
cd "$BURDEN_DIR"
BRIDGE_DIR="$(mktemp -d)"
cp "$OLEAN_DIR/L1_BURDEN.olean" "$BRIDGE_DIR/"
node dist/tools/emit-tables.js > "$BRIDGE_DIR/TS_TABLES.lean"
PAIRS="$(grep -c '^theorem ts_' "$BRIDGE_DIR/TS_TABLES.lean")"
if [ "$PAIRS" -ne 31 ]; then
  echo "FAIL: expected 31 generated pair theorems (25 tier + 6 weight), found $PAIRS" >&2
  exit 1
fi
if ! (cd "$BRIDGE_DIR" && LEAN_PATH="$BRIDGE_DIR" lean -o "$BRIDGE_DIR/TS_TABLES.olean" TS_TABLES.lean); then
  echo "FAIL: TypeScript and Lean disagree on at least one pair (see the error above)" >&2
  exit 1
fi
cd "$ROOT"
if ! LEAN_PATH="$BRIDGE_DIR" lean L1_BURDEN_BRIDGE.lean; then
  echo "FAIL: the bridge file did not compile against the generated tables" >&2
  exit 1
fi
echo "OK: 31/31 pairs agree; bridge compiled"

cd "$BURDEN_DIR"

echo "[6/11] determinism (same audit twice, byte-identical)"
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

echo "[7/11] ledger chain, anchored to a recorded head, and the last verdict reproduced"
LEDGER="ledger/receipts.jsonl"
HEAD_FILE="ledger/HEAD"
if [ ! -f "$LEDGER" ]; then
  echo "FAIL: no ledger at $LEDGER" >&2
  exit 1
fi
if [ ! -f "$HEAD_FILE" ]; then
  echo "FAIL: no recorded head at $HEAD_FILE" >&2
  echo "      A hash chain proves internal consistency, not completeness: deleting" >&2
  echo "      the last entry leaves a shorter chain that still verifies. The head" >&2
  echo "      must be recorded outside the ledger. Regenerate it with:" >&2
  echo "        node dist/src/cli.js head --ledger $LEDGER > $HEAD_FILE" >&2
  exit 1
fi
RECORDED_HEAD="$(tr -d '[:space:]' < "$HEAD_FILE")"
node dist/src/cli.js verify --ledger "$LEDGER" --expect-head "$RECORDED_HEAD"

# A truncated tail must now be detectable. Prove the anchor works rather than
# asserting it: drop the last line and require a non-zero exit.
TRUNCATED="$(mktemp)"
head -n -1 "$LEDGER" > "$TRUNCATED"
if node dist/src/cli.js verify --ledger "$TRUNCATED" --expect-head "$RECORDED_HEAD" >/dev/null 2>&1; then
  echo "FAIL: a truncated ledger still verified; the head anchor is not load-bearing" >&2
  rm -f "$TRUNCATED"
  exit 1
fi
rm -f "$TRUNCATED"
echo "OK: truncation is detected against the recorded head"

# Reproduce the last recorded verdict with its own falsifier command, and
# require the reproduced receipt to match the recorded one byte for byte on
# the fields the check is supposed to reproduce.
FALSIFIER="$(node -e 'const fs=require("fs");const lines=fs.readFileSync(process.argv[1],"utf8").trim().split("\n");const last=JSON.parse(lines[lines.length-1]);process.stdout.write(last.receipt.falsifier.command);' "$LEDGER")"
RECORDED_VERDICT="$(node -e 'const fs=require("fs");const lines=fs.readFileSync(process.argv[1],"utf8").trim().split("\n");const last=JSON.parse(lines[lines.length-1]);process.stdout.write(JSON.stringify([last.receipt.verdict.code,last.receipt.verdict.kind,last.receipt.tier,last.receipt.source&&last.receipt.source.sha256]));' "$LEDGER")"
SHIM_DIR="$(mktemp -d)"
printf '#!/usr/bin/env bash\nexec node "%s" "$@"\n' "$BURDEN_DIR/dist/src/cli.js" > "$SHIM_DIR/burden"
chmod +x "$SHIM_DIR/burden"
REPRODUCED="$(cd "$BURDEN_DIR" && PATH="$SHIM_DIR:$PATH" bash -c "$FALSIFIER" 2>/dev/null)"
if [ -z "$REPRODUCED" ]; then
  echo "FAIL: the recorded falsifier command produced no receipt:" >&2
  echo "  $FALSIFIER" >&2
  exit 1
fi
REPRODUCED_VERDICT="$(printf '%s' "$REPRODUCED" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const r=JSON.parse(s);process.stdout.write(JSON.stringify([r.verdict.code,r.verdict.kind,r.tier,r.source&&r.source.sha256]));});')"
if [ "$REPRODUCED_VERDICT" != "$RECORDED_VERDICT" ]; then
  echo "FAIL: the recorded falsifier no longer reproduces the recorded verdict" >&2
  echo "  recorded:   $RECORDED_VERDICT" >&2
  echo "  reproduced: $REPRODUCED_VERDICT" >&2
  echo "  command:    $FALSIFIER" >&2
  exit 1
fi
echo "OK: recorded falsifier reproduced the verdict: $RECORDED_VERDICT"

echo "[8/11] calibration (must never print a rate without a denominator)"
node dist/src/cli.js calibrate --ledger ledger/receipts.jsonl

echo "[9/11] adversarial-pattern scan self-test"
node dist/src/cli.js self-test

echo "[10/11] no Python in the new implementation"
python_files="$(find . -path ./node_modules -prune -o -name '*.py' -print 2>/dev/null || true)"
if [ -n "$python_files" ]; then
  echo "FAIL: Python files found in burden/:" >&2
  echo "$python_files" >&2
  exit 1
fi
echo "OK: no Python files"

echo "[11/11] no tracked node_modules under burden/"
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
