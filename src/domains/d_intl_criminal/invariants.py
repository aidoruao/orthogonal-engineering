"""D_INTL_CRIMINAL invariants — Yeshua Standard. 0 floats.

Standards:
- Rome Statute of the ICC (1998)
- Universal Jurisdiction principle (VCLT Article 2)
- Nuremberg Principles (1950)
- UN Convention Against Torture (CAT, 1984)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import UniversalJurisdictionCase, CoreCrime


def check_case_has_evidence(case: UniversalJurisdictionCase) -> Tuple[bool, ProofObject]:
    """Case must have evidence present to proceed.

    Standard: Rome Statute Article 53 — evidence threshold for prosecution
    falsifies_if: case.evidence_present is False.
    """
    ok = case.evidence_present
    premises = [
        f"case_id={case.case_id}",
        f"suspect={case.suspect}",
        f"evidence_present={case.evidence_present}",
    ]
    return ok, ProofObject(
        rule="CaseHasEvidence",
        premises=premises,
        conclusion="PASS: evidence present" if ok else "VIOLATION: no evidence — case cannot proceed",
    )


def check_case_id_nonempty(case: UniversalJurisdictionCase) -> Tuple[bool, ProofObject]:
    """Case must have a non-empty case_id for tracking.

    Standard: ICC Registry Rule 8 — case identification
    falsifies_if: case.case_id is empty.
    """
    ok = bool(case.case_id.strip())
    premises = [f"case_id={case.case_id!r}"]
    return ok, ProofObject(
        rule="CaseIdNonEmpty",
        premises=premises,
        conclusion="PASS: case_id set" if ok else "VIOLATION: case_id empty",
    )


def check_suspect_identified(case: UniversalJurisdictionCase) -> Tuple[bool, ProofObject]:
    """Case must identify the suspect.

    Standard: Rome Statute Article 58 — arrest warrant requires identified suspect
    falsifies_if: case.suspect is empty.
    """
    ok = bool(case.suspect.strip())
    premises = [f"case_id={case.case_id}", f"suspect={case.suspect!r}"]
    return ok, ProofObject(
        rule="SuspectIdentified",
        premises=premises,
        conclusion="PASS: suspect identified" if ok else "VIOLATION: suspect not identified",
    )


def check_core_crime_is_valid_enum(crime: CoreCrime) -> Tuple[bool, ProofObject]:
    """CoreCrime must be a valid enum member.

    Standard: Rome Statute Article 5 — jurisdiction over core crimes
    falsifies_if: crime is not a CoreCrime instance.
    """
    ok = isinstance(crime, CoreCrime)
    premises = [f"crime={crime!r}"]
    return ok, ProofObject(
        rule="CoreCrimeValidEnum",
        premises=premises,
        conclusion=f"PASS: valid CoreCrime {crime.name if ok else crime}" if ok else "VIOLATION: invalid crime type",
    )


def check_location_nonempty(case: UniversalJurisdictionCase) -> Tuple[bool, ProofObject]:
    """Case must have a non-empty location for jurisdiction determination.

    Standard: Rome Statute Article 12 — territorial jurisdiction
    falsifies_if: case.location is empty.
    """
    ok = bool(case.location.strip())
    premises = [f"case_id={case.case_id}", f"location={case.location!r}"]
    return ok, ProofObject(
        rule="LocationNonEmpty",
        premises=premises,
        conclusion="PASS: location set" if ok else "VIOLATION: location empty",
    )


def check_evidence_and_suspect_consistent(case: UniversalJurisdictionCase) -> Tuple[bool, ProofObject]:
    """Evidence must be present if a named suspect exists.

    Standard: Rome Statute Article 66 — presumption of innocence requires evidence before proceeding
    falsifies_if: case.suspect is non-empty but case.evidence_present is False.
    """
    if case.suspect.strip():
        ok = case.evidence_present
    else:
        ok = True
    premises = [
        f"suspect={case.suspect!r}",
        f"evidence_present={case.evidence_present}",
    ]
    return ok, ProofObject(
        rule="EvidenceSuspectConsistent",
        premises=premises,
        conclusion="PASS: evidence consistent with suspect" if ok else "VIOLATION: named suspect but no evidence",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    crime = list(CoreCrime)[0]
    case = UniversalJurisdictionCase(
        case_id="ICC-2024-001",
        crime=crime,
        suspect="John Doe",
        location="The Hague",
        evidence_present=True,
    )
    results = {}
    for fn, args in [
        (check_case_has_evidence, (case,)),
        (check_case_id_nonempty, (case,)),
        (check_suspect_identified, (case,)),
        (check_core_crime_is_valid_enum, (crime,)),
        (check_location_nonempty, (case,)),
        (check_evidence_and_suspect_consistent, (case,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
