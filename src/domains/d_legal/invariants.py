"""D_LEGAL executable invariants."""

from src.domains.d_legal.implementation import (
    parse_citation,
    validate_precedent_chain,
    verify_statute_reference,
)


def check_citation_resolves() -> bool:
    assert verify_statute_reference("29 U.S.C. § 207")
    assert not verify_statute_reference("99 U.S.C. § 999")
    return True


def check_parser_deterministic() -> bool:
    r = "18 U.S.C. § 1030"
    c1 = parse_citation(r)
    c2 = parse_citation(r)
    assert c1 == c2
    return True


def check_precedent_chain_verifiable() -> bool:
    chain = ["29 U.S.C. § 207", "18 U.S.C. § 1030"]
    assert validate_precedent_chain(chain)
    assert not validate_precedent_chain(chain + ["77 U.S.C. § 1"])
    return True


def run_all_invariants() -> dict:
    checks = [check_citation_resolves, check_parser_deterministic, check_precedent_chain_verifiable]
    out = {}
    for fn in checks:
        try:
            fn()
            out[fn.__name__] = "PASS"
        except AssertionError as e:
            out[fn.__name__] = f"FAIL: {e}"
    return out
