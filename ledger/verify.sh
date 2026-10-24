#!/usr/bin/env bash
# Verify the L1 ledger: types, tests, proofs, falsifiers, custody, coverage.
#
# Every step is required. The negative controls must FAIL to compile; if any
# of them ever succeeds, the corresponding invariant is vacuous and this
# script fails the build.

set -euo pipefail

LEDGER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$LEDGER_DIR/.." && pwd)"

cd "$LEDGER_DIR"

echo "[1/12] typecheck (tsc --noEmit)"
npx tsc --noEmit

echo "[2/12] build + tests"
npx tsc
node --test dist/test/*.test.js

echo "[3/12] lean proofs"
cd "$ROOT"
lean L1_LEDGER.lean
lean L1_SELECTION.lean
lean L1_GATES.lean
lean L1_DECAY.lean
lean L1_COVERAGE.lean
lean L1_LIFELINE.lean
lean L1_NEGATIVITY.lean

echo "[4/12] negative controls (all must be rejected)"
OLEAN_DIR="$(mktemp -d)"
cleanup() { rm -rf "$OLEAN_DIR"; }
trap cleanup EXIT

lean -o "$OLEAN_DIR/L1_LEDGER.olean" L1_LEDGER.lean
lean -o "$OLEAN_DIR/L1_SELECTION.olean" L1_SELECTION.lean
lean -o "$OLEAN_DIR/L1_GATES.olean" L1_GATES.lean
lean -o "$OLEAN_DIR/L1_DECAY.olean" L1_DECAY.lean
lean -o "$OLEAN_DIR/L1_COVERAGE.olean" L1_COVERAGE.lean
lean -o "$OLEAN_DIR/L1_LIFELINE.olean" L1_LIFELINE.lean
lean -o "$OLEAN_DIR/L1_NEGATIVITY.olean" L1_NEGATIVITY.lean

for control in \
  ledger/negative/NEGATIVE_CONTROL.lean \
  ledger/negative/SELECTION_DROP.lean \
  ledger/negative/SELECTION_ANONYMOUS.lean \
  ledger/negative/GATES_THEATRE.lean \
  ledger/negative/GATES_DOMINANCE.lean \
  ledger/negative/DECAY_STALE.lean \
  ledger/negative/DECAY_STALE_FAIL.lean \
  ledger/negative/COVERAGE_WASTE.lean \
  ledger/negative/LIFELINE_OVERCLAIM.lean \
  ledger/negative/NEGATIVITY_FALLACY.lean
do
  if LEAN_PATH="$OLEAN_DIR" lean "$control" >/dev/null 2>&1; then
    echo "FAIL: $control compiled. Its invariant is vacuous." >&2
    exit 1
  fi
  echo "OK: rejected $control"
done

echo "[5/12] local corpus guard (L0 must not be tracked)"
cd "$ROOT"
tracked_raw="$(git ls-files 'evidence/fleites/*.pdf' 'evidence/fleites/*.txt' 'evidence/fleites/*.csv' 2>/dev/null || true)"
if [ -n "$tracked_raw" ]; then
  echo "FAIL: raw L0 material is tracked by git:" >&2
  echo "$tracked_raw" >&2
  exit 1
fi
echo "OK: no raw L0 material tracked"

echo "[6/12] corpus custody (commitment vs disk)"
CORPUS_DIR="${OE_CORPUS_DIR:-$ROOT/evidence/fleites}"
if [ -f "$CORPUS_DIR/FLEITES_MANIFEST.sha256" ]; then
  node "$LEDGER_DIR/dist/src/corpus.js" \
    --manifest "$CORPUS_DIR/FLEITES_MANIFEST.sha256" \
    --sources "$CORPUS_DIR"
else
  echo "SKIP: no corpus at $CORPUS_DIR (custody not checked)"
fi

echo "[7/12] claim coverage (documents examined vs claims held)"
CANDIDATES="$ROOT/ledger/candidates.jsonl"
SELECTION="$ROOT/ledger/selection.jsonl"
node "$LEDGER_DIR/dist/src/coverage.js" \
  --root "$ROOT" \
  --claims "$ROOT/ledger/drafts/verified.jsonl" \
  --manifest "$CORPUS_DIR/FLEITES_MANIFEST.sha256" || {
    echo "FAIL: coverage reported unbound claims or malformed records" >&2
    exit 1
  }
if [ ! -f "$ROOT/ledger/drafts/verified.jsonl" ]; then
  echo "NOTE: no drafts on this machine; coverage above is 0 claims by construction."
fi

echo "[8/12] selection ledger (if one is published)"
if [ -f "$CANDIDATES" ] && [ -f "$SELECTION" ]; then
  node "$LEDGER_DIR/dist/src/selection-check.js" \
    --candidates "$CANDIDATES" --ledger "$SELECTION"
elif [ -f "$SELECTION" ]; then
  echo "FAIL: selection.jsonl exists without candidates.jsonl; the selection cannot be audited" >&2
  exit 1
else
  echo "SKIP: no selection ledger yet (nothing has been published)"
fi

echo "[9/12] citation audit (published cites vs the documents)"
node "$LEDGER_DIR/dist/tools/cite-audit.js" --corpus "$CORPUS_DIR"

echo "[10/12] standards compliance (presence checks)"
node "$LEDGER_DIR/dist/src/compliance.js" --root "$ROOT"

echo "[11/12] territory census (declarations vs disk)"
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

echo "[12/12] verification freshness (environment vs recorded)"
node "$LEDGER_DIR/dist/src/freshness.js" --root "$ROOT"

echo
echo "ledger verified"
