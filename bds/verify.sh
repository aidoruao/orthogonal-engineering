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

echo "[1/15] typecheck (strict, exactOptionalPropertyTypes, noUncheckedIndexedAccess)"
"$TSC_BIN" --noEmit

echo "[2/15] build + tests"
"$TSC_BIN"
node --test dist/test/*.test.js

echo "[3/15] lean proofs — labor conservation and jurisdiction"
cd "$ROOT"
lean L2_LABOR.lean
lean L3_JURISDICTION.lean

echo "[4/15] negative controls (each must be rejected for its stated reason)"
OLEAN_DIR="$(mktemp -d)"
lean -o "$OLEAN_DIR/L1_BURDEN.olean" L1_BURDEN.lean
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

echo "[5/15] TypeScript/Lean jurisdiction bridge (generated from the built gate)"
cd "$BDS_DIR"
JURIS_DIR="$(mktemp -d)"
cp "$OLEAN_DIR/L1_BURDEN.olean" "$JURIS_DIR/"
cp "$OLEAN_DIR/L3_JURISDICTION.olean" "$JURIS_DIR/"
node dist/tools/emit-jurisdiction.js > "$JURIS_DIR/TS_JURISDICTION.lean"
COMBOS="$(grep -c '^theorem ts_c' "$JURIS_DIR/TS_JURISDICTION.lean")"
if [ "$COMBOS" -ne 160 ]; then
  echo "FAIL: expected 160 generated combination theorems, found $COMBOS" >&2
  exit 1
fi
if ! ( cd "$JURIS_DIR" && LEAN_PATH="$JURIS_DIR" lean -o TS_JURISDICTION.olean TS_JURISDICTION.lean ); then
  echo "FAIL: the TypeScript gate and Lean's Righteous disagree (see the named combination above)" >&2
  exit 1
fi
cd "$ROOT"
if ! LEAN_PATH="$JURIS_DIR" lean L3_BURDEN_BRIDGE.lean; then
  echo "FAIL: the jurisdiction bridge did not compile against the generated table" >&2
  exit 1
fi
echo "OK: 160/160 combinations agree; bridge compiled"

cd "$BDS_DIR"
echo "[6/15] the specification's numbers, printed from the built code"
cd "$BDS_DIR"
node dist/src/cli.js figures > /dev/null
node dist/src/cli.js spec > /dev/null
echo "OK: figures and spec render"

echo "[7/15] the jurisdiction boundary is unrepresentable to cross"
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

echo "[8/15] fetched documents, if present on this machine"
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

echo "[9/15] the whole Lean surface compiles, not only this package's files"
# The IOW 1 attribution layer (L3_ATTRIBUTION, L3_FAMILY, L3_MODEL) was in no
# gate before this step existed. Files that name people were compiling and
# nothing checked them. This step makes the entire top-level Lean surface a
# gate obligation.
cd "$ROOT"
LEAN_OK=0
LEAN_FAIL=""
for f in *.lean; do
  case "$f" in
    L1_BURDEN_BRIDGE.lean|L3_BURDEN_BRIDGE.lean) continue ;;  # need generated tables; checked in step 5
  esac
  if lean "$f" > /dev/null 2>&1; then
    LEAN_OK=$((LEAN_OK + 1))
  else
    LEAN_FAIL="$LEAN_FAIL $f"
  fi
done
if [ -n "$LEAN_FAIL" ]; then
  echo "FAIL: these Lean files do not compile:$LEAN_FAIL" >&2
  exit 1
fi
echo "OK: $LEAN_OK Lean files compile (bridges checked separately)"

# The attribution layer must not rest on an undocumented trust assumption.
# `native_decide` is a trusted-executable axiom, not a kernel check; where it is
# used, the file has to say so in a specific phrase and point at the inventory.
#
# The phrase is matched exactly rather than by a fuzzy pattern, because a fuzzy
# pattern is satisfied by any file that merely mentions the compiler — which is
# how the first version of this check let a stripped disclosure pass.
if grep -ln 'native_decide' L3_*.lean > /tmp/native_users.txt 2>/dev/null; then
  while read -r f; do
    if ! grep -q 'trusted-executable assumption' "$f"; then
      echo "FAIL: $f uses native_decide without stating, in those words, that it is a trusted-executable assumption" >&2
      exit 1
    fi
    if ! grep -q 'TRUST_ASSUMPTIONS.md' "$f"; then
      echo "FAIL: $f does not point at docs/TRUST_ASSUMPTIONS.md" >&2
      exit 1
    fi
    echo "OK: $f discloses its native_decide assumption"
  done < /tmp/native_users.txt
else
  echo "OK: no Lean file uses native_decide"
fi

echo "[10/15] unproven obligations are declared, never silent"
# Unproven obligations must be declared, never silent.
SORRY_FILES=$(grep -l '\bsorry\b' *.lean 2>/dev/null | tr '\n' ' ')
if [ -n "$SORRY_FILES" ]; then
  for f in $SORRY_FILES; do
    if ! grep -qiE 'sorry.*(shape|unproved|unproven|tracked)|(shape|unproved|unproven|tracked).*sorry' "$f"; then
      echo "FAIL: $f contains sorry without declaring the unproved obligations" >&2
      exit 1
    fi
    echo "OK: $f declares its sorry obligations ($(grep -c '\bsorry\b' "$f") occurrences)"
  done
else
  echo "OK: no sorry in the Lean surface"
fi

cd "$BDS_DIR"
echo "[11/15] the audit findings render, and stay inside what the auditor said"
node dist/src/cli.js findings > /tmp/findings_out.txt
grep -q 'audit findings' /tmp/findings_out.txt || { echo "FAIL: findings did not render" >&2; exit 1; }
grep -q 'CONVERGENT, NOT PROVEN' /tmp/findings_out.txt || { echo "FAIL: the findings output does not label the inferential step" >&2; exit 1; }
grep -q 'WHAT THESE FINDINGS DO NOT ESTABLISH' /tmp/findings_out.txt || { echo "FAIL: the findings limits are missing" >&2; exit 1; }
if grep -qiE 'guilty|corrupt|fraud committed|embezzl' /tmp/findings_out.txt; then
  echo "FAIL: the findings output contains a verdict the auditor did not state" >&2
  exit 1
fi
COUNT=$(grep -cE '^    [0-9]{4}-[0-9]{3}  \[' /tmp/findings_out.txt)
if [ "$COUNT" -ne 6 ]; then
  echo "FAIL: expected 6 findings rendered, found $COUNT" >&2
  exit 1
fi
echo "OK: 6 findings render with limits and no verdict"

echo "[12/15] the attribution layer renders, and names only what it can support"
node dist/src/cli.js actors > /tmp/actors_out.txt
grep -q 'officials of record' /tmp/actors_out.txt || { echo "FAIL: actors did not render" >&2; exit 1; }
grep -q 'WHAT THIS LAYER CANNOT PRODUCE' /tmp/actors_out.txt || { echo "FAIL: the attribution limits are missing" >&2; exit 1; }
if grep -qiE 'guilty|corrupt|at fault|responsible for' /tmp/actors_out.txt; then
  echo "FAIL: the attribution output contains a verdict" >&2
  exit 1
fi
echo "OK: attribution renders with its limits and no verdict"

echo "[13/15] no Python in this instrument"
python_files="$(find . -path ./node_modules -prune -o -name '*.py' -print 2>/dev/null || true)"
if [ -n "$python_files" ]; then
  echo "FAIL: Python files found in bds/:" >&2
  echo "$python_files" >&2
  exit 1
fi
echo "OK: no Python files"

echo "[14/15] the schedule, not just the inequality (TLA+ / TLC)"
# L2_LABOR.lean proves an inequality about one allocation. It was being cited for
# a claim about a *schedule*, which is a temporal property. This runs TLC over
# the full reachable state space of a custodial schedule to check the stronger
# statement: completion is unreachable when unpaid labour is forbidden, and
# reachable when it is permitted.
set +e
tla/check.sh
TLA_EXIT=$?
set -e
case "$TLA_EXIT" in
  0) echo "OK: TLA+ schedule verified" ;;
  2) echo "WARNING: the TLA+ schedule check SKIPPED (see above)." >&2
     echo "         The schedule claim is therefore NOT verified in this run." >&2 ;;
  *) echo "FAIL: the TLA+ schedule check failed." >&2; exit 1 ;;
esac

echo "[15/15] no tracked L0 material and no untracked docket text"
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
