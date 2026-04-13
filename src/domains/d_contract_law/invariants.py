#!/usr/bin/env python3
"""Contract Law Invariants — Formation, Breach, Damages."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Breach,
    Contract,
    ContractStatus,
    Party,
    STATUTE_OF_FRAUDS_THRESHOLD,
    ContractType,
)


def check_statute_of_frauds(contract: Contract) -> Tuple[bool, ProofObject]:
    """
    UCC § 2-201: Contracts for sale of goods >= $500 must be in writing.

    Falsifies if: contract is within statute threshold and contract.is_written is False.
    falsifies_if: contract is within statute threshold and contract.is_written is False.
    """
    if not contract.is_within_statute_of_frauds():
        return True, ProofObject(
            conclusion=f"Below Statute of Frauds threshold ({contract.price} < {STATUTE_OF_FRAUDS_THRESHOLD})",
            premises=["Oral contract permissible"],
            rule="ucc_2_201_threshold"
        )
    
    if contract.is_written:
        return True, ProofObject(
            conclusion="Statute of Frauds satisfied — contract in writing",
            premises=[f"Price: {contract.price}", "Written: True"],
            rule="ucc_2_201_compliance"
        )
    
    return False, ProofObject(
        conclusion=f"VIOLATION: Statute of Frauds — {contract.price} contract not in writing",
        premises=[f"Price: {contract.price}", f"Threshold: {STATUTE_OF_FRAUDS_THRESHOLD}"],
        rule="ucc_2_201_violation"
    )


def check_formation(contract: Contract) -> Tuple[bool, ProofObject]:
    """Offer + Acceptance + Consideration = Valid Contract.

    Falsifies if: any of offer, acceptance, or consideration is missing.
    falsifies_if: any of offer, acceptance, or consideration is missing.
    """
    missing = []
    if contract.offer_date is None:
        missing.append("offer")
    if contract.acceptance_date is None:
        missing.append("acceptance")
    if contract.price <= Fraction(0):
        missing.append("consideration")
    
    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: Missing formation elements: {missing}",
            premises=[f"Missing: {missing}"],
            rule="contract_formation"
        )
    
    return True, ProofObject(
        conclusion="Valid contract formation (Offer + Acceptance + Consideration)",
        premises=["Offer present", "Acceptance present", "Consideration present"],
        rule="contract_formation"
    )


def check_breach_materiality(breach: Breach) -> Tuple[bool, ProofObject]:
    """Material breach excuses further performance; minor does not.

    Falsifies if: not applicable (function reports whether breach is material or minor).
    falsifies_if: not applicable (function reports whether breach is material or minor).
    """
    if breach.material:
        return True, ProofObject(
            conclusion="Material breach — non-breaching party excused from performance",
            premises=["Breach is material"],
            rule="breach_materiality"
        )
    return True, ProofObject(
        conclusion="Minor breach — non-breaching party must still perform",
        premises=["Breach is minor"],
        rule="breach_materiality"
    )


def check_expectation_principle(breach: Breach) -> Tuple[bool, ProofObject]:
    """
    Expectation damages should put injured party in position 
    they would have been in had contract been performed.

    Falsifies if: breach.total_damages() exceeds breach.expectation_damages.
    falsifies_if: breach.total_damages() exceeds breach.expectation_damages.
    """
    total = breach.total_damages()
    if total > breach.expectation_damages:
        return False, ProofObject(
            conclusion="VIOLATION: Damages exceed expectation interest",
            premises=[f"Awarded: {total}", f"Expectation: {breach.expectation_damages}"],
            rule="expectation_damages_cap"
        )
    
    return True, ProofObject(
        conclusion="Damages within expectation limit",
        premises=[f"Damages: {total}", f"Cap: {breach.expectation_damages}"],
        rule="expectation_damages_cap"
    )


def run_all_invariants() -> dict:
    """Run all D_CONTRACT_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    breach = Breach(
        contract=Contract(
        offeror=Party(
        name="Sample CONTRACT",
    ),
        offeree=Party(
        name="Sample CONTRACT",
    ),
        contract_type=ContractType.SALE_OF_GOODS,
    ),
        breach_date=None,
    )
    contract = Contract(
        offeror=Party(
        name="Sample CONTRACT",
    ),
        offeree=Party(
        name="Sample CONTRACT",
    ),
        contract_type=ContractType.SALE_OF_GOODS,
    )

    checks = [
        ("check_breach_materiality", lambda: check_breach_materiality(breach)),
        ("check_expectation_principle", lambda: check_expectation_principle(breach)),
        ("check_formation", lambda: check_formation(contract)),
        ("check_statute_of_frauds", lambda: check_statute_of_frauds(contract)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CONTRACT_LAW invariants: PASS")
