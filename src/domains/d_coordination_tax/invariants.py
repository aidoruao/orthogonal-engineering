"""D_COORDINATION_TAX invariants — Brooks, sovereign tax, scaling, latency.

Phase P3 of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CoordinationState, SovereignEntity


def check_brooks_law(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Brooks (1975): adding people to a late project makes it later.

    Falsifies if: actual_output >= linear_output when team_size > 1.
    falsifies_if: actual_output >= linear_output and team_size > 1.
    """
    if state.team_size > 1 and state.actual_output >= state.linear_output:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Brooks Law — actual {state.actual_output} >= linear "
                f"{state.linear_output} for team_size={state.team_size}"
            ),
            premises=[
                f"Team size: {state.team_size}",
                f"Actual: {state.actual_output}",
                f"Linear: {state.linear_output}",
            ],
            rule="coordination_brooks_law",
        )
    return True, ProofObject(
        conclusion=(
            f"Brooks Law respected: actual {state.actual_output} < linear "
            f"{state.linear_output} (or team_size=1)"
        ),
        premises=[
            f"Team size: {state.team_size}",
            f"Actual: {state.actual_output}",
        ],
        rule="coordination_brooks_law",
    )


def check_coordination_tax_monotonic(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Coordination tax is non-decreasing with team size.

    Falsifies if: tax_rate decreased when team_size increased.
    falsifies_if: previous_coordination_tax_rate > coordination_tax_rate and previous_team_size < team_size.
    """
    if (
        state.previous_team_size < state.team_size
        and state.previous_coordination_tax_rate > state.coordination_tax_rate
    ):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Tax decreased from {state.previous_coordination_tax_rate} to "
                f"{state.coordination_tax_rate} while team_size increased from "
                f"{state.previous_team_size} to {state.team_size}"
            ),
            premises=[
                f"Previous team: {state.previous_team_size}",
                f"Current team: {state.team_size}",
                f"Previous tax: {state.previous_coordination_tax_rate}",
                f"Current tax: {state.coordination_tax_rate}",
            ],
            rule="coordination_tax_monotonic",
        )
    return True, ProofObject(
        conclusion=(
            f"Tax monotonic: {state.previous_coordination_tax_rate} -> "
            f"{state.coordination_tax_rate} across team sizes"
        ),
        premises=[
            f"Previous tax: {state.previous_coordination_tax_rate}",
            f"Current tax: {state.coordination_tax_rate}",
        ],
        rule="coordination_tax_monotonic",
    )


def check_sovereign_zero_tax(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Mathematical authority eliminates coordination tax.

    Falsifies if: authority_type == "mathematical" and coordination_tax_rate != Fraction(0, 1).
    falsifies_if: authority_type == "mathematical" and coordination_tax_rate != Fraction(0, 1).
    """
    if state.authority_type == "mathematical" and state.coordination_tax_rate != Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Mathematical authority has tax {state.coordination_tax_rate} != 0"
            ),
            premises=[
                f"Authority: {state.authority_type}",
                f"Tax: {state.coordination_tax_rate}",
            ],
            rule="coordination_sovereign_zero_tax",
        )
    return True, ProofObject(
        conclusion=(
            f"Sovereign tax valid: {state.authority_type} -> {state.coordination_tax_rate}"
        ),
        premises=[
            f"Authority: {state.authority_type}",
            f"Tax: {state.coordination_tax_rate}",
        ],
        rule="coordination_sovereign_zero_tax",
    )


def check_alignment_channel_scaling(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Communication channels scale as complete graph edges: n(n-1)/2.

    Falsifies if: alignment_channels != team_size * (team_size - 1) // 2.
    falsifies_if: alignment_channels != team_size * (team_size - 1) // 2.
    """
    expected = state.team_size * (state.team_size - 1) // 2
    if state.alignment_channels != expected:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Alignment channels {state.alignment_channels} != expected {expected}"
            ),
            premises=[
                f"Team size: {state.team_size}",
                f"Expected: {expected}",
                f"Actual: {state.alignment_channels}",
            ],
            rule="coordination_channel_scaling",
        )
    return True, ProofObject(
        conclusion=f"Alignment channels {state.alignment_channels} match n(n-1)/2",
        premises=[
            f"Team size: {state.team_size}",
            f"Channels: {state.alignment_channels}",
        ],
        rule="coordination_channel_scaling",
    )


def check_decision_latency_invariant(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Mathematical authority implies zero decision latency.

    Falsifies if: decision_latency_hours > Fraction(0, 1) when authority_type == "mathematical".
    falsifies_if: authority_type == "mathematical" and decision_latency_hours > Fraction(0, 1).
    """
    if state.authority_type == "mathematical" and state.decision_latency_hours > Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Mathematical authority has latency "
                f"{state.decision_latency_hours} > 0"
            ),
            premises=[
                f"Authority: {state.authority_type}",
                f"Latency: {state.decision_latency_hours}",
            ],
            rule="coordination_decision_latency",
        )
    return True, ProofObject(
        conclusion=(
            f"Decision latency {state.decision_latency_hours} valid for "
            f"{state.authority_type}"
        ),
        premises=[
            f"Authority: {state.authority_type}",
            f"Latency: {state.decision_latency_hours}",
        ],
        rule="coordination_decision_latency",
    )


