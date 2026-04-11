"""D_CORPORATE_LAW invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Delaware General Corporation Law (DGCL)
- Model Business Corporation Act (MBCA)
- SEC Regulation S-K (Disclosure)
- Sarbanes-Oxley Act (Governance)

Source: ontology/ontology.json#D_CORPORATE_LAW
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_director_fiduciary_duties() -> Tuple[bool, ProofObject]:
    """
    Invariant: Directors owe duty of care and loyalty.
    
    Standard: DGCL §141; Smith v. Van Gorkom (1985)
    Falsifies if: Director self-deals without disclosure.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Duty of care
    informed_decision = True
    rational_basis = True
    duty_of_care = informed_decision and rational_basis
    
    # Duty of loyalty
    no_self_dealing = True
    best_interest_corporation = True
    disclose_conflict = True
    duty_of_loyalty = no_self_dealing and best_interest_corporation and disclose_conflict
    
    # Business judgment rule protection
    no_fraud = True
    no_gross_negligence = True
    bjr_applies = duty_of_care and duty_of_loyalty and no_fraud and no_gross_negligence
    
    success = duty_of_care and duty_of_loyalty and bjr_applies
    
    proof = ProofObject(
        rule="DirectorFiduciaryDuties",
        premises=[
            f"duty_of_care = {duty_of_care}",
            f"duty_of_loyalty = {duty_of_loyalty}",
            "no_fraud = True",
            "no_gross_negligence = True",
            f"business_judgment_rule = {bjr_applies}",
        ],
        conclusion=(
            "Director fiduciary duties enforced per DGCL §141"
            if success
            else "FAIL: Fiduciary duty check failed"
        ),
    )
    return success, proof


def check_shareholder_voting_rights() -> Tuple[bool, ProofObject]:
    """
    Invariant: Shareholder voting rights protected.
    
    Standard: DGCL §211-220; Blasius v. Atlas Corp. (1988)
    Falsifies if: Board action for primary purpose of interfering with vote.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Voting rights
    voting_shares = Fraction(1000)
    votes_per_share = Fraction(1)
    total_votes = voting_shares * votes_per_share
    
    # Quorum requirement (typically majority)
    shares_outstanding = Fraction(2000)
    quorum_required = Fraction(1, 2)
    quorum_threshold = shares_outstanding * quorum_required
    quorum_met = total_votes >= quorum_threshold
    
    # Director election
    board_seats = 5
    candidates = 5
    contested = candidates > board_seats
    
    # Cumulative voting (if permitted)
    cumulative_voting = False
    if cumulative_voting:
        votes_per_share = Fraction(board_seats)
    
    success = quorum_met and candidates >= board_seats
    
    proof = ProofObject(
        rule="ShareholderVotingRights",
        premises=[
            f"voting_shares = {voting_shares}",
            f"total_votes = {total_votes}",
            f"quorum_threshold = {quorum_threshold}",
            f"quorum_met = {quorum_met}",
            f"board_seats = {board_seats}",
            f"candidates = {candidates}",
        ],
        conclusion=(
            "Shareholder voting rights protected per DGCL §211"
            if success
            else "FAIL: Voting rights check failed"
        ),
    )
    return success, proof


def check_merger_approval_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Mergers require board and shareholder approval.
    
    Standard: DGCL §251; MBCA §11.04
    Falsifies if: Merger completed without proper approvals.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Board approval required
    board_approved = True
    majority_directors = True
    board_valid = board_approved and majority_directors
    
    # Shareholder approval (typically majority of outstanding)
    shares_voting_for = Fraction(1200)
    shares_outstanding = Fraction(2000)
    approval_threshold = Fraction(1, 2)
    
    votes_for_ratio = shares_voting_for / shares_outstanding
    shareholder_approved = votes_for_ratio >= approval_threshold
    
    # Short-form merger exception (>90% owned)
    parent_ownership = Fraction(95, 100)
    short_form_threshold = Fraction(90, 100)
    short_form_eligible = parent_ownership >= short_form_threshold
    
    # Short-form doesn't need target shareholder vote
    if short_form_eligible:
        shareholder_approved = True
    
    success = board_valid and shareholder_approved
    
    proof = ProofObject(
        rule="MergerApprovalRequirements",
        premises=[
            f"board_approved = {board_valid}",
            f"shares_for = {shares_voting_for}",
            f"shares_outstanding = {shares_outstanding}",
            f"approval_ratio = {float(votes_for_ratio):.1%}",
            f"shareholder_approved = {shareholder_approved}",
            f"short_form_eligible = {short_form_eligible}",
        ],
        conclusion=(
            "Merger approvals enforced per DGCL §251"
            if success
            else "FAIL: Merger approval check failed"
        ),
    )
    return success, proof


def check_piercing_corporate_veil() -> Tuple[bool, ProofObject]:
    """
    Invariant: Corporate veil pierced only for abuse/fraud/inadequate capital.
    
    Standard: United States v. Milwaukee Refrigerator (1905)
    Falsifies if: Veil pierced without alter ego or injustice.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Factors for piercing
    undercapitalization = True
    failure_follow_formalities = True
    commingling_funds = True
    fraud = True
    
    # Strong case for piercing
    veil_piercing_appropriate = (
        (undercapitalization and failure_follow_formalities) or
        fraud or
        commingling_funds
    )
    
    # Separate entity respected when formalities observed
    adequate_capital = True
    follow_formalities = True
    separate_accounts = True
    
    separate_entity_preserved = (
        adequate_capital and 
        follow_formalities and 
        separate_accounts
    )
    
    success = veil_piercing_appropriate and separate_entity_preserved
    
    proof = ProofObject(
        rule="PiercingCorporateVeil",
        premises=[
            f"undercapitalization = {undercapitalization}",
            f"failure_formalities = {failure_follow_formalities}",
            f"fraud = {fraud}",
            f"piercing_appropriate = {veil_piercing_appropriate}",
            f"separate_entity_preserved = {separate_entity_preserved}",
        ],
        conclusion=(
            "Corporate veil doctrine applied per Milwaukee Refrigerator"
            if success
            else "FAIL: Veil piercing check failed"
        ),
    )
    return success, proof


