"""D_PLATFORM Invariants — DSA Compliance, Content Moderation, Transparency

Verifies Digital Services Act requirements, content moderation transparency,
appeal mechanisms, VLOP obligations.

Standards: Regulation (EU) 2022/2065 (DSA), Platform Transparency laws
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ContentModeration, DigitalPlatform, ContentDecision, vlop_user_threshold


def check_vlop_designation(platform: DigitalPlatform) -> Tuple[bool, ProofObject]:
    """
    DSA designates platforms >45M EU users as VLOPs.
    
    DSA Article 25:
    - VLOPs have additional obligations
    - Risk assessments required
    - Independent audits
    
    Falsifies if: VLOP fails to meet obligations
    """
    is_vlop = platform.is_vlop()
    
    if is_vlop and not platform.transparency_report_published:
        return False, ProofObject(
            conclusion=f"VIOLATION: Platform {platform.name} is VLOP but transparency report not published",
            premises=[
                f"EU users: {platform.eu_users}",
                f"VLOP threshold: {vlop_user_threshold()}",
                f"Transparency: {platform.transparency_report_published}",
                "DSA Art. 25 — VLOP obligations"
            ],
            rule="dsa_vlop_obligations"
        )
    
    if is_vlop and not platform.ad_repository_public:
        return False, ProofObject(
            conclusion=f"VIOLATION: Platform {platform.name} VLOP without public ad repository",
            premises=[
                f"Ad repository: {platform.ad_repository_public}",
                "DSA Art. 30 — Ad transparency"
            ],
            rule="dsa_ad_repository"
        )
    
    return True, ProofObject(
        conclusion=f"Platform {platform.name} DSA VLOP obligations satisfied",
        premises=[f"VLOP: {is_vlop}"],
        rule="dsa_vlop_obligations"
    )


def check_content_appeal_mechanism(moderation: ContentModeration) -> Tuple[bool, ProofObject]:
    """
    DSA requires effective appeal mechanism.
    
    DSA Article 17:
    - Users can appeal content decisions
    - Human review for contested automated decisions
    - Timely response required
    
    Falsifies if: no appeal available
    """
    if moderation.decision == ContentDecision.NO_ACTION:
        return True, ProofObject(
            conclusion=f"Decision {moderation.decision_id} no action — appeal N/A",
            premises=["Decision: NO_ACTION"],
            rule="appeal_exemption"
        )
    
    if not moderation.appeal_available:
        return False, ProofObject(
            conclusion=f"VIOLATION: Decision {moderation.decision_id} no appeal available",
            premises=[
                f"Decision: {moderation.decision.name}",
                f"Appeal available: {moderation.appeal_available}",
                "DSA Art. 17 — Appeal mechanism"
            ],
            rule="content_appeal_mechanism"
        )
    
    return True, ProofObject(
        conclusion=f"Decision {moderation.decision_id} appeal mechanism available",
        premises=["Appeal: YES"],
        rule="content_appeal_mechanism"
    )


def check_automated_decision_oversight(moderation: ContentModeration) -> Tuple[bool, ProofObject]:
    """
    Automated content decisions require human oversight.
    
    DSA Article 16:
    - Human review for significant automated decisions
    - Human intervention available
    - Notified as automated
    
    Falsifies if: automated significant decision without oversight
    """
    if not moderation.automated:
        return True, ProofObject(
            conclusion=f"Decision {moderation.decision_id} human-made — oversight N/A",
            premises=["Automated: NO"],
            rule="automated_oversight_exemption"
        )
    
    if moderation.decision in (ContentDecision.REMOVE, ContentDecision.RESTRICT) and not moderation.human_oversight:
        return False, ProofObject(
            conclusion=f"VIOLATION: Decision {moderation.decision_id} automated {moderation.decision.name} lacks human oversight",
            premises=[
                f"Automated: {moderation.automated}",
                f"Human oversight: {moderation.human_oversight}",
                "DSA Art. 16 — Human oversight"
            ],
            rule="automated_decision_oversight"
        )
    
    return True, ProofObject(
        conclusion=f"Decision {moderation.decision_id} human oversight verified",
        premises=[f"Human oversight: {moderation.human_oversight}"],
        rule="automated_decision_oversight"
    )


def check_statement_of_reasons(moderation: ContentModeration) -> Tuple[bool, ProofObject]:
    """
    DSA requires statement of reasons for content decisions.
    
    DSA Article 17:
    - Clear explanation of decision
    - Reference to specific policy
    - Available to user
    
    Falsifies if: decision made without reason provided
    """
    if moderation.decision == ContentDecision.NO_ACTION:
        return True, ProofObject(
            conclusion=f"Decision {moderation.decision_id} no action — reasons N/A",
            premises=["Decision: NO_ACTION"],
            rule="statement_of_reasons_exemption"
        )
    
    if not moderation.reason_provided:
        return False, ProofObject(
            conclusion=f"VIOLATION: Decision {moderation.decision_id} no statement of reasons",
            premises=[
                f"Reason provided: {moderation.reason_provided}",
                f"User notified: {moderation.user_notified}",
                "DSA Art. 17 — Statement of reasons"
            ],
            rule="statement_of_reasons"
        )
    
    return True, ProofObject(
        conclusion=f"Decision {moderation.decision_id} statement of reasons provided",
        premises=["Reasons: YES"],
        rule="statement_of_reasons"
    )


def check_appeal_success_rate(platform: DigitalPlatform) -> Tuple[bool, ProofObject]:
    """
    Appeal success rate indicates moderation accuracy.
    
    Quality indicator:
    - High upheld rate (>30%) suggests over-removal
    - Very low rate (<1%) suggests appeals inaccessible
    - Trend monitoring important
    
    Falsifies if: upheld rate > 40% (indicates systemic issues)
    """
    max_upheld_rate = Fraction(4, 10)  # 40%
    
    if platform.appeals_received < 100:  # Small sample
        return True, ProofObject(
            conclusion=f"Platform {platform.name} appeal sample small ({platform.appeals_received})",
            premises=["Insufficient appeals for analysis"],
            rule="appeal_rate_exemption"
        )
    
    rate = platform.get_appeal_upheld_rate()
    
    if rate > max_upheld_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Platform {platform.name} appeal upheld rate {rate} high (>{max_upheld_rate}) — over-removal suspected",
            premises=[
                f"Appeals: {platform.appeals_received}",
                f"Upheld: {platform.appeals_upheld}",
                f"Rate: {rate}",
                "Content moderation quality — Over-removal"
            ],
            rule="appeal_success_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Platform {platform.name} appeal upheld rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="appeal_success_rate"
    )
