"""D_EDUCATION executable invariants."""

from src.domains.d_education.implementation import issue_credential, verify_credential


def check_hash_immutable() -> bool:
    c = issue_credential("s-1", {"course": "logic", "grade": "A"})
    assert verify_credential(c)
    tampered = c.__class__(student_id=c.student_id, payload={"course": "logic", "grade": "B"}, issued_hash=c.issued_hash)
    assert not verify_credential(tampered)
    return True


def check_verification_deterministic() -> bool:
    c = issue_credential("s-2", {"course": "cat", "grade": "A+"})
    r1 = verify_credential(c)
    r2 = verify_credential(c)
    assert r1 is True
    assert r1 == r2
    return True


def run_all_invariants() -> dict:
    checks = [check_hash_immutable, check_verification_deterministic]
    out = {}
    for fn in checks:
        try:
            fn()
            out[fn.__name__] = "PASS"
        except AssertionError as e:
            out[fn.__name__] = f"FAIL: {e}"
    return out
