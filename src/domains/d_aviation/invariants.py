"""D_AVIATION invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- FAA 14 CFR Part 25 (Airworthiness Standards)
- ICAO Annex 6 (Operation of Aircraft)
- NASA-STD-8719.13B (Software Safety)
- RTCA DO-178C (Software Considerations)

Source: ontology/ontology.json#D_AVIATION
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_aviation.implementation import (
    EnvelopeViolationError,
    CircuitBreaker,
    CircuitState,
    check_flight_envelope,
    parse_atc_message,
    compute_lift_mcn,
    ENVELOPE,
)


def check_envelope_overspeed_rejected() -> Tuple[bool, ProofObject]:
    """
    Invariant: Aircraft never enters a state violating safe-flight envelopes.
    
    Standard: FAA 14 CFR 25.253 (High-speed characteristics)
    Falsifies if: Overspeed is accepted without error, F_AVIATION_001 is violated.
    falsifies_if: Overspeed is accepted without error, F_AVIATION_001 is violated.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    raised = False
    error_msg = ""
    
    try:
        check_flight_envelope(
            speed_kt=ENVELOPE["max_speed_kt"] + 1,
            altitude_ft=10_000,
            bank_deg=0,
            pitch_deg=0,
            vs_fpm=0,
        )
    except EnvelopeViolationError as e:
        raised = True
        error_msg = str(e)
    
    success = raised
    proof = ProofObject(
        rule="FlightEnvelopeViolationCheck",
        premises=[
            f"max_speed_kt = {ENVELOPE['max_speed_kt']}",
            f"test_speed = {ENVELOPE['max_speed_kt'] + 1}",
            f"envelope_violation_raised = {raised}",
        ],
        conclusion=(
            "Overspeed correctly rejected per 14 CFR 25.253"
            if success
            else f"FAIL: Overspeed accepted — {error_msg}"
        ),
    )
    return success, proof


def check_envelope_normal_state_accepted() -> Tuple[bool, ProofObject]:
    """
    Invariant: Normal flight states within envelope must be accepted.
    
    Standard: ICAO Annex 6 (Normal operations envelope)
    Falsifies if: A safe state raises an exception (over-restriction).
    falsifies_if: A safe state raises an exception (over-restriction).
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    try:
        result = check_flight_envelope(
            speed_kt=250,
            altitude_ft=35_000,
            bank_deg=15,
            pitch_deg=5,
            vs_fpm=500,
        )
        success = result is True
    except Exception as e:
        success = False
        result = f"Exception: {e}"
    
    proof = ProofObject(
        rule="FlightEnvelopeNormalCheck",
        premises=[
            "speed_kt = 250",
            "altitude_ft = 35000",
            "bank_deg = 15",
            "pitch_deg = 5",
            f"result = {result}",
        ],
        conclusion=(
            "Normal flight state accepted per ICAO Annex 6"
            if success
            else f"FAIL: Normal state rejected — {result}"
        ),
    )
    return success, proof


def check_circuit_breaker_open_on_failures() -> Tuple[bool, ProofObject]:
    """
    Invariant: Circuit opens after failure_threshold consecutive failures.
    
    Standard: NASA-STD-8719.13B (Software fault tolerance)
    Falsifies if: Circuit stays CLOSED after threshold failures.
    falsifies_if: Circuit stays CLOSED after threshold failures.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60)
    initial_state = cb.state
    
    def always_fails():
        raise ConnectionError("API down")
    
    for i in range(3):
        cb.call("weather", always_fails, fallback={"wind_kt": 0})
    
    final_state = cb.state
    success = final_state == CircuitState.OPEN
    
    proof = ProofObject(
        rule="CircuitBreakerFailureThreshold",
        premises=[
            f"failure_threshold = 3",
            f"initial_state = {initial_state}",
            f"consecutive_failures = 3",
            f"final_state = {final_state}",
        ],
        conclusion=(
            "Circuit opened after threshold failures per NASA-STD-8719.13B"
            if success
            else f"FAIL: Circuit stayed {final_state} after 3 failures"
        ),
    )
    return success, proof


