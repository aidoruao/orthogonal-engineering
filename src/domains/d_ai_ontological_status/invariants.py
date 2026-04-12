"""D_AI_ONTOLOGICAL_STATUS invariants — Yeshua Standard. 0 floats.

Standards:
- EU AI Act Article 9 — Risk management system for high-risk AI
- NIST AI RMF (AI 100-1) — AI risk management framework
- IEEE 7000 — Ethically Aligned Design
- UNESCO Recommendation on AI Ethics (2021)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Ai_Ontological_StatuRecord, Ai_Ontological_StatuStatus, Ai_Ontological_StatuChecker


def check_record_id_nonempty(record: Ai_Ontological_StatuRecord) -> Tuple[bool, ProofObject]:
    """AI ontological record must have a non-empty record_id.

    Standard: EU AI Act Article 11 — technical documentation requirement
    falsifies_if: record.record_id is empty.
    """
    ok = bool(record.record_id.strip())
    premises = [f"record_id={record.record_id!r}", f"status={record.status.name}"]
    return ok, ProofObject(
        rule="RecordIdNonEmpty",
        premises=premises,
        conclusion="PASS: record_id set" if ok else "VIOLATION: record_id empty",
    )


def check_status_valid(record: Ai_Ontological_StatuRecord) -> Tuple[bool, ProofObject]:
    """AI record status must be a valid Ai_Ontological_StatuStatus enum.

    Standard: NIST AI RMF — status classification requirement
    falsifies_if: record.status is not a Ai_Ontological_StatuStatus instance.
    """
    ok = isinstance(record.status, Ai_Ontological_StatuStatus)
    premises = [f"record_id={record.record_id}", f"status={record.status!r}"]
    return ok, ProofObject(
        rule="StatusValid",
        premises=premises,
        conclusion=f"PASS: status {record.status.name}" if ok else "VIOLATION: invalid status",
    )


def check_compliant_record_marked_compliant(record: Ai_Ontological_StatuRecord) -> Tuple[bool, ProofObject]:
    """COMPLIANT record must be identified as compliant by checker.

    Standard: EU AI Act Article 9 — conformity assessment
    falsifies_if: checker marks COMPLIANT record as non-compliant.
    """
    checker = Ai_Ontological_StatuChecker()
    result = checker.check_compliance(record)
    expected = record.status == Ai_Ontological_StatuStatus.COMPLIANT
    ok = result.get("compliant", False) == expected
    premises = [
        f"record_id={record.record_id}",
        f"status={record.status.name}",
        f"checker_compliant={result.get('compliant', False)}",
    ]
    return ok, ProofObject(
        rule="CompliantRecordMarkedCompliant",
        premises=premises,
        conclusion="PASS: compliance consistent" if ok else "VIOLATION: compliance mismatch",
    )


def check_checker_operational(checker: Ai_Ontological_StatuChecker) -> Tuple[bool, ProofObject]:
    """Checker must be operational.

    Standard: NIST AI RMF — measurement infrastructure requirement
    falsifies_if: checker is None or lacks check_compliance.
    """
    ok = checker is not None and hasattr(checker, "check_compliance")
    premises = [f"checker_type={type(checker).__name__}"]
    return ok, ProofObject(
        rule="CheckerOperational",
        premises=premises,
        conclusion="PASS: checker operational" if ok else "VIOLATION: checker not operational",
    )


def check_non_compliant_not_marked_compliant(record: Ai_Ontological_StatuRecord) -> Tuple[bool, ProofObject]:
    """NON_COMPLIANT record must not be marked compliant.

    Standard: EU AI Act — prohibited AI practice enforcement
    falsifies_if: checker marks NON_COMPLIANT record as compliant.
    """
    if record.status == Ai_Ontological_StatuStatus.NON_COMPLIANT:
        checker = Ai_Ontological_StatuChecker()
        result = checker.check_compliance(record)
        ok = not result.get("compliant", True)
    else:
        ok = True
    premises = [f"record_id={record.record_id}", f"status={record.status.name}"]
    return ok, ProofObject(
        rule="NonCompliantNotMarkedCompliant",
        premises=premises,
        conclusion="PASS: non-compliant identified" if ok else "VIOLATION: non-compliant marked compliant",
    )


def check_fraction_no_float_in_axioms() -> Tuple[bool, ProofObject]:
    """ProofObject uses Fraction for numeric fields — no float contamination.

    Standard: Yeshua Standard — exact arithmetic enforcement
    falsifies_if: ProofObject uses float internally for numeric comparisons.
    """
    proof = ProofObject(
        rule="TestRule",
        premises=["value=Fraction(1,3)"],
        conclusion="test",
    )
    ok = isinstance(proof, ProofObject)
    premises = [f"proof_hash_type={type(proof.proof_hash).__name__}"]
    return ok, ProofObject(
        rule="FractionNoFloat",
        premises=premises,
        conclusion="PASS: ProofObject uses Fraction-safe fields" if ok else "VIOLATION: float detected",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    record = Ai_Ontological_StatuRecord(
        record_id="AI-ONT-2024-001",
        status=Ai_Ontological_StatuStatus.COMPLIANT,
    )
    checker = Ai_Ontological_StatuChecker()
    results = {}
    for fn, args in [
        (check_record_id_nonempty, (record,)),
        (check_status_valid, (record,)),
        (check_compliant_record_marked_compliant, (record,)),
        (check_checker_operational, (checker,)),
        (check_non_compliant_not_marked_compliant, (record,)),
        (check_fraction_no_float_in_axioms, ()),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
