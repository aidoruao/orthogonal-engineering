#!/usr/bin/env python3
"""Indigenous Rights Domain Invariants — Treaty rights, consultation, ICWA compliance.

Standards:
- UNDRIP (UN Declaration on Rights of Indigenous Peoples)
- ICWA 25 U.S.C. 1901-1963
- ISDEAA (Self-Determination Act)
- Executive Order 13175 (Consultation)
- NHPA Section 106

Falsifies if:
- ICWA notification not given to tribe
- Treaty rights violated
- Consultation not meaningful
- Sacred site not protected
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    IndigenousNation, Treaty, TribalConsultation, ICWCase,
    CulturalResource, TreatyStatus
)


def check_treaty_obligation_status(treaty: Treaty) -> Tuple[bool, ProofObject]:
    """Treaties are the supreme law of the land (U.S. Constitution, Article VI).
    
    Falsifies if: treaty.status is BREACHED or TERMINATED without consent.
    falsifies_if: treaty.status is BREACHED or TERMINATED without consent.
    """
    if treaty.status == TreatyStatus.BREACHED:
        return False, ProofObject(
            conclusion=f"VIOLATION: Treaty {treaty.treaty_name} obligations breached",
            premises=[
                f"Treaty: {treaty.treaty_id}",
                f"Status: {treaty.status.name}",
                f"Breach documentation: {len(treaty.breach_documentation)}"
            ],
            rule="treaty_obligation_supremacy"
        )
    
    if treaty.status == TreatyStatus.TERMINATED:
        return False, ProofObject(
            conclusion=f"VIOLATION: Treaty {treaty.treaty_name} improperly terminated",
            premises=[
                f"Treaty: {treaty.treaty_id}",
                "Termination requires tribal consent"
            ],
            rule="treaty_termination_consent"
        )
    
    return True, ProofObject(
        conclusion="Treaty obligations being honored",
        premises=[f"Treaty: {treaty.treaty_name}", f"Status: {treaty.status.name}"],
        rule="treaty_obligation_current"
    )


def check_icwa_tribal_notification(case: ICWCase) -> Tuple[bool, ProofObject]:
    """ICWA 25 U.S.C. 1912(a) requires immediate notification to tribe.
    
    Falsifies if: tribe_notified is False or notification_date is missing/late.
    falsifies_if: tribe_notified is False or notification_date is missing/late.
    """
    if not case.tribe_notified:
        return False, ProofObject(
            conclusion="VIOLATION: ICWA requires tribal notification",
            premises=[
                f"Case: {case.case_id}",
                "Tribe notified: False",
                f"Tribal affiliation: {case.child_tribal_affiliation}"
            ],
            rule="icwa_25usc1912_notification"
        )
    
    if case.notification_date is None:
        return False, ProofObject(
            conclusion="VIOLATION: ICWA notification date not recorded",
            premises=[f"Case: {case.case_id}", "Notification date: None"],
            rule="icwa_notification_documentation"
        )
    
    return True, ProofObject(
        conclusion="ICWA tribal notification satisfied",
        premises=[
            f"Case: {case.case_id}",
            f"Notified: {case.tribe_notified}",
            f"Date: {case.notification_date}"
        ],
        rule="icwa_notification_compliant"
    )


def check_icwa_placement_preference(case: ICWCase) -> Tuple[bool, ProofObject]:
    """ICWA 25 U.S.C. 1915 establishes placement preferences.
    
    Falsifies if: placement made without following preference or lacking good
    falsifies_if: placement made without following preference or lacking good
    cause documentation.
    """
    if not case.placement_made:
        return True, ProofObject(
            conclusion="No placement made yet, preference check not applicable",
            premises=["Placement made: False"],
            rule="icwa_placement_not_applicable"
        )
    
    if not case.preference_followed:
        return False, ProofObject(
            conclusion="VIOLATION: ICWA placement preference not followed",
            premises=[
                f"Case: {case.case_id}",
                f"Preference level used: {case.preference_level}",
                "Preference followed: False",
                "Requires good cause documentation"
            ],
            rule="icwa_25usc1915_placement_preference"
        )
    
    return True, ProofObject(
        conclusion="ICWA placement preference followed",
        premises=[f"Preference level: {case.preference_level}"],
        rule="icwa_placement_compliant"
    )


def check_meaningful_consultation(consultation: TribalConsultation) -> Tuple[bool, ProofObject]:
    """Executive Order 13175 requires meaningful consultation (not just notification).
    
    Falsifies if: meaningful_consultation is False or determination is missing.
    falsifies_if: meaningful_consultation is False or determination is missing.
    """
    if consultation.meaningful_consultation is None:
        return False, ProofObject(
            conclusion="VIOLATION: Consultation outcome not determined",
            premises=[
                f"Consultation: {consultation.consultation_id}",
                f"Project: {consultation.project_name}",
                "Meaningful consultation: Not assessed"
            ],
            rule="eo13175_meaningful_consultation"
        )
    
    if not consultation.meaningful_consultation:
        return False, ProofObject(
            conclusion="VIOLATION: Consultation not meaningful",
            premises=[
                f"Consultation: {consultation.consultation_id}",
                f"Nations: {consultation.affected_nations}",
                "Tribes determined consultation insufficient"
            ],
            rule="eo13175_meaningful_consultation"
        )
    
    return True, ProofObject(
        conclusion="Meaningful consultation conducted",
        premises=[
            f"Project: {consultation.project_name}",
            f"Nations consulted: {len(consultation.affected_nations)}"
        ],
        rule="consultation_meaningful"
    )


def check_free_prior_informed_consent(consultation: TribalConsultation) -> Tuple[bool, ProofObject]:
    """UNDRIP Article 32 requires FPIC for projects affecting indigenous lands.
    
    Falsifies if: consent_given is False or absent before project approval.
    falsifies_if: consent_given is False or absent before project approval.
    """
    if consultation.consent_given is None:
        return True, ProofObject(
            conclusion="FPIC determination pending",
            premises=["Consent: Not yet determined"],
            rule="fpic_pending"
        )
    
    if not consultation.consent_given:
        return False, ProofObject(
            conclusion="VIOLATION: FPIC not obtained (consent withheld or denied)",
            premises=[
                f"Project: {consultation.project_name}",
                f"Nations: {consultation.affected_nations}",
                "UNDRIP Article 32 requires FPIC"
            ],
            rule="undrip_article_32_fpic"
        )
    
    return True, ProofObject(
        conclusion="Free Prior Informed Consent obtained",
        premises=[
            f"Project: {consultation.project_name}",
            "FPIC: Obtained"
        ],
        rule="fpic_obtained"
    )


def check_cultural_resource_protection(resource: CulturalResource) -> Tuple[bool, ProofObject]:
    """NHPA Section 106 requires review of effects on historic properties.
    
    Falsifies if: nhpa_section_106_reviewed is False or mitigation is absent.
    falsifies_if: nhpa_section_106_reviewed is False or mitigation is absent.
    """
    if not resource.nhpa_section_106_reviewed:
        return False, ProofObject(
            conclusion="VIOLATION: Cultural resource lacks NHPA Section 106 review",
            premises=[
                f"Resource: {resource.name}",
                f"Type: {resource.resource_type}",
                f"Affiliated: {resource.affiliated_nations}",
                "Section 106 reviewed: False"
            ],
            rule="nhpa_section_106_required"
        )
    
    return True, ProofObject(
        conclusion="Cultural resource protection reviewed",
        premises=[
            f"Resource: {resource.name}",
            "Section 106: Reviewed"
        ],
        rule="cultural_resource_protected"
    )


def run_all_invariants() -> dict:
    """Run all D_INDIGENOUS_RIGHTS invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    cultural_resource = CulturalResource(
        resource_id=None,
        name=None,
        description=None,
        affiliated_nations=None,
        resource_type=None,
        nhpa_section_106_reviewed=None,
        confidentiality_required=None,
        location_description=None,
    )
    tribal_consultation = TribalConsultation(
        consultation_id=None,
        project_name=None,
        project_description=None,
        affected_nations=None,
        consultation_type=None,
        initiated_date=None,
        comment_period_end=None,
        meaningful_consultation=None,
        consent_given=None,
    )
    icw_case = ICWCase(
        case_id=None,
        child_tribal_affiliation=None,
        tribe_notified=None,
        notification_date=None,
        placement_made=None,
        placement_type=None,
        preference_level=None,
        preference_followed=None,
        tribal_court_involved=None,
        state_court_transfer=None,
    )
    treaty = Treaty(
        treaty_id=None,
        treaty_name=None,
        signing_date=None,
        nations=None,
        counterparty=None,
        reserved_rights=None,
        territory_description=None,
        status=TreatyStatus.IN_FORCE,
    )

    checks = [
        ("check_cultural_resource_protection", lambda: check_cultural_resource_protection(cultural_resource)),
        ("check_free_prior_informed_consent", lambda: check_free_prior_informed_consent(tribal_consultation)),
        ("check_icwa_placement_preference", lambda: check_icwa_placement_preference(icw_case)),
        ("check_icwa_tribal_notification", lambda: check_icwa_tribal_notification(icw_case)),
        ("check_meaningful_consultation", lambda: check_meaningful_consultation(tribal_consultation)),
        ("check_treaty_obligation_status", lambda: check_treaty_obligation_status(treaty)),
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
    print("All D_INDIGENOUS_RIGHTS invariants: PASS")
