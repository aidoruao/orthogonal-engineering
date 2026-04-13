"""D_INTERNATIONAL_CRIMINAL invariants — Yeshua Standard. 0 floats.

Standards:
- Rome Statute of the ICC (1998) — Article 5 core crimes
- Convention on Prevention and Punishment of Genocide (1948)
- 4th Geneva Convention — war crimes
- Nuremberg Charter (1945) — crimes against humanity
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Case, Evidence, CrimeType, CaseStatus


def check_case_has_defendant(case: Case) -> Tuple[bool, ProofObject]:
    """Case must identify a defendant.

    Standard: Rome Statute Article 58 — arrest warrant requires named accused
    falsifies_if: case.defendant is empty.
    """
    ok = bool(case.defendant.strip())
    premises = [f"case_id={case.case_id}", f"defendant={case.defendant!r}"]
    return ok, ProofObject(
        rule="CaseHasDefendant",
        premises=premises,
        conclusion="PASS: defendant identified" if ok else "VIOLATION: defendant not identified",
    )


def check_case_jurisdiction_nonempty(case: Case) -> Tuple[bool, ProofObject]:
    """Case must specify jurisdiction.

    Standard: Rome Statute Article 12 — preconditions to jurisdiction
    falsifies_if: case.jurisdiction is empty.
    """
    ok = bool(case.jurisdiction.strip())
    premises = [f"case_id={case.case_id}", f"jurisdiction={case.jurisdiction!r}"]
    return ok, ProofObject(
        rule="CaseJurisdictionNonEmpty",
        premises=premises,
        conclusion="PASS: jurisdiction set" if ok else "VIOLATION: jurisdiction empty",
    )


def check_evidence_authenticity(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Evidence must have verified authenticity.

    Standard: Rome Statute Article 64(9) — evidence admissibility
    falsifies_if: evidence.authenticity_verified is False.
    """
    ok = evidence.authenticity_verified
    premises = [
        f"evidence_id={evidence.evidence_id}",
        f"case_id={evidence.case_id}",
        f"authenticity_verified={evidence.authenticity_verified}",
    ]
    return ok, ProofObject(
        rule="EvidenceAuthenticity",
        premises=premises,
        conclusion="PASS: evidence authenticity verified" if ok else "VIOLATION: evidence authenticity not verified",
    )


def check_case_id_nonempty(case: Case) -> Tuple[bool, ProofObject]:
    """Case must have a non-empty identifier.

    Standard: ICC Registry — case identification requirement
    falsifies_if: case.case_id is empty.
    """
    ok = bool(case.case_id.strip())
    premises = [f"case_id={case.case_id!r}"]
    return ok, ProofObject(
        rule="CaseIdNonEmpty",
        premises=premises,
        conclusion="PASS: case_id set" if ok else "VIOLATION: case_id empty",
    )


def check_crime_type_is_valid(crime: CrimeType) -> Tuple[bool, ProofObject]:
    """Crime type must be a valid CrimeType enum.

    Standard: Rome Statute Article 5 — jurisdiction limited to core crimes
    falsifies_if: crime is not a CrimeType instance.
    """
    ok = isinstance(crime, CrimeType)
    premises = [f"crime={crime!r}"]
    return ok, ProofObject(
        rule="CrimeTypeValid",
        premises=premises,
        conclusion=f"PASS: {crime.name}" if ok else "VIOLATION: invalid crime type",
    )


def check_evidence_type_nonempty(evidence: Evidence) -> Tuple[bool, ProofObject]:
    """Evidence must have a non-empty type description.

    Standard: Rome Statute Rule 68 — prior recorded testimony requirements
    falsifies_if: evidence.type is empty.
    """
    ok = bool(evidence.type.strip())
    premises = [
        f"evidence_id={evidence.evidence_id}",
        f"type={evidence.type!r}",
    ]
    return ok, ProofObject(
        rule="EvidenceTypeNonEmpty",
        premises=premises,
        conclusion="PASS: evidence type documented" if ok else "VIOLATION: evidence type empty",
    )


def check_case_has_evidence(case: Case, evidence: Evidence) -> Tuple[bool, ProofObject]:
    """A case with a named defendant must carry supporting evidence.

    Standard: Rome Statute Article 53 — evidence threshold for prosecution
    falsifies_if: case.defendant is non-empty and evidence.case_id != case.case_id.
    """
    if case.defendant.strip():
        ok = evidence.case_id == case.case_id
    else:
        ok = True
    premises = [
        f"case_id={case.case_id}",
        f"defendant={case.defendant!r}",
        f"evidence_case_id={evidence.case_id}",
    ]
    return ok, ProofObject(
        rule="CaseHasEvidence",
        premises=premises,
        conclusion="PASS: evidence linked to case" if ok else "VIOLATION: missing/incorrect evidence linkage",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    from .implementation import CaseStatus
    crime = list(CrimeType)[0]
    status = list(CaseStatus)[0]
    case = Case(
        case_id="ICC-2024-001",
        crime_type=crime,
        status=status,
        opened_at=datetime(2024, 1, 1),
        defendant="John Doe",
        jurisdiction="International Criminal Court",
    )
    evidence = Evidence(
        evidence_id="EV-001",
        case_id="ICC-2024-001",
        type="documentary",
        authenticity_verified=True,
    )
    results = {}
    for fn, args in [
        (check_case_has_defendant, (case,)),
        (check_case_jurisdiction_nonempty, (case,)),
        (check_evidence_authenticity, (evidence,)),
        (check_case_id_nonempty, (case,)),
        (check_crime_type_is_valid, (crime,)),
        (check_evidence_type_nonempty, (evidence,)),
        (check_case_has_evidence, (case, evidence)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
