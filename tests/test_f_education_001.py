"""F_EDUCATION_001 — credential immutability and determinism."""

from src.domains.d_education.implementation import (
    Credential,
    deterministic_credential_fingerprint,
    issue_credential,
    issue_revised_credential,
    verify_credential,
    verify_revision_chain,
)


def test_credential_hash_immutable_and_deterministic():
    cred = issue_credential("student-1", {"course": "logic", "grade": "A"})
    assert verify_credential(cred)
    assert verify_credential(cred)
    assert deterministic_credential_fingerprint(cred) == deterministic_credential_fingerprint(cred)

    tampered = Credential(
        student_id=cred.student_id,
        payload={"course": "logic", "grade": "B"},
        issued_hash=cred.issued_hash,
        issued_at_ns=cred.issued_at_ns,
    )
    assert not verify_credential(tampered)


def test_credential_revision_chain_verifiable():
    base = issue_credential("student-2", {"course": "cat", "grade": "B"})
    revised, revision = issue_revised_credential(base, {"course": "cat", "grade": "A"}, "appeal")
    assert verify_revision_chain(base, revised, revision)
