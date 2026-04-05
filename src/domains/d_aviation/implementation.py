"""
D_AVIATION — Aviation & ATC domain implementation.
External API circuit-breakers and safe-flight envelope enforcement.

Invariants (from ontology/ontology.json#D_AVIATION):
  1. Aircraft never enters a state that violates known safe-flight envelopes.
  2. External weather/ATC API failures are circuit-broken; cached data is used instead.
  3. ATC messages with invalid format are rejected without crashing the parser.

Biblical inspiration: "The prudent see danger and take refuge, but the simple keep going
and pay the penalty." (Proverbs 22:3)
A circuit-breaker is the prudent refuge: when an external API signal is unreliable,
the system does not blindly continue — it shelters behind cached state and alerts the crew.

Falsification IDs: F_AVIATION_001, F_AVIATION_002, F_AVIATION_003, F_AVIATION_004
"""

from __future__ import annotations

import time
from fractions import Fraction
from typing import Any, Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Safe-flight envelope enforcement (F_AVIATION_001)
# ---------------------------------------------------------------------------

class EnvelopeViolationError(Exception):
    """Raised when a computed flight state would exceed a safe-flight envelope limit."""


# Safe-flight envelope limits (all integer or Fraction for exactness)
ENVELOPE = {
    "max_speed_kt": 350,             # Maximum operating speed in knots
    "min_speed_kt": 60,              # Minimum speed (stall boundary)
    "max_altitude_ft": 45_000,       # Service ceiling
    "min_altitude_ft": 0,            # Ground level
    "max_bank_deg": 67,              # Maximum bank angle
    "max_pitch_up_deg": 30,          # Maximum nose-up pitch
    "max_pitch_down_deg": -20,       # Maximum nose-down pitch
    "max_vs_fpm": 6000,              # Maximum vertical speed (fpm)
    "min_vs_fpm": -6000,             # Maximum descent rate (fpm)
}


def check_flight_envelope(
    speed_kt: int,
    altitude_ft: int,
    bank_deg: int,
    pitch_deg: int,
    vs_fpm: int,
) -> bool:
    """
    Verify that the given flight state is within the safe-flight envelope.

    Invariant: No flight state that violates envelope limits may be accepted.
    Falsification: If a state outside any envelope limit is returned without error,
    F_AVIATION_001 is violated.

    Args:
        speed_kt:    Current airspeed in knots (integer).
        altitude_ft: Pressure altitude in feet (integer).
        bank_deg:    Bank angle in degrees (integer, positive = right).
        pitch_deg:   Pitch angle in degrees (positive = up).
        vs_fpm:      Vertical speed in feet per minute.

    Returns:
        True if all limits are satisfied.

    Raises:
        EnvelopeViolationError: If any parameter exceeds its safe limit.
        ValueError: If any input is not an integer.
    """
    for name, val in [
        ("speed_kt", speed_kt),
        ("altitude_ft", altitude_ft),
        ("bank_deg", bank_deg),
        ("pitch_deg", pitch_deg),
        ("vs_fpm", vs_fpm),
    ]:
        if not isinstance(val, int):
            raise ValueError(f"{name} must be int, got {type(val).__name__}")

    violations = []
    if speed_kt > ENVELOPE["max_speed_kt"]:
        violations.append(f"speed {speed_kt} kt > max {ENVELOPE['max_speed_kt']} kt")
    if speed_kt < ENVELOPE["min_speed_kt"]:
        violations.append(f"speed {speed_kt} kt < min {ENVELOPE['min_speed_kt']} kt")
    if altitude_ft > ENVELOPE["max_altitude_ft"]:
        violations.append(f"altitude {altitude_ft} ft > max {ENVELOPE['max_altitude_ft']} ft")
    if altitude_ft < ENVELOPE["min_altitude_ft"]:
        violations.append(f"altitude {altitude_ft} ft < min {ENVELOPE['min_altitude_ft']} ft")
    if abs(bank_deg) > ENVELOPE["max_bank_deg"]:
        violations.append(f"bank {bank_deg} deg exceeds ±{ENVELOPE['max_bank_deg']} deg")
    if pitch_deg > ENVELOPE["max_pitch_up_deg"]:
        violations.append(f"pitch {pitch_deg} deg > max {ENVELOPE['max_pitch_up_deg']} deg")
    if pitch_deg < ENVELOPE["max_pitch_down_deg"]:
        violations.append(f"pitch {pitch_deg} deg < min {ENVELOPE['max_pitch_down_deg']} deg")
    if vs_fpm > ENVELOPE["max_vs_fpm"]:
        violations.append(f"vs {vs_fpm} fpm > max {ENVELOPE['max_vs_fpm']} fpm")
    if vs_fpm < ENVELOPE["min_vs_fpm"]:
        violations.append(f"vs {vs_fpm} fpm < min {ENVELOPE['min_vs_fpm']} fpm")

    if violations:
        raise EnvelopeViolationError(
            "Safe-flight envelope violated — F_AVIATION_001: " + "; ".join(violations)
        )
    return True


