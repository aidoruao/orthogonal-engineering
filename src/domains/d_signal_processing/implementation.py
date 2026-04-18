"""Implementation models for Signal Processing."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SignalProcessingClaim:
    """Structured claim parameters for Signal Processing domain invariants."""

    nyquist_satisfied: bool
    fourier_invertible: bool
    filter_causal: bool
    snr_positive: bool
    bandwidth_hz: Fraction


def create_nominal_claim() -> SignalProcessingClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return SignalProcessingClaim(
        nyquist_satisfied=True,
        fourier_invertible=True,
        filter_causal=True,
        snr_positive=True,
        bandwidth_hz=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "SIGNAL_PROCESSING",
    "claim_model": "SignalProcessingClaim",
    "check_functions": [
        "check_nyquist_criterion_satisfied",
        "check_fourier_transform_invertible",
        "check_filter_causality",
        "check_snr_positive",
        "check_bandwidth_fraction",
    ],
}
