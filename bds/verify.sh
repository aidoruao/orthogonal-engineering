#!/usr/bin/env bash
# Verify the BDS instrument: types, tests, the labor proof, its falsifiers, the
# fetched-document figures, and the jurisdiction boundary.
#
# Every step is required. The negative controls must FAIL to compile, and each
# must fail because its proposition is refuted — not because Lean could not
# elaborate the file. A control that fails for the wrong reason would still fail
# with the invariant deleted, which is the opposite of a falsifier.

set -euo pipefail

BDS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$BDS_DIR/.." && pwd)"

cd "$BDS_DIR"

TSC_BIN="${TSC_BIN:-../ledger/node_modules/.bin/tsc}"
if [ ! -x "$TSC_BIN" ]; then
  echo "FAIL: no TypeScript compiler at $TSC_BIN" >&2
  echo "      The toolchain is pinned to typescript 5.9.3 in package.json." >&2
  exit 1
fi

echo "[1/9] typecheck (strict, exactOptionalPropertyTypes, noUncheckedIndexedAccess)"
"$TSC_BIN" --noEmit

echo "[2/9] build + tests"
"$TSC_BIN"
node --test dist/test/*.test.js

echo "[3/9] lean proofs — labor conservation and jurisdiction"
cd "$ROOT"
lean L2_LABOR.lean
lean L3_JURISDICTION.lean

echo "[4/9] negative controls (each must be rejected for its stated reason)"
OLEAN_DIR="$(mktemp -d)"
lean -o "$OLEAN_DIR/L2_LABOR.olean" L2_LABOR.lean
lean -o "$OLEAN_DIR/L3_JURISDICTION.olean" L3_JURISDICTION.lean

rejected=0
for control in \
  bds/negative/LABOR_LARGER_CAMPUS_LESS_DEMAND.lean \
  bds/negative/LABOR_PARTITION_EXCEEDS_TOTAL.lean \
  bds/negative/LABOR_ESCAPE_WITHOUT_UNPAID.lean \
  bds/negative/LABOR_FEASIBLE_AND_NOT.lean \
  bds/negative/JURISDICTION_MAY_CONDEMN.lean \
  bds/negative/JURISDICTION_FREE_EXCUSE.lean \
  bds/negative/JURISDICTION_INFLATED_IS_RIGHTEOUS.lean \
  bds/negative/JURISDICTION_UNFALSIFIABLE_IS_RIGHTEOUS.lean
do
  CONTROL_LOG="$(mktemp)"
  if LEAN_PATH="$OLEAN_DIR" lean "$control" > "$CONTROL_LOG" 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    exit 1
  fi
  if grep -qE 'failed to synthesize|unknown identifier|unknown constant|unknown module|unexpected token' "$CONTROL_LOG"; then
    echo "FAIL: $control was rejected for the wrong reason; it would fail even with its invariant removed:" >&2
    head -5 "$CONTROL_LOG" >&2
    exit 1
  fi
  rejected=$((rejected + 1))
  echo "OK: rejected $control"
done

if [ "$rejected" -ne 8 ]; then
  echo "FAIL: expected 8 negative controls, ran $rejected" >&2
  exit 1
fi

echo "[5/9] the specification's numbers, printed from the built code"
cd "$BDS_DIR"
node dist/src/cli.js figures > /dev/null
node dist/src/cli.js spec > /dev/null
echo "OK: figures and spec render"

echo "[6/9] the jurisdiction boundary is unrepresentable to cross"
# `Subject` has no condemnation member, so no finding can name one. Check the
# type union itself rather than the word: the source deliberately discusses
# condemnation in prose, to explain why the type excludes it. A quote-marked
# occurrence would mean a union member or a literal was added.
if grep -rn '"condemnation"' src/ > /dev/null 2>&1; then
  echo "FAIL: 'condemnation' appears as a string literal in src/; the boundary has been widened:" >&2
  grep -rn '"condemnation"' src/ >&2
  exit 1
fi
EXPECTED_SUBJECT='export type Subject = "structure" | "attribution";'
if ! grep -qF "$EXPECTED_SUBJECT" src/types.ts; then
  echo "FAIL: the Subject union is not the two fileable members:" >&2
  grep -n 'export type Subject' src/types.ts >&2
  exit 1
fi
echo "OK: Subject is exactly {structure, attribution}; no condemnation member"

echo "[7/9] fetched documents, if present on this machine"
CORPUS="$ROOT/evidence/bds"
if [ -d "$CORPUS" ] && [ -f "$CORPUS/19-10_Contract_Cleaning_Services.pdf" ]; then
  if [ -f "$CORPUS/MANIFEST.sha256" ]; then
    ( cd "$CORPUS" && sha256sum -c MANIFEST.sha256 )
    echo "OK: every fetched document matches its recorded hash"
  else
    echo "FAIL: documents are present but no MANIFEST.sha256 commits to them" >&2
    exit 1
  fi
else
  echo "SKIP: no fetched corpus at $CORPUS (hash verification not run)"
  echo "      Absence of the corpus is not evidence that the figures reproduce."
fi

echo "[8/9] no Python in this instrument"
python_files="$(find . -path ./node_modules -prune -o -name '*.py' -print 2>/dev/null || true)"
if [ -n "$python_files" ]; then
  echo "FAIL: Python files found in bds/:" >&2
  echo "$python_files" >&2
  exit 1
fi
echo "OK: no Python files"

echo "[9/9] no tracked L0 material and no untracked docket text"
cd "$ROOT"
tracked_raw="$(git ls-files 'evidence/bds/*.pdf' 'evidence/bds/*.txt' 'evidence/bds/*.csv' 2>/dev/null || true)"
if [ -n "$tracked_raw" ]; then
  echo "FAIL: raw fetched material is tracked by git:" >&2
  echo "$tracked_raw" >&2
  exit 1
fi
echo "OK: no raw fetched material tracked"

echo
echo "bds verified"