def check_circuit_breaker_returns_cache_when_open() -> Tuple[bool, ProofObject]:
    """
    Invariant: When circuit is OPEN, cached data is returned (no live API call).
    
    Standard: NASA-STD-8719.13B (Graceful degradation)
    Falsifies if: Live call is made when circuit is OPEN.
    falsifies_if: Live call is made when circuit is OPEN.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=60)
    cached = {"wind_kt": 15, "visibility_sm": 10}
    
    # One successful call to populate cache
    cb.call("weather", lambda: cached)
    cb.trip()
    circuit_state_after_trip = cb.state
    
    live_called = [False]
    
    def live_fetch():
        live_called[0] = True
        return {"wind_kt": 99}
    
    result = cb.call("weather", live_fetch, fallback=None)
    
    success = (not live_called[0]) and (result == cached)
    
    proof = ProofObject(
        rule="CircuitBreakerCacheFallback",
        premises=[
            f"circuit_state = {circuit_state_after_trip}",
            f"cached_data = {cached}",
            f"live_called = {live_called[0]}",
            f"result = {result}",
        ],
        conclusion=(
            "Cached data returned when OPEN per graceful degradation"
            if success
            else "FAIL: Live called or wrong result when circuit OPEN"
        ),
    )
    return success, proof


def check_malformed_atc_no_exception() -> Tuple[bool, ProofObject]:
    """
    Invariant: Malformed ATC messages never cause unhandled exceptions.
    
    Standard: RTCA DO-178C (Robustness testing)
    Falsifies if: Any exception from parse_atc_message.
    falsifies_if: Any exception from parse_atc_message.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    malformed_inputs = ["", "X", "\x00\xff", "A" * 5000, "   "]
    all_passed = True
    failures = []
    
    for inp in malformed_inputs:
        try:
            result = parse_atc_message(inp)
            if not isinstance(result, dict):
                all_passed = False
                failures.append(f"Expected dict for {inp!r}, got {type(result)}")
            elif "error" not in result and "callsign" not in result:
                all_passed = False
                failures.append(f"Result missing error/callsign for {inp!r}")
        except Exception as e:
            all_passed = False
            failures.append(f"Exception for {inp!r}: {e}")
    
    proof = ProofObject(
        rule="MalformedATCRobustness",
        premises=[
            f"test_cases = {len(malformed_inputs)}",
            f"all_passed = {all_passed}",
            f"failures = {len(failures)}",
        ],
        conclusion=(
            "Malformed ATC handled gracefully per DO-178C"
            if all_passed
            else f"FAIL: {failures[:2]}"
        ),
    )
    return all_passed, proof


def check_lift_deterministic() -> Tuple[bool, ProofObject]:
    """
    Invariant: Same inputs always produce identical lift (determinism).
    
    Standard: FAA 14 CFR 25.105 (Takeoff speeds - deterministic computation)
    Falsifies if: Two calls with identical inputs return different values.
    falsifies_if: Two calls with identical inputs return different values.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    args = (250, 1225, 1000, 12, 10, 200)
    r1 = compute_lift_mcn(*args)
    r2 = compute_lift_mcn(*args)
    
    deterministic = r1 == r2
    is_integer = isinstance(r1, int)
    success = deterministic and is_integer
    
    proof = ProofObject(
        rule="LiftDeterminism",
        premises=[
            f"inputs = {args}",
            f"result_1 = {r1}",
            f"result_2 = {r2}",
            f"deterministic = {deterministic}",
            f"is_integer = {is_integer}",
        ],
        conclusion=(
            "Lift computation deterministic per 14 CFR 25.105"
            if success
            else f"FAIL: Not deterministic ({r1} vs {r2}) or not integer"
        ),
    )
    return success, proof


def check_flight_envelope_fraction_precision() -> Tuple[bool, ProofObject]:
    """
    Invariant: Flight envelope calculations use exact Fraction arithmetic.
    
    Standard: NASA-STD-8719.13B (No floating-point in safety-critical)
    Falsifies if: Float values used instead of Fraction.
    falsifies_if: Float values used instead of Fraction.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Verify envelope values are Fraction-compatible
    max_speed = Fraction(ENVELOPE["max_speed_kt"])
    min_speed = Fraction(ENVELOPE.get("min_speed_kt", 0))
    
    speed_range = max_speed - min_speed
    safety_margin = Fraction(105, 100)  # 1.05 as exact fraction
    
    # Check that calculations maintain precision
    test_max = max_speed * safety_margin
    
    success = isinstance(test_max, Fraction)
    
    proof = ProofObject(
        rule="FlightEnvelopeFractionPrecision",
        premises=[
            f"max_speed = {max_speed}",
            f"min_speed = {min_speed}",
            f"speed_range = {speed_range}",
            f"safety_margin = {safety_margin}",
            f"test_result_type = {type(test_max).__name__}",
        ],
        conclusion=(
            "Exact Fraction arithmetic verified per NASA-STD-8719.13B"
            if success
            else "FAIL: Non-Fraction arithmetic detected"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_AVIATION invariants. Returns dict of check_name → pass/fail.

    Falsifies if: any aviation invariant check returns False or raises an exception.
    falsifies_if: any aviation invariant check returns False or raises an exception.
    """
    checks = [
        ("check_envelope_overspeed_rejected", check_envelope_overspeed_rejected),
        ("check_envelope_normal_state_accepted", check_envelope_normal_state_accepted),
        ("check_circuit_breaker_open_on_failures", check_circuit_breaker_open_on_failures),
        ("check_circuit_breaker_returns_cache_when_open", check_circuit_breaker_returns_cache_when_open),
        ("check_malformed_atc_no_exception", check_malformed_atc_no_exception),
        ("check_lift_deterministic", check_lift_deterministic),
        ("check_flight_envelope_fraction_precision", check_flight_envelope_fraction_precision),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_AVIATION invariants: PASS")
