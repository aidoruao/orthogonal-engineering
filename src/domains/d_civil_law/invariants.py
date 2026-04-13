"""D_CIVIL_LAW invariants — Fraction only. 0 floats.

Standards:
- Restatement (Second) of Torts
- UCC §2-201 (Statute of Frauds for goods)
- Restatement (Second) of Contracts §110 (Statute of Frauds)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import FrozenTortClaim, FrozenContract


def check_tort_elements(claim: FrozenTortClaim) -> Tuple[bool, ProofObject]:
    """
    Rule: A valid tort claim requires all four elements: duty, breach, causation, and damages > 0, filed within the statute of limitations.

    Standard: Restatement (Second) of Torts §281
    falsifies_if: any tort element missing OR damages_amount <= 0 OR days_since_incident > statute_of_limitations_days.
    """
    all_elements = (
        claim.duty_exists
        and claim.breach_occurred
        and claim.causation_established
    )
    damages_positive = claim.damages_amount > Fraction(0)
    within_sol = claim.days_since_incident <= claim.statute_of_limitations_days

    success = all_elements and damages_positive and within_sol

    premises = [
        f"claim_id={claim.claim_id}",
        f"duty_exists={claim.duty_exists}",
        f"breach_occurred={claim.breach_occurred}",
        f"causation_established={claim.causation_established}",
        f"damages_amount={claim.damages_amount}",
        f"days_since_incident={claim.days_since_incident}",
        f"statute_of_limitations_days={claim.statute_of_limitations_days}",
        f"within_sol={within_sol}",
    ]

    if not success:
        return False, ProofObject(
            rule="TortElements",
            premises=premises,
            conclusion="VIOLATION: Tort claim fails — missing element, zero damages, or statute of limitations expired",
        )

    return True, ProofObject(
        rule="TortElements",
        premises=premises,
        conclusion="Restatement §281 tort elements satisfied — all four elements, positive damages, within SOL",
    )


def check_statute_of_frauds(contract: FrozenContract) -> Tuple[bool, ProofObject]:
    """
    Rule: Contracts involving land or value > $500 must be in writing under the Statute of Frauds.

    Standard: UCC §2-201; Restatement (Second) of Contracts §110
    falsifies_if: (involves_land OR contract_value > 500) AND in_writing is False.
    """
    writing_required = contract.involves_land or contract.contract_value > Fraction(500)
    success = not writing_required or contract.in_writing

    premises = [
        f"contract_id={contract.contract_id}",
        f"involves_land={contract.involves_land}",
        f"contract_value={contract.contract_value}",
        f"writing_required={writing_required}",
        f"in_writing={contract.in_writing}",
    ]

    if not success:
        return False, ProofObject(
            rule="StatuteOfFrauds",
            premises=premises,
            conclusion="VIOLATION: Statute of Frauds — contract involving land or value > $500 not in writing",
        )

    return True, ProofObject(
        rule="StatuteOfFrauds",
        premises=premises,
        conclusion="Statute of Frauds satisfied — writing requirement met or not applicable",
    )


def check_contract_formation(contract: FrozenContract) -> Tuple[bool, ProofObject]:
    """
    Rule: Valid contract formation requires offer, acceptance, and consideration.

    Standard: Restatement (Second) of Contracts §17
    falsifies_if: offer_present is False OR acceptance_present is False OR consideration_present is False.
    """
    success = contract.offer_present and contract.acceptance_present and contract.consideration_present

    premises = [
        f"contract_id={contract.contract_id}",
        f"offer_present={contract.offer_present}",
        f"acceptance_present={contract.acceptance_present}",
        f"consideration_present={contract.consideration_present}",
    ]

    if not success:
        return False, ProofObject(
            rule="ContractFormation",
            premises=premises,
            conclusion="VIOLATION: Restatement §17 contract formation — missing offer, acceptance, or consideration",
        )

    return True, ProofObject(
        rule="ContractFormation",
        premises=premises,
        conclusion="Restatement §17 contract formation elements satisfied",
    )


def run_all_invariants() -> dict:
    """Run all D_CIVIL_LAW invariants with nominal sample data.

    falsifies_if: any civil law invariant check fails or raises an exception.
    """
    tort = FrozenTortClaim(
        claim_id="TORT-001",
        duty_exists=True,
        breach_occurred=True,
        causation_established=True,
        damages_amount=Fraction(10000),
        statute_of_limitations_days=Fraction(1095),
        days_since_incident=Fraction(365),
    )
    contract = FrozenContract(
        contract_id="CONTRACT-001",
        offer_present=True,
        acceptance_present=True,
        consideration_present=True,
        in_writing=True,
        contract_value=Fraction(1000),
        involves_land=True,
    )

    checks = [
        ("check_tort_elements", lambda: check_tort_elements(tort)),
        ("check_statute_of_frauds", lambda: check_statute_of_frauds(contract)),
        ("check_contract_formation", lambda: check_contract_formation(contract)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
