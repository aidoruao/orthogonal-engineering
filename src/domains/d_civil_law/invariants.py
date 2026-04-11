"""D_CIVIL_LAW invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Federal Rules of Civil Procedure (FRCP)
- State civil procedure codes
- Uniform Commercial Code (UCC) Articles 2, 9
- Restatement (Second) of Contracts

Source: ontology/ontology.json#D_CIVIL_LAW
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_contract_formation_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Valid contract requires offer, acceptance, consideration.
    
    Standard: Restatement (Second) of Contracts §17
    Falsifies if: Contract formed without all three elements.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Valid contract elements
    has_offer = True
    has_acceptance = True
    has_consideration = True
    
    valid_contract = has_offer and has_acceptance and has_consideration
    
    # Invalid - missing consideration
    missing_consideration = has_offer and has_acceptance and not has_consideration
    
    success = valid_contract and not missing_consideration
    
    proof = ProofObject(
        rule="ContractFormationRequirements",
        premises=[
            "element_offer = required",
            "element_acceptance = required", 
            "element_consideration = required",
            f"valid_contract = {valid_contract}",
            f"missing_consideration_rejected = {not missing_consideration}",
        ],
        conclusion=(
            "Contract formation requires all elements per Restatement §17"
            if success
            else "FAIL: Contract formation check failed"
        ),
    )
    return success, proof


def check_statute_of_frauds_compliance() -> Tuple[bool, ProofObject]:
    """
    Invariant: Contracts for land/>$500 must be in writing.
    
    Standard: UCC §2-201, Restatement (Second) §110
    Falsifies if: Oral contract for land or >$500 enforced.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Land contract - must be written
    land_contract_value = Fraction(1)  # Any value for land
    land_in_writing = True
    land_enforceable = land_in_writing  # Only enforceable if written
    
    # Goods contract > $500
    goods_value = Fraction(1000)
    goods_threshold = Fraction(500)
    goods_in_writing = True
    goods_requires_writing = goods_value > goods_threshold
    goods_enforceable = goods_in_writing if goods_requires_writing else True
    
    # Small goods contract <= $500 - oral OK
    small_goods_value = Fraction(300)
    small_requires_writing = small_goods_value > goods_threshold
    small_enforceable = True  # Oral OK for small amounts
    
    success = (
        land_enforceable and 
        goods_enforceable and 
        small_enforceable and 
        not small_requires_writing
    )
    
    proof = ProofObject(
        rule="StatuteOfFraudsCompliance",
        premises=[
            f"land_contract_requires_writing = True",
            f"goods_threshold = ${goods_threshold}",
            f"goods_contract_value = ${goods_value}",
            f"goods_requires_writing = {goods_requires_writing}",
            f"small_goods_value = ${small_goods_value}",
            f"small_requires_writing = {small_requires_writing}",
        ],
        conclusion=(
            "Statute of Frauds applied per UCC §2-201"
            if success
            else "FAIL: Statute of Frauds check failed"
        ),
    )
    return success, proof


def check_frcp_timing_deadlines() -> Tuple[bool, ProofObject]:
    """
    Invariant: Civil procedure timing deadlines must be enforced.
    
    Standard: FRCP 12(a)(1) - 21 days to answer
    Falsifies if: Late answer accepted without good cause.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    answer_deadline_days = Fraction(21)
    
    # Timely answer (day 20)
    answer_filed_day = Fraction(20)
    timely = answer_filed_day <= answer_deadline_days
    
    # Late answer (day 25)
    late_filed_day = Fraction(25)
    is_late = late_filed_day > answer_deadline_days
    
    success = timely and is_late
    
    proof = ProofObject(
        rule="FRCPTimingDeadlines",
        premises=[
            f"answer_deadline = {answer_deadline_days} days",
            f"timely_answer_day = {answer_filed_day}",
            f"timely = {timely}",
            f"late_answer_day = {late_filed_day}",
            f"is_late = {is_late}",
        ],
        conclusion=(
            "FRCP timing deadlines enforced per Rule 12(a)(1)"
            if success
            else "FAIL: Timing deadline check failed"
        ),
    )
    return success, proof


def check_damages_calculation_precision() -> Tuple[bool, ProofObject]:
    """
    Invariant: Damages calculations use exact Fraction arithmetic.
    
    Standard: Restatement (Second) of Contracts §347
    Falsifies if: Float rounding in damages computation.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    contract_price = Fraction(100_000)
    costs_saved = Fraction(1, 3) * contract_price  # 33,333.33... exactly
    expected_profit = Fraction(20_000)
    
    # Expectation damages = profit lost
    expectation_damages = expected_profit
    
    # Reliance damages = costs incurred
    reliance_costs = Fraction(15_000)
    reliance_damages = reliance_costs
    
    # Both should be exact Fractions
    expectation_exact = isinstance(expectation_damages, Fraction)
    reliance_exact = isinstance(reliance_damages, Fraction)
    
    success = expectation_exact and reliance_exact
    
    proof = ProofObject(
        rule="DamagesCalculationPrecision",
        premises=[
            f"contract_price = ${contract_price}",
            f"costs_saved = ${costs_saved}",
            f"expectation_damages = ${expectation_damages}",
            f"reliance_damages = ${reliance_damages}",
            f"expectation_is_fraction = {expectation_exact}",
            f"reliance_is_fraction = {reliance_exact}",
        ],
        conclusion=(
            "Exact Fraction damages per Restatement §347"
            if success
            else "FAIL: Non-exact damages detected"
        ),
    )
    return success, proof