# ---------------------------------------------------------------------------
# Circuit breaker for external APIs (F_AVIATION_004)
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"       # Normal: requests pass through
    OPEN = "open"           # Tripped: requests fail fast, return cached data
    HALF_OPEN = "half_open" # Testing: one probe request allowed


class CircuitBreaker:
    """
    Circuit breaker for external weather/ATC data APIs.

    Invariant: When the circuit is OPEN, no real API call is made;
    cached data is returned immediately.
    Falsification: If a real API call is attempted while circuit is OPEN,
    F_AVIATION_004 is violated.

    Parameters:
        failure_threshold: Number of consecutive failures to open the circuit.
        recovery_timeout_s: Seconds before transitioning OPEN → HALF_OPEN.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_s: int = 30,
    ):
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout_s < 1:
            raise ValueError("recovery_timeout_s must be >= 1")
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: Optional[float] = None
        self._cache: dict[str, Any] = {}

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.monotonic() - self._opened_at
            if elapsed >= self.recovery_timeout_s:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, key: str, fetch_fn, fallback: Any = None) -> Any:
        """
        Invoke fetch_fn if circuit is CLOSED or HALF_OPEN; return cached value if OPEN.

        Args:
            key:       Cache key for this data source.
            fetch_fn:  Zero-argument callable that fetches live data.
            fallback:  Value to return if circuit is OPEN and no cache exists.

        Returns:
            Fresh data (CLOSED/HALF_OPEN) or cached data (OPEN).
        """
        current_state = self.state

        if current_state == CircuitState.OPEN:
            return self._cache.get(key, fallback)

        try:
            result = fetch_fn()
            self._cache[key] = result
            if current_state == CircuitState.HALF_OPEN:
                # Successful probe — close the circuit
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._opened_at = None
            else:
                self._failure_count = 0
            return result
        except Exception:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()
            return self._cache.get(key, fallback)

    def trip(self) -> None:
        """Manually open the circuit (e.g., for testing or known outage)."""
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()

    def reset(self) -> None:
        """Reset circuit to CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None


# ---------------------------------------------------------------------------
# ATC message parser (F_AVIATION_002)
# ---------------------------------------------------------------------------

def parse_atc_message(msg: str) -> dict:
    """
    Parse an ATC message string into a structured dict.

    Invariant: Malformed messages are rejected gracefully — no exceptions escape.
    Falsification: If any input causes an unhandled exception, F_AVIATION_002 is violated.

    Returns a dict with 'error' key on invalid input, or structured fields on success.
    """
    if not isinstance(msg, str):
        return {"error": "not_string"}
    stripped = msg.strip()
    if len(stripped) < 3:
        return {"error": "too_short", "raw": msg[:50]}
    # Guard against extremely large messages (DoS protection)
    if len(stripped) > 2000:
        return {"error": "too_long"}
    parts = stripped.split()
    if not parts:
        return {"error": "empty_after_strip"}
    callsign = parts[0]
    instruction = parts[1] if len(parts) > 1 else ""
    payload = parts[2:] if len(parts) > 2 else []
    return {
        "callsign": callsign,
        "instruction": instruction,
        "payload": payload,
    }


# ---------------------------------------------------------------------------
# Deterministic lift model (F_AVIATION_001)
# ---------------------------------------------------------------------------

def compute_lift_mcn(
    speed_kt: int,
    density_ratio_num: int,
    density_ratio_den: int,
    cl_num: int,
    cl_den: int,
    area_dm2: int,
) -> int:
    """
    Compute aerodynamic lift in milli-centi-Newtons using integer arithmetic.

    L = (1/2) * rho * v^2 * Cl * A

    All inputs are integers; result is integer (milli-centi-Newtons).
    Uses Fraction for exact intermediate computation.

    Invariant: Same inputs always produce identical integer result (determinism).
    Falsification: Two calls with identical inputs return different results → F_AVIATION_001.
    """
    speed = Fraction(speed_kt)
    rho = Fraction(density_ratio_num, density_ratio_den)
    cl = Fraction(cl_num, cl_den)
    area = Fraction(area_dm2)
    lift_rational = Fraction(1, 2) * rho * speed * speed * cl * area
    return int(lift_rational)


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_AVIATION",
    "name": "Aviation & ATC",
    "invariants": [
        "Aircraft never enters a state that violates known safe-flight envelopes.",
        "External weather/ATC API failures are circuit-broken; cached data is used instead.",
        "ATC messages with invalid format are rejected without crashing the parser.",
    ],
    "falsification_tests": ["F_AVIATION_001", "F_AVIATION_002", "F_AVIATION_003", "F_AVIATION_004"],
    "implementation_functions": [
        "check_flight_envelope",
        "CircuitBreaker",
        "parse_atc_message",
        "compute_lift_mcn",
    ],
    "uses_circuit_breaker": True,
    "uses_integer_arithmetic": True,
}
