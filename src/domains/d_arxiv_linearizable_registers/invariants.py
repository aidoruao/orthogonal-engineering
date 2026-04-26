"""Invariant checks for D_ARXIV_LINEARIZABLE_REGISTERS.

Paper: arXiv 2604.05862v1 (cs.DC)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    DistributedSystem,
    RegisterImplementation,
    LinearizableRegistersClaim,
    LinearizableRegistersEvidence,
)


# ---------------------------------------------------------------------------
# 1. Linearizability
# ---------------------------------------------------------------------------

def check_linearizability(
    claim: LinearizableRegistersClaim,
) -> Tuple[bool, ProofObject]:
    """Register implementation must be linearizable.

    Standard: arXiv 2604.05862v1 claim operationalization.
    Falsifies if: register.is_linearizable is False.
    falsifies_if: register is not linearizable.
    """
    if not claim.register.is_linearizable:
        return False, ProofObject(
            rule="check_linearizability",
            premises=["is_linearizable=False"],
            conclusion="VIOLATION: Register implementation is not linearizable",
        )
    return True, ProofObject(
        rule="check_linearizability",
        premises=["is_linearizable=True"],
        conclusion="PASS: Register implementation is linearizable",
    )


# ---------------------------------------------------------------------------
# 2. Real-time order preserved
# ---------------------------------------------------------------------------

def check_real_time_order_preserved(
    claim: LinearizableRegistersClaim,
) -> Tuple[bool, ProofObject]:
    """Register must preserve real-time order of operations.

    Standard: arXiv 2604.05862v1 claim operationalization.
    Falsifies if: register.preserves_real_time_order is False.
    falsifies_if: real-time order is not preserved.
    """
    if not claim.register.preserves_real_time_order:
        return False, ProofObject(
            rule="check_real_time_order_preserved",
            premises=["preserves_real_time_order=False"],
            conclusion="VIOLATION: Real-time order not preserved",
        )
    return True, ProofObject(
        rule="check_real_time_order_preserved",
        premises=["preserves_real_time_order=True"],
        conclusion="PASS: Real-time order preserved",
    )


# ---------------------------------------------------------------------------
# 3. Message chains required
# ---------------------------------------------------------------------------

def check_message_chains_required(
    claim: LinearizableRegistersClaim,
) -> Tuple[bool, ProofObject]:
    """Linearizable implementations must use message chains.

    Standard: arXiv 2604.05862v1 claim operationalization.
    Falsifies if: register.uses_message_chains is False in asynchronous system.
    falsifies_if: message chains are not used in asynchronous system.
    """
    if claim.system.is_asynchronous and not claim.register.uses_message_chains:
        return False, ProofObject(
            rule="check_message_chains_required",
            premises=[
                "is_asynchronous=True",
                "uses_message_chains=False",
            ],
            conclusion="VIOLATION: Message chains required in asynchronous system",
        )
    return True, ProofObject(
        rule="check_message_chains_required",
        premises=[
            f"is_asynchronous={claim.system.is_asynchronous}",
            f"uses_message_chains={claim.register.uses_message_chains}",
        ],
        conclusion="PASS: Message chains used where required",
    )


# ---------------------------------------------------------------------------
# 4. Chain density threshold
# ---------------------------------------------------------------------------

def check_chain_density_threshold(
    claim: LinearizableRegistersClaim,
) -> Tuple[bool, ProofObject]:
    """Message chain density must meet threshold for linearizability.

    Standard: arXiv 2604.05862v1 claim operationalization.
    Falsifies if: message_chain_density < chain_density_threshold.
    falsifies_if: message chain density is below threshold.
    """
    if claim.register.message_chain_density < claim.chain_density_threshold:
        return False, ProofObject(
            rule="check_chain_density_threshold",
            premises=[
                f"message_chain_density={claim.register.message_chain_density}",
                f"chain_density_threshold={claim.chain_density_threshold}",
            ],
            conclusion="VIOLATION: Message chain density below threshold",
        )
    return True, ProofObject(
        rule="check_chain_density_threshold",
        premises=[
            f"message_chain_density={claim.register.message_chain_density}",
            f"chain_density_threshold={claim.chain_density_threshold}",
        ],
        conclusion="PASS: Message chain density meets threshold",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_LINEARIZABLE_REGISTERS invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    system = DistributedSystem(
        system_name="async_message_passing",
        is_asynchronous=True,
        process_count=3,
    )
    register_good = RegisterImplementation(
        is_linearizable=True,
        preserves_real_time_order=True,
        uses_message_chains=True,
        message_chain_density=Fraction(8, 10),
    )
    claim_safe = LinearizableRegistersClaim(
        system=system,
        register=register_good,
        chain_density_threshold=Fraction(5, 10),
    )

    # FAIL case: not linearizable
    register_bad_lin = RegisterImplementation(
        is_linearizable=False,
        preserves_real_time_order=True,
        uses_message_chains=True,
        message_chain_density=Fraction(8, 10),
    )
    claim_bad_lin = LinearizableRegistersClaim(
        system=system,
        register=register_bad_lin,
        chain_density_threshold=Fraction(5, 10),
    )

    # FAIL case: no message chains
    register_bad_chains = RegisterImplementation(
        is_linearizable=True,
        preserves_real_time_order=True,
        uses_message_chains=False,
        message_chain_density=Fraction(0),
    )
    claim_bad_chains = LinearizableRegistersClaim(
        system=system,
        register=register_bad_chains,
        chain_density_threshold=Fraction(5, 10),
    )

    # FAIL case: low chain density
    register_low_density = RegisterImplementation(
        is_linearizable=True,
        preserves_real_time_order=True,
        uses_message_chains=True,
        message_chain_density=Fraction(2, 10),
    )
    claim_low_density = LinearizableRegistersClaim(
        system=system,
        register=register_low_density,
        chain_density_threshold=Fraction(5, 10),
    )

    checks = [
        ("check_linearizability_pass", lambda: check_linearizability(claim_safe)),
        ("check_real_time_order_preserved_pass", lambda: check_real_time_order_preserved(claim_safe)),
        ("check_message_chains_required_pass", lambda: check_message_chains_required(claim_safe)),
        ("check_chain_density_threshold_pass", lambda: check_chain_density_threshold(claim_safe)),
        ("check_linearizability_fail", lambda: check_linearizability(claim_bad_lin)),
        ("check_message_chains_required_fail", lambda: check_message_chains_required(claim_bad_chains)),
        ("check_chain_density_threshold_fail", lambda: check_chain_density_threshold(claim_low_density)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_LINEARIZABLE_REGISTERS invariants: PASS")
