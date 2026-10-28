#!/usr/bin/env bash
# Check the TLA+ labor schedule model.
#
# Three runs, and the *pattern* of their results is the claim:
#
#   1. InfeasiblePaidOnly   demand > capacity, no unpaid labour
#                           -> NotComplete HOLDS. No interleaving completes.
#   2. InfeasibleWithUnpaid the same instance, unpaid labour permitted
#                           -> NotComplete VIOLATED. Completion reachable.
#   3. FeasiblePaidOnly     demand <= capacity, no unpaid labour
#                           -> NotComplete VIOLATED. Completion reachable.
#
# Run 3 exists to stop run 1 being vacuous: without it, a model in which
# completion is unreachable for any inputs would look identical to a correct
# one. Run 2 exists because the difference between it and run 1 is the
# dichotomy, and a dichotomy asserted without the second branch is a slogan.
#
# The only difference between runs 1 and 2 is the boolean `UnpaidAllowed`.

set -euo pipefail

TLA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$TLA_DIR"
TLA_VERSION=v1.7.1
TLA_JAR="${TLA_JAR:-$TLA_DIR/.tools/tla2tools.jar}"

# The jar is a 2.2 MB binary, so it is fetched on demand into a gitignored
# directory rather than committed. Pinned to a release tag and verified against
# a recorded hash: an unpinned download would make this check depend on whatever
# the network served that day.
TLA_SHA256="${TLA_SHA256:-d532ba31aafe17afba1130f92410d9257454ff7393d1eb2fe032f0c07f352da5}"

if [ ! -f "$TLA_JAR" ]; then
  mkdir -p "$(dirname "$TLA_JAR")"
  echo "fetching tla2tools.jar $TLA_VERSION ..." >&2
  if ! curl -sSfL -o "$TLA_JAR" \
      "https://github.com/tlaplus/tlaplus/releases/download/$TLA_VERSION/tla2tools.jar"; then
    echo "SKIP: could not fetch tla2tools.jar, and none is present locally" >&2
    echo "      A skip is reported, never counted as a pass." >&2
    rm -f "$TLA_JAR"
    exit 2
  fi
fi

if [ -n "$TLA_SHA256" ]; then
  actual="$(sha256sum "$TLA_JAR" | cut -d' ' -f1)"
  if [ "$actual" != "$TLA_SHA256" ]; then
    echo "FAIL: tla2tools.jar hash $actual does not match the pinned $TLA_SHA256" >&2
    exit 1
  fi
  echo "OK: tla2tools.jar matches the pinned hash"
fi

if [ ! -f "$TLA_JAR" ]; then
  echo "SKIP: no tla2tools.jar and none could be fetched" >&2
  exit 2
fi

run_tlc() {
  java -XX:+UseParallelGC -cp "$TLA_JAR" tlc2.TLC -config "$1" LaborSchedule.tla 2>&1
}

fail=0

# --- 1. Infeasible, paid only: completion must be unreachable ----------------
out1="$(run_tlc InfeasiblePaidOnly.cfg || true)"
if echo "$out1" | grep -q "No error has been found"; then
  states="$(echo "$out1" | grep -oE '[0-9]+ distinct states found' | head -1)"
  echo "OK: infeasible + paid-only -> completion unreachable ($states)"
else
  echo "FAIL: InfeasiblePaidOnly did not hold. Either the model admits paid" >&2
  echo "      completion when demand exceeds capacity, or TLC errored:" >&2
  echo "$out1" | tail -12 >&2
  fail=1
fi

# --- 2. Same instance with unpaid labour: completion must be reachable -------
out2="$(run_tlc InfeasibleWithUnpaid.cfg || true)"
if echo "$out2" | grep -q "Invariant NotComplete is violated"; then
  echo "OK: infeasible + unpaid allowed -> completion reachable (dichotomy branch 2)"
  # The violated state must actually carry unpaid minutes, or the completion was
  # reached some other way and this run does not demonstrate the dichotomy.
  if echo "$out2" | grep -qE 'unpaidTotal = [1-9]'; then
    echo "OK: the completing trace contains unpaid minutes"
  else
    echo "FAIL: completion was reached with unpaidTotal = 0, so this run does" >&2
    echo "      not demonstrate the unpaid-labour branch:" >&2
    echo "$out2" | grep -A 20 'behavior up to this point' | tail -14 >&2
    fail=1
  fi
else
  echo "FAIL: InfeasibleWithUnpaid did not reach completion. The dichotomy's" >&2
  echo "      second branch is then unexhibited:" >&2
  echo "$out2" | tail -12 >&2
  fail=1
fi

# --- 3. Feasible, paid only: completion must be reachable -------------------
out3="$(run_tlc FeasiblePaidOnly.cfg || true)"
if echo "$out3" | grep -q "Invariant NotComplete is violated"; then
  echo "OK: feasible + paid-only -> completion reachable (run 1 is not vacuous)"
  if echo "$out3" | grep -q 'unpaidTotal = 0'; then
    echo "OK: completion reached with zero unpaid minutes"
  else
    echo "FAIL: the feasible paid-only completion has unpaid minutes, which" >&2
    echo "      should be impossible in this model:" >&2
    echo "$out3" | grep -A 20 'behavior up to this point' | tail -14 >&2
    fail=1
  fi
else
  echo "FAIL: FeasiblePaidOnly did not reach completion. Either the model is" >&2
  echo "      broken or run 1 proves nothing, because completion is unreachable" >&2
  echo "      for every input:" >&2
  echo "$out3" | tail -12 >&2
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "TLA+ schedule verified: unreachable when unpaid forbidden, reachable when allowed"
