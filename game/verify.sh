#!/usr/bin/env bash
# Verify the game instrument.
#
# Nine gates. Each one is required, and four of them exist specifically to
# catch the failure this package is about: a check that passes without having
# checked anything.
#
#   [5] axiom audit   — a proof that depends on `sorryAx` is a proof that does
#                       not exist. A proof that depends on `native_decide` is a
#                       proof about the compiler's evaluator, not about Lean's
#                       kernel. Both are named and both are refused.
#   [6] negative      — every control must fail to compile, and must fail
#                       because its proposition is refuted rather than because
#                       Lean could not elaborate the file. A control that fails
#                       for the wrong reason would still fail with the
#                       invariant deleted.
#   [7] determinism   — the committed money trace must regenerate byte-identically.
#   [8] language      — no new Python. The rule is mechanism, not intention.
#   [9] provenance    — game's six citations must agree with bds's six. This gate
#                       was added after five of six page numbers here turned out
#                       to be guesses. See tools/cross-check-findings.mjs.
#
# Usage: ./verify.sh  (exit 0 only if all nine gates pass)

set -euo pipefail

GAME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$GAME_DIR/.." && pwd)"

cd "$GAME_DIR"

TSC_BIN="${TSC_BIN:-../ledger/node_modules/.bin/tsc}"
if [ ! -x "$TSC_BIN" ]; then
  echo "FAIL: no TypeScript compiler at $TSC_BIN" >&2
  echo "      The toolchain is pinned to typescript 5.9.3 in package.json." >&2
  exit 1
fi

echo "[1/9] typecheck (strict, exactOptionalPropertyTypes, noUncheckedIndexedAccess)"
"$TSC_BIN" --noEmit

echo "[2/9] build"
"$TSC_BIN"