def check_institutional_overhead_ratio(state: CoordinationState) -> Tuple[bool, ProofObject]:
    """Governance overhead must not exceed 10x investigation output (GAP-5).

    Falsifies if: governance_overhead / investigation_output > Fraction(10, 1).
    falsifies_if: governance_overhead / investigation_output > Fraction(10, 1).
    """
    if state.investigation_output == Fraction(0, 1):
        return False, ProofObject(
            conclusion="VIOLATION: Zero investigation output — ratio undefined",
            premises=[
                f"Overhead: {state.governance_overhead}",
                "Investigation: 0",
            ],
            rule="coordination_institutional_overhead",
        )
    ratio = state.governance_overhead / state.investigation_output
    if ratio > Fraction(10, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Overhead ratio {ratio} > 10"
            ),
            premises=[
                f"Overhead: {state.governance_overhead}",
                f"Investigation: {state.investigation_output}",
                f"Ratio: {ratio}",
            ],
            rule="coordination_institutional_overhead",
        )
    return True, ProofObject(
        conclusion=f"Overhead ratio {ratio} <= 10",
        premises=[
            f"Overhead: {state.governance_overhead}",
            f"Investigation: {state.investigation_output}",
            f"Ratio: {ratio}",
        ],
        rule="coordination_institutional_overhead",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all coordination tax checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = CoordinationState(
        team_size=1,
        previous_team_size=1,
        linear_output=Fraction(10, 1),
        actual_output=Fraction(10, 1),
        coordination_tax_rate=Fraction(0, 1),
        previous_coordination_tax_rate=Fraction(0, 1),
        alignment_channels=0,
        decision_latency_hours=Fraction(0, 1),
        authority_type="mathematical",
        governance_overhead=Fraction(1, 1),
        investigation_output=Fraction(10, 1),
    )
    fail_state = CoordinationState(
        team_size=10,
        previous_team_size=5,
        linear_output=Fraction(10, 1),
        actual_output=Fraction(12, 1),
        coordination_tax_rate=Fraction(7, 10),
        previous_coordination_tax_rate=Fraction(8, 10),
        alignment_channels=44,
        decision_latency_hours=Fraction(72, 1),
        authority_type="mathematical",
        governance_overhead=Fraction(100, 1),
        investigation_output=Fraction(5, 1),
    )

    checks = [
        ("check_brooks_law_pass", lambda: check_brooks_law(pass_state)),
        ("check_brooks_law_fail", lambda: check_brooks_law(fail_state)),
        ("check_coordination_tax_monotonic_pass", lambda: check_coordination_tax_monotonic(pass_state)),
        ("check_coordination_tax_monotonic_fail", lambda: check_coordination_tax_monotonic(fail_state)),
        ("check_sovereign_zero_tax_pass", lambda: check_sovereign_zero_tax(pass_state)),
        ("check_sovereign_zero_tax_fail", lambda: check_sovereign_zero_tax(fail_state)),
        ("check_alignment_channel_scaling_pass", lambda: check_alignment_channel_scaling(pass_state)),
        ("check_alignment_channel_scaling_fail", lambda: check_alignment_channel_scaling(fail_state)),
        ("check_decision_latency_invariant_pass", lambda: check_decision_latency_invariant(pass_state)),
        ("check_decision_latency_invariant_fail", lambda: check_decision_latency_invariant(fail_state)),
        ("check_institutional_overhead_ratio_pass", lambda: check_institutional_overhead_ratio(pass_state)),
        ("check_institutional_overhead_ratio_fail", lambda: check_institutional_overhead_ratio(fail_state)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
