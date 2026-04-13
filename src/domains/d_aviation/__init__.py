# D_AVIATION domain — Aviation & ATC (External API circuit-breakers)
# Invariant: Aircraft never enters a state that violates known safe-flight envelopes.
# Source: ontology/ontology.json#D_AVIATION
# Falsification ID: F_AVIATION_004

from .implementation import FlightState
from .invariants import (
    check_flight_envelope_compliance,
    check_pilot_certification,
    check_ifr_requirements,
    run_all_invariants,
)

__all__ = [
    "FlightState",
    "check_flight_envelope_compliance",
    "check_pilot_certification",
    "check_ifr_requirements",
    "run_all_invariants",
]
