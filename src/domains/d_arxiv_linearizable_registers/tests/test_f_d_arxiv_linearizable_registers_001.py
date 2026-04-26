"""Tests for D_ARXIV_LINEARIZABLE_REGISTERS.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_linearizable_registers.implementation import (
    DistributedSystem,
    RegisterImplementation,
    LinearizableRegistersClaim,
)
from domains.d_arxiv_linearizable_registers.invariants import (
    check_linearizability,
    check_real_time_order_preserved,
    check_message_chains_required,
    check_chain_density_threshold,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_system():
    return DistributedSystem(
        system_name="async_message_passing",
        is_asynchronous=True,
        process_count=3,
    )


def make_good_register():
    return RegisterImplementation(
        is_linearizable=True,
        preserves_real_time_order=True,
        uses_message_chains=True,
        message_chain_density=Fraction(8, 10),
    )


def make_safe_claim():
    return LinearizableRegistersClaim(
        system=make_system(),
        register=make_good_register(),
        chain_density_threshold=Fraction(5, 10),
    )


def make_bad_lin_claim():
    return LinearizableRegistersClaim(
        system=make_system(),
        register=RegisterImplementation(
            is_linearizable=False,
            preserves_real_time_order=True,
            uses_message_chains=True,
            message_chain_density=Fraction(8, 10),
        ),
        chain_density_threshold=Fraction(5, 10),
    )


def make_bad_chains_claim():
    return LinearizableRegistersClaim(
        system=make_system(),
        register=RegisterImplementation(
            is_linearizable=True,
            preserves_real_time_order=True,
            uses_message_chains=False,
            message_chain_density=Fraction(0),
        ),
        chain_density_threshold=Fraction(5, 10),
    )


def make_low_density_claim():
    return LinearizableRegistersClaim(
        system=make_system(),
        register=RegisterImplementation(
            is_linearizable=True,
            preserves_real_time_order=True,
            uses_message_chains=True,
            message_chain_density=Fraction(2, 10),
        ),
        chain_density_threshold=Fraction(5, 10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_linearizability_pass():
    claim = make_safe_claim()
    success, proof = check_linearizability(claim)
    assert success is True
    assert "linearizable" in proof.conclusion


def test_check_linearizability_fail():
    claim = make_bad_lin_claim()
    success, proof = check_linearizability(claim)
    assert success is False
    assert "not linearizable" in proof.conclusion


def test_check_real_time_order_preserved_pass():
    claim = make_safe_claim()
    success, proof = check_real_time_order_preserved(claim)
    assert success is True
    assert "preserved" in proof.conclusion


def test_check_message_chains_required_pass():
    claim = make_safe_claim()
    success, proof = check_message_chains_required(claim)
    assert success is True
    assert "used" in proof.conclusion


def test_check_message_chains_required_fail():
    claim = make_bad_chains_claim()
    success, proof = check_message_chains_required(claim)
    assert success is False
    assert "required" in proof.conclusion


def test_check_chain_density_threshold_pass():
    claim = make_safe_claim()
    success, proof = check_chain_density_threshold(claim)
    assert success is True
    assert "meets" in proof.conclusion


def test_check_chain_density_threshold_fail():
    claim = make_low_density_claim()
    success, proof = check_chain_density_threshold(claim)
    assert success is False
    assert "below" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
