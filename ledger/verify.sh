#!/usr/bin/env bash
# Verify the L1 ledger: types, tests, proofs, falsifiers, custody, census.
#
# Every step is required. The negative controls must FAIL to compile; if any
# of them ever succeeds, the corresponding invariant is vacuous and this
# script fails the build.

set -euo pipefail

LEDGER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$LEDGER_DIR/.." && pwd)"

cd "$LEDGER_DIR"

echo "[1/10] typecheck (tsc --noEmit)"
npx tsc --noEmit

echo "[2/10] build + tests"
npx tsc
node --test dist/test/*.test.js

echo "[3/10] lean proofs"
cd "$ROOT"
lean L1_LEDGER.lean
lean L1_SELECTION.lean
lean L1_GATES.lean

echo "[4/10] negative controls (all must be rejected)"
OLEAN_DIR="$(mktemp -d)"
cleanup() { rm -rf "$OLEAN_DIR"; }
trap cleanup EXIT

lean -o "$OLEAN_DIR/L1_LEDGER.olean" L1_LEDGER.lean
lean -o "$OLEAN_DIR/L1_SELECTION.olean" L1_SELECTION.lean
lean -o "$OLEAN_DIR/L1_GATES.olean" L1_GATES.lean

for control in \
  ledger/negative/NEGATIVE_CONTROL.lean \
  ledger/negative/SELECTION_DROP.lean \
  ledger/negative/SELECTION_ANONYMOUS.lean \
  ledger/negative/GATES_THEATRE.lean \
  ledger/negative/GATES_DOMINANCE.lean
do
  if LEAN_PATH="$OLEAN_DIR" lean "$control" >/dev/null 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    exit 1
  fi
  echo "OK: rejected $control"
done

echo "[5/10] local corpus guard (L0 must not be tracked)"
cd "$ROOT"
tracked_raw="$(git ls-files 'evidence/fleites/*.pdf' 'evidence/fleites/*.txt' 'evidence/fleites/*.csv' 2>/dev/null || true)"
if [ -n "$tracked_raw" ]; then
  echo "FAIL: raw L0 material is tracked by git:" >&2
  echo "$tracked_raw" >&2
  exit 1
fi
echo "OK: no raw L0 material tracked"

echo "[6/10] corpus custody (commitment vs disk)"
CORPUS_DIR="${OE_CORPUS_DIR:-$ROOT/evidence/fleites}"
if [ -f "$CORPUS_DIR/FLEITES_MANIFEST.sha256" ]; then
  node "$LEDGER_DIR/dist/src/corpus.js" \
    --manifest "$CORPUS_DIR/FLEITES_MANIFEST.sha256" \
    --sources "$CORPUS_DIR"
else
  echo "SKIP: no corpus at $CORPUS_DIR (custody not checked)"
fi

echo "[7/10] selection ledger (if one is published)"
CANDIDATES="$ROOT/ledger/candidates.jsonl"
SELECTION="$ROOT/ledger/selection.jsonl"
if [ -f "$CANDIDATES" ] && [ -f "$SELECTION" ]; then
  node "$LEDGER_DIR/dist/src/selection-check.js" \
    --candidates "$CANDIDATES" --ledger "$SELECTION"
elif [ -f "$SELECTION" ]; then
  echo "FAIL: selection.jsonl exists without candidates.jsonl; the selection cannot be audited" >&2
  exit 1
else
  echo "SKIP: no selection ledger yet (nothing has been drafted)"
fi

echo "[8/10] citation audit (published cites vs the documents)"
node "$LEDGER_DIR/dist/tools/cite-audit.js" --corpus "$CORPUS_DIR"

echo "[9/10] standards compliance (presence checks)"
node "$LEDGER_DIR/dist/src/compliance.js" --root "$ROOT"

echo "[10/10] territory census (declarations vs disk)"
# The census needs a declared tree and a root. Both are optional: with neither,
# it reports that it did not run rather than silently passing.
CENSUS_ROOT="${OE_CENSUS_ROOT:-}"
if [ -n "$CENSUS_ROOT" ] && [ -f "$CENSUS_ROOT/README.md" ]; then
  node "$LEDGER_DIR/dist/tools/census.js" declarations \
    --readme "$CENSUS_ROOT/README.md" \
    --root "$CENSUS_ROOT" \
    --strip-prefix "$(basename "$CENSUS_ROOT")" || {
      echo "NOTE: declaration divergence reported above. This is a finding, not a build failure," >&2
      echo "      unless OE_CENSUS_STRICT=1 is set." >&2
      if [ "${OE_CENSUS_STRICT:-0}" = "1" ]; then exit 1; fi
    }
else
  echo "SKIP: no OE_CENSUS_ROOT set; declaration audit not run"
fi

echo
echo "ledger verified"