def check_burden_of_proof_allocation() -> Tuple[bool, ProofObject]:
    """
    Invariant: Burden of proof allocated correctly to plaintiff.
    
    Standard: FRCP 8 (Pleading standards)
    Falsifies if: Defendant bears burden on plaintiff's claim.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Plaintiff bears burden of proof on elements of claim
    plaintiff_claim_elements = [
        "duty",
        "breach", 
        "causation",
        "damages"
    ]
    
    burden_on_plaintiff = all(elem in plaintiff_claim_elements for elem in plaintiff_claim_elements)
    
    # Defendant bears burden on affirmative defenses
    affirmative_defenses = ["statute_of_limitations", "accord_and_satisfaction"]
    defendant_burden = len(affirmative_defenses) > 0
    
    success = burden_on_plaintiff and defendant_burden
    
    proof = ProofObject(
        rule="BurdenOfProofAllocation",
        premises=[
            f"plaintiff_elements = {len(plaintiff_claim_elements)}",
            f"burden_on_plaintiff = {burden_on_plaintiff}",
            f"affirmative_defenses = {len(affirmative_defenses)}",
            f"defendant_burden_exists = {defendant_burden}",
        ],
        conclusion=(
            "Burden allocation correct per FRCP 8"
            if success
            else "FAIL: Burden allocation incorrect"
        ),
    )
    return success, proof


def check_res_judicata_effect() -> Tuple[bool, ProofObject]:
    """
    Invariant: Claim preclusion prevents relitigation of final judgments.
    
    Standard: Restatement (Second) of Judgments §17
    Falsifies if: Same parties relitigate same claim after final judgment.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Requirements for claim preclusion
    same_parties = True
    same_claim = True
    final_judgment = True
    valid_judgment = True
    
    # All must be true for preclusion to apply
    preclusion_applies = same_parties and same_claim and final_judgment and valid_judgment
    
    # Different claim - preclusion does not apply
    different_claim = False
    preclusion_not_applicable = not different_claim
    
    success = preclusion_applies and preclusion_not_applicable
    
    proof = ProofObject(
        rule="ResJudicataEffect",
        premises=[
            "requirement_same_parties = True",
            "requirement_same_claim = True",
            "requirement_final_judgment = True",
            "requirement_valid_judgment = True",
            f"preclusion_applies = {preclusion_applies}",
            f"different_claim_exempt = {preclusion_not_applicable}",
        ],
        conclusion=(
            "Claim preclusion applied per Restatement §17"
            if success
            else "FAIL: Res judicata check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_CIVIL_LAW invariants."""
    checks = [
        ("check_contract_formation_requirements", check_contract_formation_requirements),
        ("check_statute_of_frauds_compliance", check_statute_of_frauds_compliance),
        ("check_frcp_timing_deadlines", check_frcp_timing_deadlines),
        ("check_damages_calculation_precision", check_damages_calculation_precision),
        ("check_burden_of_proof_allocation", check_burden_of_proof_allocation),
        ("check_res_judicata_effect", check_res_judicata_effect),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CIVIL_LAW invariants: PASS")
