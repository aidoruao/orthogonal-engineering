"""F_EDUCATION_001 — credential immutability and determinism."""

from src.domains.d_education.implementation import issue_credential, verify_credential


def test_credential_hash_immutable_and_deterministic():
    cred = issue_credential("student-1", {"course": "logic", "grade": "A"})
    assert verify_credential(cred)
    assert verify_credential(cred)

    tampered = cred.__class__(
        student_id=cred.student_id,
        payload={"course": "logic", "grade": "B"},
        issued_hash=cred.issued_hash,
    )
    assert not verify_credential(tampered)
