"""D_EDUCATION executable invariants."""

from src.domains.d_education.implementation import (
    Credential,
    deterministic_credential_fingerprint,
    issue_credential,
    issue_revised_credential,
    verify_credential,
    verify_revision_chain,
)


def check_hash_immutable() -> bool:
    c = issue_credential("s-1", {"course": "logic", "grade": "A"})
    assert verify_credential(c)
    tampered = Credential(
        student_id=c.student_id,
        payload={"course": "logic", "grade": "B"},
        issued_hash=c.issued_hash,
        issued_at_ns=c.issued_at_ns,
    )
    assert not verify_credential(tampered)
    return True


def check_verification_deterministic() -> bool:
    c = issue_credential("s-2", {"course": "cat", "grade": "A+"})
    r1 = verify_credential(c)
    r2 = verify_credential(c)
    assert r1 is True
    assert r1 == r2
    f1 = deterministic_credential_fingerprint(c)
    f2 = deterministic_credential_fingerprint(c)
    assert f1 == f2
    return True


def check_revision_chain_verifiable() -> bool:
    original = issue_credential("s-3", {"course": "proofs", "grade": "B"})
    revised, rev = issue_revised_credential(original, {"course": "proofs", "grade": "A"}, "grade appeal")
    assert verify_revision_chain(original, revised, rev)
    return True


def run_all_invariants() -> dict:
    checks = [check_hash_immutable, check_verification_deterministic, check_revision_chain_verifiable]
    out = {}
    for fn in checks:
        try:
            fn()
            out[fn.__name__] = "PASS"
        except AssertionError as e:
            out[fn.__name__] = f"FAIL: {e}"
    return out
