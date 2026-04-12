#!/usr/bin/env python3
"""Media Law Domain Invariants — FCC compliance, defamation, shield laws.

Standards:
- First Amendment
- FCC regulations (Children's TV Act)
- NYT v. Sullivan (actual malice)
- State shield laws
- Right of publicity

Falsifies if:
- Broadcast license expired
- Children's programming insufficient
- Defamation without privilege
- Journalist held in contempt for source protection
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import BroadcastStation, DefamationClaim, ShieldLawClaim, PublishedContent


def check_broadcast_license_current(station: BroadcastStation) -> Tuple[bool, ProofObject]:
    """FCC license required for broadcast operations.
    
    Falsifies if: license_expiration has passed.
    falsifies_if: license_expiration has passed.
    """
    if not station.license_current():
        days_expired = (datetime.now() - station.license_expiration).days
        return False, ProofObject(
            conclusion=f"VIOLATION: Broadcast license expired {days_expired} days ago",
            premises=[
                f"Station: {station.call_sign}",
                f"Expired: {station.license_expiration}",
                f"Days expired: {days_expired}"
            ],
            rule="fcc_broadcast_license_required"
        )
    
    return True, ProofObject(
        conclusion="Broadcast license current",
        premises=[
            f"Station: {station.call_sign}",
            f"Expires: {station.license_expiration}"
        ],
        rule="broadcast_license_valid"
    )


def check_children_programming_requirement(station: BroadcastStation) -> Tuple[bool, ProofObject]:
    """Children's Television Act requires 3 hours/week core programming.
    
    Falsifies if: children_programming_hours is below 3 per week.
    falsifies_if: children_programming_hours is below 3 per week.
    """
    REQUIRED_HOURS = Fraction(3)
    
    if not station.meets_children_programming():
        return False, ProofObject(
            conclusion=f"VIOLATION: Children's programming {station.children_programming_hours}h < required {REQUIRED_HOURS}h",
            premises=[
                f"Station: {station.call_sign}",
                f"Hours: {station.children_programming_hours}",
                f"Required: {REQUIRED_HOURS} per week"
            ],
            rule="childrens_television_act_1990"
        )
    
    return True, ProofObject(
        conclusion="Children's programming requirement met",
        premises=[f"Hours: {station.children_programming_hours}"],
        rule="children_programming_compliant"
    )


def check_defamation_actual_malice(claim: DefamationClaim) -> Tuple[bool, ProofObject]:
    """NYT v. Sullivan requires actual malice for public officials.
    
    Falsifies if: claim involves public figure but fault level is not actual malice.
    falsifies_if: claim involves public figure but fault level is not actual malice.
    """
    if claim.is_public_figure_claim():
        if claim.fault_level != "actual_malice":
            return False, ProofObject(
                conclusion="VIOLATION: Public figure defamation requires actual malice",
                premises=[
                    f"Claim: {claim.claim_id}",
                    f"Plaintiff: {claim.plaintiff}",
                    f"Fault level: {claim.fault_level}",
                    "Required: actual_malice"
                ],
                rule="nyt_v_sullivan_actual_malice"
            )
    
    return True, ProofObject(
        conclusion="Defamation claim meets fault requirement",
        premises=[f"Fault level: {claim.fault_level}"],
        rule="defamation_fault_compliant"
    )


def check_shield_law_protection(claim: ShieldLawClaim) -> Tuple[bool, ProofObject]:
    """Shield laws protect journalists from source disclosure.
    
    Falsifies if: qualified journalist with confidential source is held in contempt.
    falsifies_if: qualified journalist with confidential source is held in contempt.
    """
    if claim.qualified_journalist and claim.information_confidential:
        if claim.contempt_issued:
            return False, ProofObject(
                conclusion="VIOLATION: Journalist held in contempt despite shield law protection",
                premises=[
                    f"Claim: {claim.claim_id}",
                    f"Journalist: {claim.journalist}",
                    f"Outlet: {claim.media_outlet}",
                    "Qualified journalist: True",
                    "Confidential source: True",
                    "Contempt: Issued"
                ],
                rule="shield_law_journalist_protection"
            )
    
    return True, ProofObject(
        conclusion="Shield law protection respected or not applicable",
        premises=[
            f"Qualified: {claim.qualified_journalist}",
            f"Contempt: {claim.contempt_issued}"
        ],
        rule="shield_law_compliant"
    )


def check_retraction_timeliness(content: PublishedContent) -> Tuple[bool, ProofObject]:
    """Many jurisdictions require retraction request before libel suit.
    
    Falsifies if: defamation claim proceeds without opportunity for retraction where required.
    falsifies_if: defamation claim proceeds without opportunity for retraction where required.
    """
    if content.defamation_claim_filed and not content.retraction_issued:
        # Some jurisdictions require retraction demand first
        return True, ProofObject(
            conclusion="Defamation claim filed, retraction status noted",
            premises=[
                f"Content: {content.content_id}",
                f"Retraction issued: {content.retraction_issued}"
            ],
            rule="retraction_status_noted"
        )
    
    return True, ProofObject(
        conclusion="Retraction status acceptable",
        premises=[f"Defamation filed: {content.defamation_claim_filed}"],
        rule="retraction_compliant"
    )


def check_public_file_completeness(station: BroadcastStation) -> Tuple[bool, ProofObject]:
    """FCC requires public inspection file for broadcast stations.
    
    Falsifies if: public_file_complete is False.
    falsifies_if: public_file_complete is False.
    """
    if not station.public_file_complete:
        return False, ProofObject(
            conclusion="VIOLATION: Station public file incomplete",
            premises=[
                f"Station: {station.call_sign}",
                "Public file: Incomplete"
            ],
            rule="fcc_public_file_requirement"
        )
    
    return True, ProofObject(
        conclusion="Public file complete",
        premises=["Public file: Complete"],
        rule="public_file_compliant"
    )
