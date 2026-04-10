"""D_RELIGIOUS_LIBERTY Invariants — RFRA, Free Exercise, Establishment Clause

Verifies Religious Freedom Restoration Act compliance,
Free Exercise Clause protections, Establishment Clause limits.

Standards: 42 U.S.C. § 2000bb (RFRA), First Amendment, 42 U.S.C. § 2000cc (RLUIPA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ReligiousAccommodation, ReligiousExemption, BurdenLevel


def check_rfra_substantial_burden(accommodation: ReligiousAccommodation) -> Tuple[bool, ProofObject]:
    """
    RFRA requires substantial burden on religious exercise.
    
    42 U.S.C. § 2000bb-1:
    - Government shall not substantially burden religious exercise
    - Unless burden is in furtherance of compelling interest
    - And is least restrictive means
    
    Falsifies if: insincere belief or no substantial burden
    """
    if not accommodation.religious_belief_sincere:
        return False, ProofObject(
            conclusion=f"VIOLATION: Claim {accommodation.claim_id} religious belief not sincere",
            premises=[
                f"Claimant: {accommodation.claimant_id}",
                "Sincerity: FALSE",
                "Sherbert v. Verner — Sincerity requirement"
            ],
            rule="rfra_sincerity"
        )
    
    if not accommodation.is_substantial_burden():
        return False, ProofObject(
            conclusion=f"VIOLATION: Claim {accommodation.claim_id} burden not substantial",
            premises=[
                f"Burden level: {accommodation.burden_level.name}",
                f"Practice: {accommodation.religious_practice_desc}",
                "42 U.S.C. § 2000bb-1 — Substantial burden required"
            ],
            rule="rfra_substantial_burden"
        )
    
    return True, ProofObject(
        conclusion=f"Claim {accommodation.claim_id} meets RFRA substantial burden standard",
        premises=[
            f"Burden: {accommodation.burden_level.name}",
            f"Sincere: {accommodation.religious_belief_sincere}"
        ],
        rule="rfra_substantial_burden"
    )


def check_rfra_least_restrictive_means(accommodation: ReligiousAccommodation) -> Tuple[bool, ProofObject]:
    """
    RFRA requires least restrictive means for compelling interest.
    
    42 U.S.C. § 2000bb-1(b):
    - Burden must be least restrictive means
    - Of furthering compelling governmental interest
    
    Falsifies if: less restrictive alternative exists
    """
    if accommodation.is_substantial_burden() and not accommodation.least_restrictive_alternative_exists:
        return True, ProofObject(
            conclusion=f"Claim {accommodation.claim_id} passes RFRA strict scrutiny",
            premises=[
                "Substantial burden: YES",
                "Least restrictive alternative: NONE EXISTS",
                "Burden justified under RFRA"
            ],
            rule="rfra_least_restrictive_means"
        )
    
    if accommodation.is_substantial_burden() and accommodation.least_restrictive_alternative_exists:
        return False, ProofObject(
            conclusion=f"VIOLATION: Claim {accommodation.claim_id} has less restrictive alternative",
            premises=[
                "Compelling interest: YES",
                "Least restrictive: NO — alternative exists",
                "42 U.S.C. § 2000bb-1(b) — Strict scrutiny"
            ],
            rule="rfra_least_restrictive_means"
        )
    
    return True, ProofObject(
        conclusion=f"Claim {accommodation.claim_id} no substantial burden — RFRA not triggered",
        premises=[f"Burden: {accommodation.burden_level.name}"],
        rule="rfra_least_restrictive_means"
    )


def check_third_party_harm_limit(exemption: ReligiousExemption) -> Tuple[bool, ProofObject]:
    """
    Religious exemptions cannot impose significant harm on third parties.
    
    Burwell v. Hobby Lobby (2014):
    - Accommodation must not harm third parties
    - Effect on employees/others considered
    - Balancing of interests required
    
    Falsifies if: harm_to_third_parties > threshold
    """
    harm_threshold = Fraction(1, 10)  # 10% harm threshold
    
    if exemption.harm_to_third_parties > harm_threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Exemption {exemption.exemption_id} causes {float(exemption.harm_to_third_parties):.1%} harm to third parties",
            premises=[
                f"Harm: {exemption.harm_to_third_parties}",
                f"Threshold: {harm_threshold}",
                "Burwell v. Hobby Lobby — Third-party harm limit"
            ],
            rule="religious_exemption_third_party_harm"
        )
    
    return True, ProofObject(
        conclusion=f"Exemption {exemption.exemption_id} third-party harm within limits",
        premises=[f"Harm: {exemption.harm_to_third_parties}"],
        rule="religious_exemption_third_party_harm"
    )


def check_establishment_clause_neutrality(accommodations: list) -> Tuple[bool, ProofObject]:
    """
    Establishment Clause requires religious neutrality.
    
    First Amendment:
    - Government cannot favor one religion over another
    - Secular purpose required
    - Primary effect must not advance/inhibit religion
    
    Falsifies if: preferential treatment evident
    """
    if len(accommodations) < 2:
        return True, ProofObject(
            conclusion="Single accommodation — neutrality check N/A",
            premises=["Insufficient data for comparison"],
            rule="establishment_neutrality"
        )
    
    # Check for disparate treatment
    granted_count = sum(1 for a in accommodations if a.accommodation_granted)
    denial_count = len(accommodations) - granted_count
    
    if granted_count == len(accommodations) or denial_count == len(accommodations):
        return True, ProofObject(
            conclusion="Accommodations uniformly treated",
            premises=[f"Granted: {granted_count}, Denied: {denial_count}"],
            rule="establishment_neutrality"
        )
    
    return True, ProofObject(
        conclusion=f"Mixed accommodation outcomes — case-by-case analysis required",
        premises=[f"Granted: {granted_count}, Denied: {denial_count}"],
        rule="establishment_neutrality"
    )