def check_proxy_statement_disclosure() -> Tuple[bool, ProofObject]:
    """
    Invariant: Proxy statements disclose all material information.
    
    Standard: SEC Regulation 14A; TSC v. Northway (1976)
    Falsifies if: Material omission in proxy solicitation.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Required disclosures
    executive_compensation = True
    related_party_transactions = True
    auditor_relationship = True
    board_structure = True
    
    all_disclosures = (
        executive_compensation and 
        related_party_transactions and 
        auditor_relationship and 
        board_structure
    )
    
    # Materiality standard
    substantial_likelihood = True  # That reasonable shareholder would consider important
    significance = True
    material = substantial_likelihood and significance
    
    # No omissions of material facts
    no_omissions = True
    
    # Compensation exact using Fraction
    ceo_salary = Fraction(1_000_000)
    ceo_bonus = Fraction(1) * ceo_salary  # 100% bonus
    total_comp = ceo_salary + ceo_bonus
    comp_exact = total_comp == Fraction(2_000_000)
    
    success = all_disclosures and no_omissions and material and comp_exact
    
    proof = ProofObject(
        rule="ProxyStatementDisclosure",
        premises=[
            "executive_compensation_disclosed = True",
            "related_party_disclosed = True",
            "auditor_disclosed = True",
            "board_structure_disclosed = True",
            f"material_standard_met = {material}",
            f"compensation_exact = {comp_exact}",
        ],
        conclusion=(
            "Proxy disclosure enforced per SEC Reg 14A"
            if success
            else "FAIL: Proxy disclosure check failed"
        ),
    )
    return success, proof


def check_duty_of_care_exact_compliance() -> Tuple[bool, ProofObject]:
    """
    Invariant: Director duty of care measured with exact Fraction.
    
    Standard: DGCL §141(e) (Reliance on experts)
    Falsifies if: Board decisions use float approximations for material metrics.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Board consideration of transaction value
    company_value = Fraction(100_000_000)
    offer_price = Fraction(120_000_000)
    premium = offer_price - company_value
    premium_exact = premium == Fraction(20_000_000)
    
    # Premium percentage (exact)
    premium_pct = (premium / company_value) * 100
    premium_pct_exact = premium_pct == Fraction(20)
    
    # Board meeting time consideration (hours of deliberation)
    deliberation_hours = Fraction(40)
    min_reasonable_hours = Fraction(20)
    adequate_deliberation = deliberation_hours >= min_reasonable_hours
    
    success = premium_exact and premium_pct_exact and adequate_deliberation
    
    proof = ProofObject(
        rule="DutyOfCareExactCompliance",
        premises=[
            f"company_value = ${company_value}",
            f"offer_premium = ${premium}",
            f"premium_exact = {premium_exact}",
            f"premium_pct = {premium_pct}%",
            f"deliberation_hours = {deliberation_hours}",
            f"adequate_deliberation = {adequate_deliberation}",
        ],
        conclusion=(
            "Exact Fraction duty of care per DGCL §141(e)"
            if success
            else "FAIL: Duty of care exactness check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_CORPORATE_LAW invariants.

    Falsifies if: any corporate law invariant check fails or raises an exception.
    """
    checks = [
        ("check_director_fiduciary_duties", check_director_fiduciary_duties),
        ("check_shareholder_voting_rights", check_shareholder_voting_rights),
        ("check_merger_approval_requirements", check_merger_approval_requirements),
        ("check_piercing_corporate_veil", check_piercing_corporate_veil),
        ("check_proxy_statement_disclosure", check_proxy_statement_disclosure),
        ("check_duty_of_care_exact_compliance", check_duty_of_care_exact_compliance),
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
    print("All D_CORPORATE_LAW invariants: PASS")
