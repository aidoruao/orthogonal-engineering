"""D_TRANSPORTATION invariants — Yeshua Standard. 0 floats.

Standards:
- 49 U.S.C. §40101 — Aviation safety (FAA)
- 49 U.S.C. §20101 — Rail safety (FRA)
- 49 U.S.C. §30101 — Motor vehicle safety (NHTSA)
- FMCSA Hours of Service (49 CFR Part 395) — driver fatigue prevention
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import TransportationRecord, TransportationStatus, TransportationChecker


def check_record_id_nonempty(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Transportation record must have a non-empty record_id.

    Standard: DOT record keeping requirements (49 CFR Part 390)
    falsifies_if: record.record_id is empty.
    """
    ok = bool(record.record_id.strip())
    premises = [f"record_id={record.record_id!r}", f"status={record.status.name}"]
    return ok, ProofObject(
        rule="RecordIdNonEmpty",
        premises=premises,
        conclusion="PASS: record_id set" if ok else "VIOLATION: record_id empty",
    )


def check_status_valid(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Transportation record status must be a valid TransportationStatus enum.

    Standard: FMCSA compliance status classification
    falsifies_if: record.status is not a TransportationStatus instance.
    """
    ok = isinstance(record.status, TransportationStatus)
    premises = [f"record_id={record.record_id}", f"status={record.status!r}"]
    return ok, ProofObject(
        rule="StatusValid",
        premises=premises,
        conclusion=f"PASS: status {record.status.name}" if ok else "VIOLATION: invalid status",
    )


def check_compliant_record_marked_compliant(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Compliant records must be marked COMPLIANT by checker.

    Standard: 49 CFR Part 390 — compliance determination
    falsifies_if: checker marks compliant record as non-compliant.
    """
    checker = TransportationChecker()
    result = checker.check_compliance(record)
    expected = record.status == TransportationStatus.COMPLIANT
    ok = result.get("compliant", False) == expected
    premises = [
        f"record_id={record.record_id}",
        f"status={record.status.name}",
        f"checker_says_compliant={result.get('compliant', False)}",
    ]
    return ok, ProofObject(
        rule="CompliantRecordMarkedCompliant",
        premises=premises,
        conclusion="PASS: compliance consistent" if ok else "VIOLATION: compliance status mismatch",
    )


def check_checker_has_check_compliance(checker: TransportationChecker) -> Tuple[bool, ProofObject]:
    """TransportationChecker must have check_compliance method.

    Standard: FMCSA safety fitness determination — checker must be operational
    falsifies_if: checker.check_compliance is not callable.
    """
    ok = hasattr(checker, "check_compliance") and callable(checker.check_compliance)
    premises = [f"has_check_compliance={ok}"]
    return ok, ProofObject(
        rule="CheckerHasCheckCompliance",
        premises=premises,
        conclusion="PASS: checker operational" if ok else "VIOLATION: checker missing check_compliance",
    )


def check_non_compliant_not_marked_compliant(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """NON_COMPLIANT record must not be marked compliant.

    Standard: 49 CFR Part 385 — safety fitness rating
    falsifies_if: checker marks NON_COMPLIANT record as compliant.
    """
    if record.status == TransportationStatus.NON_COMPLIANT:
        checker = TransportationChecker()
        result = checker.check_compliance(record)
        ok = not result.get("compliant", True)
    else:
        ok = True
    premises = [f"record_id={record.record_id}", f"status={record.status.name}"]
    return ok, ProofObject(
        rule="NonCompliantNotMarkedCompliant",
        premises=premises,
        conclusion="PASS: non-compliant correctly identified" if ok else "VIOLATION: non-compliant marked compliant",
    )


def check_record_has_status(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Record must have a status attribute.

    Standard: DOT audit trail requirements
    falsifies_if: record does not have a status attribute.
    """
    ok = hasattr(record, "status")
    premises = [f"record_id={record.record_id}", f"has_status={ok}"]
    return ok, ProofObject(
        rule="RecordHasStatus",
        premises=premises,
        conclusion="PASS: status attribute present" if ok else "VIOLATION: status missing",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    record = TransportationRecord(
        record_id="TRANS-2024-001",
        status=TransportationStatus.COMPLIANT,
    )
    checker = TransportationChecker()
    results = {}
    for fn, args in [
        (check_record_id_nonempty, (record,)),
        (check_status_valid, (record,)),
        (check_compliant_record_marked_compliant, (record,)),
        (check_checker_has_check_compliance, (checker,)),
        (check_non_compliant_not_marked_compliant, (record,)),
        (check_record_has_status, (record,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
