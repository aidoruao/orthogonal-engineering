"""D_INTERNATIONAL_CRIMINAL invariants — Yeshua Standard. 0 floats.

Standards:
- Rome Statute of the ICC (1998) — Article 5 core crimes
- Convention on Prevention and Punishment of Genocide (1948)
- 4th Geneva Convention — war crimes
- Nuremberg Charter (1945) — crimes against humanity
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, List, Tuple
from axioms.logic import ProofObject
from .implementation import Case, Evidence, CrimeType, CaseStatus


def check_charge_gravity_threshold(case: Case) -> Tuple[bool, ProofObject]:
    """Case charge gravity must meet ICC threshold for core crimes.

    Standard: Rome Statute Article 5 — jurisdiction limited to most serious crimes
    falsifies_if: case.charge_gravity < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = case.charge_gravity >= threshold
    premises = [
        f"case_id={case.case_id}",
        f"charge_gravity={case.charge_gravity}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="ChargeGravityThreshold",
        premises=premises,
        conclusion="PASS: charge gravity meets threshold" if ok else "VIOLATION: charge gravity below threshold",
    )


def check_jurisdiction_strength(case: Case) -> Tuple[bool, ProofObject]:
    """Jurisdiction strength must satisfy complementarity requirements.

    Standard: Rome Statute Article 12 — preconditions to jurisdiction
    falsifies_if: case.jurisdiction_strength < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = case.jurisdiction_strength >= threshold
    premises = [
        f"case_id={case.case_id}",
        f"jurisdiction_strength={case.jurisdiction_strength}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="JurisdictionStrength",
        premises=premises,
        conclusion="PASS: jurisdiction strength sufficient" if ok else "VIOLATION: jurisdiction strength insufficient",
    )


def check_evidence_probative_weight(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Evidence must carry sufficient probative weight.

    Standard: Rome Statute Article 64(9) — evidence admissibility and weight
    falsifies_if: evidence.evidence_weight < Fraction(1, 3).
    """
    threshold = Fraction(1, 3)
    ok = evidence.evidence_weight >= threshold
    premises = [
        f"evidence_id={evidence.evidence_id}",
        f"evidence_weight={evidence.evidence_weight}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="EvidenceProbativeWeight",
        premises=premises,
        conclusion="PASS: evidence weight sufficient" if ok else "VIOLATION: evidence weight below threshold",
    )