echo "[3/9] tests"
node --test dist/test/*.test.js

echo "[4/9] lean proofs — covenant and mechanism"
cd "$ROOT"
lean L5_COVENANT.lean
lean L6_GAME.lean

echo "[5/9] axiom audit (no sorryAx, no native_decide, no choice)"
OLEAN_DIR="$(mktemp -d)"
trap 'rm -rf "$OLEAN_DIR"' EXIT
lean -o "$OLEAN_DIR/L5_COVENANT.olean" L5_COVENANT.lean
lean -o "$OLEAN_DIR/L6_GAME.olean" L6_GAME.lean

AXIOM_LOG="$(mktemp)"
cat > "$AXIOM_LOG.src" <<'LEAN'
import «L5_COVENANT»
import «L6_GAME»
open Covenant Game
#print axioms substitution_required
#print axioms cheap_mercy_is_uninhabited
#print axioms ledger_ignores_report
#print axioms no_finite_excuse_chain_discharges
#print axioms excuse_forecloses_restitution
#print axioms grace_is_substitution
#print axioms no_rule_recovers_truth
#print axioms no_claim_is_a_baseline
#print axioms bond_without_detection_is_inert
#print axioms truthful_dominant_iff
#print axioms inversion_pays_iff
#print axioms stateless_cannot_escape
#print axioms zero_bearing_chain_is_unaccountable
#print axioms bearing_chain_has_a_bearing_member
LEAN
mv "$AXIOM_LOG.src" "$AXIOM_LOG"
LEAN_PATH="$OLEAN_DIR" lean "$AXIOM_LOG" > "$OLEAN_DIR/axioms.txt" 2>&1 || {
  echo "FAIL: axiom audit did not run:" >&2
  cat "$OLEAN_DIR/axioms.txt" >&2
  exit 1
}
if grep -qE 'sorryAx|ofReduceBool|Classical\.choice' "$OLEAN_DIR/axioms.txt"; then
  echo "FAIL: a new theorem depends on an axiom that is not permitted here:" >&2
  grep -E 'sorryAx|ofReduceBool|Classical\.choice' "$OLEAN_DIR/axioms.txt" >&2
  exit 1
fi
PERMITTED=0
while IFS= read -r line; do
  case "$line" in
    *"does not depend on any axioms"*) PERMITTED=$((PERMITTED+1)) ;;
    *"depends on axioms: [propext"*|*"depends on axioms: [Quot.sound"*|*"[propext, Quot.sound]"*) PERMITTED=$((PERMITTED+1)) ;;
    *) echo "FAIL: unexpected axiom line: $line" >&2; exit 1 ;;
  esac
done < "$OLEAN_DIR/axioms.txt"
if [ "$PERMITTED" -ne 14 ]; then
  echo "FAIL: expected 14 axiom reports, saw $PERMITTED" >&2
  cat "$OLEAN_DIR/axioms.txt" >&2
  exit 1
fi
echo "      14 theorems audited; only propext and Quot.sound appear"

echo "[6/9] negative controls (each must be rejected for its stated reason)"
rejected=0
for control in \
  game/negative/COVENANT_SUBSTITUTION_NOT_FORCED.lean \
  game/negative/COVENANT_CHEAP_MERCY.lean \
  game/negative/COVENANT_EXCUSE_DISCHARGES.lean \
  game/negative/GAME_TRUTH_RECOVERED.lean \
  game/negative/GAME_BOND_WITHOUT_DETECTION.lean \
  game/negative/GAME_STATELESS_ESCAPES.lean
do
  CONTROL_LOG="$(mktemp)"
  if LEAN_PATH="$OLEAN_DIR" lean "$control" > "$CONTROL_LOG" 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    rm -f "$CONTROL_LOG"
    exit 1
  fi
  if grep -qE 'failed to synthesize|unknown identifier|unknown constant|unknown module|unexpected token' "$CONTROL_LOG"; then
    echo "FAIL: $control was rejected for the wrong reason; it would fail even with its invariant removed:" >&2
    head -5 "$CONTROL_LOG" >&2
    rm -f "$CONTROL_LOG"
    exit 1
  fi
  rejected=$((rejected+1))
  rm -f "$CONTROL_LOG"
done
echo "      $rejected/6 controls rejected for their stated reasons"

echo "[7/9] determinism (same input twice, byte-identical output)"
# Gate 4 changed directory to the repo root for Lean. Return, or this gate
# runs a nonexistent binary and `set -e` swallows the reason.
cd "$GAME_DIR"
for CASE in \
  "settle --debt 10 --capacity 3 --violator 3 --other 7" \
  "money"
do
  DET_A="$(mktemp)"; DET_B="$(mktemp)"
  # shellcheck disable=SC2086
  node dist/src/cli.js $CASE > "$DET_A" 2>&1
  # shellcheck disable=SC2086
  node dist/src/cli.js $CASE > "$DET_B" 2>&1
  if ! cmp -s "$DET_A" "$DET_B"; then
    echo "FAIL: two identical invocations of \"$CASE\" produced different output" >&2
    diff "$DET_A" "$DET_B" >&2 || true
    rm -f "$DET_A" "$DET_B"
    exit 1
  fi
  rm -f "$DET_A" "$DET_B"
done
echo "      CLI output is reproducible byte-for-byte (settle, money)"

# The money trace is the artefact a reader inspects, so it is regenerated here
# and required to match the committed copy exactly. A trace that drifts from
# the committed one is either an unrecorded code change or an unrecorded
# finding, and both need a human to look.
TRACE="$GAME_DIR/../docs/traces/bds-money-trace.txt"
REGEN="$(mktemp)"
node dist/src/cli.js money > "$REGEN" 2>&1
if [ ! -f "$TRACE" ]; then
  echo "FAIL: committed trace missing at $TRACE" >&2
  rm -f "$REGEN"
  exit 1
fi
if ! cmp -s "$REGEN" "$TRACE"; then
  echo "FAIL: the money trace differs from the committed copy at" >&2
  echo "      $TRACE" >&2
  echo "      If the change is intended, regenerate and commit it:" >&2
  echo "        node dist/src/cli.js money > docs/traces/bds-money-trace.txt" >&2
  diff "$TRACE" "$REGEN" >&2 || true
  rm -f "$REGEN"
  exit 1
fi
rm -f "$REGEN"
echo "      money trace matches the committed artefact"

echo "[8/9] language gate (no new Python)"
BASELINE="$(git -C "$ROOT" rev-list --max-parents=0 HEAD 2>/dev/null | head -1 || true)"
# Count new .py files against the recorded arc baseline. Anything added after
# that commit must be justified in game/PYTHON_ALLOWLIST, and the allowlist is
# currently empty by design: the bound exception (cage/worker/infer.py) predates
# this gate and is therefore grandfathered, not exempted.
ALLOWLIST="$GAME_DIR/PYTHON_ALLOWLIST"
if [ ! -f "$ALLOWLIST" ]; then
  echo "FAIL: $ALLOWLIST is missing. An absent allowlist is not an empty one." >&2
  exit 1
fi
NEW_PY="$(git -C "$ROOT" diff --diff-filter=A --name-only eb6ada8f -- '*.py' 2>/dev/null || true)"
if [ -n "$NEW_PY" ]; then
  UNLISTED=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if ! grep -qxF "$f" "$ALLOWLIST"; then UNLISTED="$UNLISTED$f"$'\n'; fi
  done <<< "$NEW_PY"
  if [ -n "$UNLISTED" ]; then
    echo "FAIL: new Python files added since eb6ada8f and not on the allowlist:" >&2
    printf '%s' "$UNLISTED" >&2
    echo "      The rule is strict TypeScript for implementation. If a case is" >&2
    echo "      genuinely bound, name it in game/PYTHON_ALLOWLIST with its reason." >&2
    exit 1
  fi
fi
echo "      no unlisted Python added (baseline $BASELINE)"

echo "[9/9] provenance cross-check (game citations vs bds citations)"
node tools/cross-check-findings.mjs

echo "ALL GATES PASSED (9/9)"
