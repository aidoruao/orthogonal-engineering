"""Implementation models for Plumbing Trades."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class PlumbingTradesClaim:
    """Structured claim parameters for Plumbing Trades domain invariants."""

    backflow_prevention_installed: bool
    pipe_slope_adequate: bool
    fixture_unit_count_valid: bool
    pressure_regulation_present: bool
    flow_rate_gpm: Fraction


def create_nominal_claim() -> PlumbingTradesClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return PlumbingTradesClaim(
        backflow_prevention_installed=True,
        pipe_slope_adequate=True,
        fixture_unit_count_valid=True,
        pressure_regulation_present=True,
        flow_rate_gpm=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "PLUMBING_TRADES",
    "claim_model": "PlumbingTradesClaim",
    "check_functions": [
        "check_backflow_prevention_installed",
        "check_pipe_slope_adequate",
        "check_fixture_unit_count_valid",
        "check_pressure_regulation_present",
        "check_flow_rate_gpm_fraction",
    ],
}