def check_chain_of_custody_integrity(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Chain of custody gaps must be within acceptable ratio.

    Standard: Rome Statute Rule 63 — evidence integrity and chain of custody
    falsifies_if: custody_gaps / custody_links >= Fraction(1, 4).
    """
    if evidence.custody_links <= 0:
        ratio = Fraction(1)
        ok = False
    else:
        ratio = Fraction(evidence.custody_gaps, evidence.custody_links)
        ok = ratio < Fraction(1, 4)
    premises = [
        f"evidence_id={evidence.evidence_id}",
        f"custody_gaps={evidence.custody_gaps}",
        f"custody_links={evidence.custody_links}",
        f"gap_ratio={ratio}",
    ]
    return ok, ProofObject(
        rule="ChainOfCustodyIntegrity",
        premises=premises,
        conclusion=f"PASS: gap ratio {ratio} < 1/4" if ok else f"VIOLATION: gap ratio {ratio} >= 1/4",
    )


def check_evidence_authenticity_composite(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Composite authenticity score must exceed threshold.

    Standard: Rome Statute Article 69 — relevance and probative value
    falsifies_if: composite_score < Fraction(1, 4).
    """
    authenticity_factor = Fraction(1) if evidence.authenticity_verified else Fraction(1, 2)
    if evidence.custody_links > 0:
        integrity_factor = Fraction(1) - Fraction(evidence.custody_gaps, evidence.custody_links)
    else:
        integrity_factor = Fraction(0)
    composite = evidence.evidence_weight * authenticity_factor * integrity_factor
    threshold = Fraction(1, 4)
    ok = composite >= threshold
    premises = [
        f"evidence_id={evidence.evidence_id}",
        f"evidence_weight={evidence.evidence_weight}",
        f"authenticity_factor={authenticity_factor}",
        f"integrity_factor={integrity_factor}",
        f"composite={composite}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="EvidenceAuthenticityComposite",
        premises=premises,
        conclusion=f"PASS: composite {composite} >= 1/4" if ok else f"VIOLATION: composite {composite} < 1/4",
    )


def check_case_evidence_ratio(case: Case, evidence_list: List[Evidence]) -> Tuple[bool, ProofObject]:
    """Total evidence weight must be proportionate to charge gravity.

    Standard: Rome Statute Article 53 — evidence threshold for prosecution
    falsifies_if: total_evidence_weight / charge_gravity < Fraction(1, 2).
    """
    total_weight = sum(e.evidence_weight for e in evidence_list)
    if case.charge_gravity <= Fraction(0):
        ok = False
        ratio = Fraction(0)
    else:
        ratio = total_weight / case.charge_gravity
        ok = ratio >= Fraction(1, 2)
    premises = [
        f"case_id={case.case_id}",
        f"charge_gravity={case.charge_gravity}",
        f"total_evidence_weight={total_weight}",
        f"ratio={ratio}",
    ]
    return ok, ProofObject(
        rule="CaseEvidenceRatio",
        premises=premises,
        conclusion=f"PASS: ratio {ratio} >= 1/2" if ok else f"VIOLATION: ratio {ratio} < 1/2",
    )


def check_defendant_evidence_linkage(case: Case, evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Named defendant must have linked evidence with positive weight.

    Standard: Rome Statute Article 58 — arrest warrant requires supporting evidence
    falsifies_if: defendant named AND (evidence.case_id != case.case_id OR evidence.evidence_weight <= 0).
    """
    if not case.defendant.strip():
        ok = True
        reason = "no defendant named"
    elif evidence.case_id != case.case_id:
        ok = False
        reason = "evidence not linked to case"
    elif evidence.evidence_weight <= Fraction(0):
        ok = False
        reason = "evidence weight non-positive"
    else:
        ok = True
        reason = "defendant linked to weighted evidence"
    premises = [
        f"case_id={case.case_id}",
        f"defendant={case.defendant!r}",
        f"evidence_case_id={evidence.case_id}",
        f"evidence_weight={evidence.evidence_weight}",
    ]
    return ok, ProofObject(
        rule="DefendantEvidenceLinkage",
        premises=premises,
        conclusion=f"PASS: {reason}" if ok else f"VIOLATION: {reason}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    crime = list(CrimeType)[0]
    status = list(CaseStatus)[0]
    case = Case(
        case_id="ICC-2024-001",
        crime_type=crime,
        status=status,
        opened_at=datetime(2024, 1, 1),
        defendant="John Doe",
        jurisdiction="International Criminal Court",
        charge_gravity=Fraction(1, 1),
        jurisdiction_strength=Fraction(1, 1),
    )
    evidence = Evidence(
        evidence_id="EV-001",
        case_id="ICC-2024-001",
        type="documentary",
        authenticity_verified=True,
        evidence_weight=Fraction(1, 1),
        custody_links=4,
        custody_gaps=0,
    )
    evidence_light = Evidence(
        evidence_id="EV-002",
        case_id="ICC-2024-001",
        type="testimonial",
        authenticity_verified=True,
        evidence_weight=Fraction(1, 2),
        custody_links=2,
        custody_gaps=0,
    )
    results = {}
    for fn, args in [
        (check_charge_gravity_threshold, (case,)),
        (check_jurisdiction_strength, (case,)),
        (check_evidence_probative_weight, (evidence,)),
        (check_chain_of_custody_integrity, (evidence,)),
        (check_evidence_authenticity_composite, (evidence,)),
        (check_case_evidence_ratio, (case, [evidence, evidence_light])),
        (check_defendant_evidence_linkage, (case, evidence)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
