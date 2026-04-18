"""Invariant checks for Plumbing Trades."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import PlumbingTradesClaim, create_nominal_claim


def check_backflow_prevention_installed(data: PlumbingTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Backflow prevention is installed.

    Standard: Plumbing Trades domain invariant.
    Falsifies if: not backflow_prevention_installed.
    falsifies_if: not backflow_prevention_installed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.backflow_prevention_installed
    proof = ProofObject(
        rule="check_backflow_prevention_installed",
        premises=[
            "domain=Plumbing Trades",
            f"backflow_prevention_installed={{data.backflow_prevention_installed}}",
        ],
        conclusion=(
            "PASS: Backflow prevention is installed"
            if success else "FAIL: Backflow prevention is installed"
        ),
    )
    return success, proof


def check_pipe_slope_adequate(data: PlumbingTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Pipe slope is adequate for drainage.

    Standard: Plumbing Trades domain invariant.
    Falsifies if: not pipe_slope_adequate.
    falsifies_if: not pipe_slope_adequate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.pipe_slope_adequate
    proof = ProofObject(
        rule="check_pipe_slope_adequate",
        premises=[
            "domain=Plumbing Trades",
            f"pipe_slope_adequate={{data.pipe_slope_adequate}}",
        ],
        conclusion=(
            "PASS: Pipe slope is adequate for drainage"
            if success else "FAIL: Pipe slope is adequate for drainage"
        ),
    )
    return success, proof


def check_fixture_unit_count_valid(data: PlumbingTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Fixture unit count is valid.

    Standard: Plumbing Trades domain invariant.
    Falsifies if: not fixture_unit_count_valid.
    falsifies_if: not fixture_unit_count_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.fixture_unit_count_valid
    proof = ProofObject(
        rule="check_fixture_unit_count_valid",
        premises=[
            "domain=Plumbing Trades",
            f"fixture_unit_count_valid={{data.fixture_unit_count_valid}}",
        ],
        conclusion=(
            "PASS: Fixture unit count is valid"
            if success else "FAIL: Fixture unit count is valid"
        ),
    )
    return success, proof


def check_pressure_regulation_present(data: PlumbingTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Pressure regulation is present.

    Standard: Plumbing Trades domain invariant.
    Falsifies if: not pressure_regulation_present.
    falsifies_if: not pressure_regulation_present.

    Returns:
        Tuple of (success, proof).
    """
    success = data.pressure_regulation_present
    proof = ProofObject(
        rule="check_pressure_regulation_present",
        premises=[
            "domain=Plumbing Trades",
            f"pressure_regulation_present={{data.pressure_regulation_present}}",
        ],
        conclusion=(
            "PASS: Pressure regulation is present"
            if success else "FAIL: Pressure regulation is present"
        ),
    )
    return success, proof


def check_flow_rate_gpm_fraction(data: PlumbingTradesClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Flow rate is non-negative.

    Standard: Plumbing Trades domain invariant.
    Falsifies if: not flow_rate_gpm.
    falsifies_if: not flow_rate_gpm.

    Returns:
        Tuple of (success, proof).
    """
    success = data.flow_rate_gpm >= Fraction(0)
    proof = ProofObject(
        rule="check_flow_rate_gpm_fraction",
        premises=[
            "domain=Plumbing Trades",
            f"flow_rate_gpm={{data.flow_rate_gpm}}",
        ],
        conclusion=(
            "PASS: Flow rate is non-negative is non-negative"
            if success else "FAIL: Flow rate is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Plumbing Trades nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_backflow_prevention_installed", check_backflow_prevention_installed),
        ("check_pipe_slope_adequate", check_pipe_slope_adequate),
        ("check_fixture_unit_count_valid", check_fixture_unit_count_valid),
        ("check_pressure_regulation_present", check_pressure_regulation_present),
        ("check_flow_rate_gpm_fraction", check_flow_rate_gpm_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
