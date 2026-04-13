"""D_FBI_TRAINING invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes FBI Quantico training,
DOJ use-of-force policy, and Fed. R. Evid. 901 chain-of-custody integrity.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    EvidenceItem,
    AgentCertification,
    UseOfForceReport,
    DigitalForensicArtifact,
)


def check_chain_of_custody(evidence: EvidenceItem) -> Tuple[bool, ProofObject]:
    """
    Rule: Evidence must have unbroken chain of custody and matching hashes (FBI DIOG, FRE 901).

    falsifies_if: current_hash != hash_at_collection OR chain_of_custody is empty OR sealed is False.
    """
    unbroken_chain = len(evidence.chain_of_custody) > 0
    hash_matches = evidence.current_hash == evidence.hash_at_collection
    sealed = evidence.sealed

    if not (unbroken_chain and hash_matches and sealed):
        return False, ProofObject(
            rule="chain_of_custody_integrity",
            premises=[
                f"item_id={evidence.item_id}",
                f"chain_length={len(evidence.chain_of_custody)}",
                f"hash_match={hash_matches}",
                f"sealed={sealed}",
            ],
            conclusion="VIOLATION: Chain of custody broken or hash mismatch or evidence unsealed",
        )

    return True, ProofObject(
        rule="chain_of_custody_integrity",
        premises=[
            f"item_id={evidence.item_id}",
            f"chain_length={len(evidence.chain_of_custody)}",
            "hash_match=True",
            "sealed=True",
        ],
        conclusion="Chain of custody intact with matching hashes and seal applied",
    )


def check_agent_certification_valid(
    cert: AgentCertification,
    current_time: Fraction,
) -> Tuple[bool, ProofObject]:
    """
    Rule: Agent certification must meet passing threshold, be unexpired, and be witnessed (FBI Academy quals).

    falsifies_if: exam_score < pass_threshold OR current_time > expiry_date OR witnessed is False.
    """
    passing = cert.exam_score >= cert.pass_threshold
    valid_time = current_time <= cert.expiry_date
    witnessed = cert.witnessed

    if not (passing and valid_time and witnessed):
        return False, ProofObject(
            rule="agent_certification_valid",
            premises=[
                f"agent_id={cert.agent_id}",
                f"score={cert.exam_score}",
                f"threshold={cert.pass_threshold}",
                f"current_time={current_time}",
                f"expiry={cert.expiry_date}",
                f"witnessed={cert.witnessed}",
            ],
            conclusion="VIOLATION: Certification failing, expired, or unwitnessed",
        )

    return True, ProofObject(
        rule="agent_certification_valid",
        premises=[
            f"agent_id={cert.agent_id}",
            f"score={cert.exam_score}",
            f"threshold={cert.pass_threshold}",
            f"current_time={current_time}",
            f"expiry={cert.expiry_date}",
            "witnessed=True",
        ],
        conclusion="Certification valid, within date, and independently witnessed",
    )


def check_use_of_force_proportional(report: UseOfForceReport) -> Tuple[bool, ProofObject]:
    """
    Rule: Use of force must stay within authorized proportionality ratio and include de-escalation attempt (DOJ policy).

    falsifies_if: proportionality_ratio > max_authorized_ratio OR de_escalation_attempted is False.
    """
    proportional = report.proportionality_ratio <= report.max_authorized_ratio
    de_escalated = report.de_escalation_attempted

    if not (proportional and de_escalated):
        return False, ProofObject(
            rule="use_of_force_proportional",
            premises=[
                f"report_id={report.report_id}",
                f"force_level={report.force_level}",
                f"threat_level={report.threat_level}",
                f"ratio={report.proportionality_ratio}",
                f"max_ratio={report.max_authorized_ratio}",
                f"de_escalation_attempted={report.de_escalation_attempted}",
            ],
            conclusion="VIOLATION: Force disproportionate or no de-escalation attempt documented",
        )

    return True, ProofObject(
        rule="use_of_force_proportional",
        premises=[
            f"report_id={report.report_id}",
            f"ratio={report.proportionality_ratio}",
            f"max_ratio={report.max_authorized_ratio}",
            "de_escalation_attempted=True",
        ],
        conclusion="Use of force proportional to threat with de-escalation attempted",
    )


def check_witness_verification(report: UseOfForceReport) -> Tuple[bool, ProofObject]:
    """
    Rule: Use-of-force events require at least two witnesses (FBI shooting review policy).

    falsifies_if: len(witnesses) < 2.
    """
    witness_count = len(report.witnesses)
    has_minimum_witnesses = witness_count >= 2

    if not has_minimum_witnesses:
        return False, ProofObject(
            rule="witness_verification",
            premises=[
                f"report_id={report.report_id}",
                f"witness_count={witness_count}",
            ],
            conclusion="VIOLATION: Fewer than two witnesses recorded for use-of-force event",
        )

    return True, ProofObject(
        rule="witness_verification",
        premises=[
            f"report_id={report.report_id}",
            f"witness_count={witness_count}",
        ],
        conclusion="Use-of-force report contains required witness minimum",
    )


def check_digital_forensic_integrity(
    artifact: DigitalForensicArtifact,
) -> Tuple[bool, ProofObject]:
    """
    Rule: Digital evidence hash must match extraction hash and examiner identity is recorded (FBI CART, NIST SP 800-86).

    falsifies_if: current_hash != hash_at_extraction OR examiner_id is empty.
    """
    hash_preserved = artifact.current_hash == artifact.hash_at_extraction
    examiner_recorded = artifact.examiner_id != ""

    if not (hash_preserved and examiner_recorded):
        return False, ProofObject(
            rule="digital_forensic_integrity",
            premises=[
                f"artifact_id={artifact.artifact_id}",
                f"hash_preserved={hash_preserved}",
                f"examiner_recorded={examiner_recorded}",
            ],
            conclusion="VIOLATION: Digital evidence hash changed or examiner missing",
        )

    return True, ProofObject(
        rule="digital_forensic_integrity",
        premises=[
            f"artifact_id={artifact.artifact_id}",
            "hash_preserved=True",
            "examiner_recorded=True",
        ],
        conclusion="Digital forensic artifact retains hash with recorded examiner",
    )


def check_training_record_witnessed(cert: AgentCertification) -> Tuple[bool, ProofObject]:
    """
    Rule: Training and certification records must be independently witnessed (Quantico verification logs).

    falsifies_if: witnessed is False OR witness_id is empty.
    """
    has_witness = cert.witnessed and cert.witness_id != ""

    if not has_witness:
        return False, ProofObject(
            rule="training_record_witnessed",
            premises=[
                f"agent_id={cert.agent_id}",
                f"witnessed={cert.witnessed}",
                f"witness_id={cert.witness_id}",
            ],
            conclusion="VIOLATION: Training record lacks independent witness",
        )

    return True, ProofObject(
        rule="training_record_witnessed",
        premises=[
            f"agent_id={cert.agent_id}",
            f"witness_id={cert.witness_id}",
        ],
        conclusion="Training record witnessed and traceable",
    )


def check_evidence_sealed(evidence: EvidenceItem) -> Tuple[bool, ProofObject]:
    """
    Rule: Evidence must be sealed after collection before transfer (FBI DIOG chain of custody).

    falsifies_if: sealed is False AND chain_of_custody length > 1.
    """
    sealed = evidence.sealed
    multiple_handlers = len(evidence.chain_of_custody) > 1

    if (not sealed) and multiple_handlers:
        return False, ProofObject(
            rule="evidence_sealed",
            premises=[
                f"item_id={evidence.item_id}",
                f"chain_length={len(evidence.chain_of_custody)}",
                "sealed=False",
            ],
            conclusion="VIOLATION: Evidence transferred without seal across handlers",
        )

    return True, ProofObject(
        rule="evidence_sealed",
        premises=[
            f"item_id={evidence.item_id}",
            f"chain_length={len(evidence.chain_of_custody)}",
            f"sealed={sealed}",
        ],
        conclusion="Evidence appropriately sealed for custody transfers",
    )


def run_all_invariants() -> dict:
    """Run all D_FBI_TRAINING invariants with nominal sample data.

    Falsifies if: any FBI training invariant fails or raises an exception.
    falsifies_if: any FBI training invariant fails or raises an exception.
    """
    evidence = EvidenceItem(
        item_id="EV-001",
        collector_id="AGENT-001",
        timestamp=Fraction(0),
        chain_of_custody=("AGENT-001",),
        hash_at_collection="abc123",
        current_hash="abc123",
        sealed=True,
    )
    cert = AgentCertification(
        agent_id="AGENT-001",
        certification_type="firearms",
        exam_score=Fraction(9, 10),
        pass_threshold=Fraction(7, 10),
        exam_date=Fraction(0),
        expiry_date=Fraction(100),
        witnessed=True,
        witness_id="WITNESS-001",
    )
    report = UseOfForceReport(
        report_id="UOF-001",
        agent_id="AGENT-001",
        force_level=Fraction(3, 10),
        threat_level=Fraction(2, 10),
        proportionality_ratio=Fraction(3, 2),
        max_authorized_ratio=Fraction(3, 2),
        de_escalation_attempted=True,
        witnesses=("WITNESS-001", "WITNESS-002"),
        timestamp=Fraction(10),
    )
    artifact = DigitalForensicArtifact(
        artifact_id="ART-001",
        source_device="DEVICE-001",
        extraction_method="forensic-imager",
        hash_at_extraction="def456",
        current_hash="def456",
        examiner_id="EXAMINER-001",
        tool_version="1.0.0",
        timestamp=Fraction(5),
    )
    current_time = Fraction(10)

    checks = [
        ("check_chain_of_custody", lambda: check_chain_of_custody(evidence)),
        ("check_agent_certification_valid", lambda: check_agent_certification_valid(cert, current_time)),
        ("check_use_of_force_proportional", lambda: check_use_of_force_proportional(report)),
        ("check_witness_verification", lambda: check_witness_verification(report)),
        ("check_digital_forensic_integrity", lambda: check_digital_forensic_integrity(artifact)),
        ("check_training_record_witnessed", lambda: check_training_record_witnessed(cert)),
        ("check_evidence_sealed", lambda: check_evidence_sealed(evidence)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FBI_TRAINING invariants: PASS")
