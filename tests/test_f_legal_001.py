"""F_LEGAL_001 — citation verification and deterministic parsing."""

import pytest

from src.domains.d_legal.implementation import (
    parse_citation,
    validate_precedent_chain,
    verify_statute_reference,
)


def test_legal_citation_verifiability():
    assert verify_statute_reference("29 U.S.C. § 207")
    assert not verify_statute_reference("99 U.S.C. § 999")

    c1 = parse_citation("18 U.S.C. § 1030")
    c2 = parse_citation("18 U.S.C. § 1030")
    assert c1 == c2

    assert validate_precedent_chain(["29 U.S.C. § 207", "18 U.S.C. § 1030"])
    assert not validate_precedent_chain(["29 U.S.C. § 207", "77 U.S.C. § 1"])


def test_legal_invalid_citation_rejected():
    with pytest.raises(ValueError):
        parse_citation("29 USC 207")
    with pytest.raises(ValueError):
        parse_citation("§ 207")
    with pytest.raises(ValueError):
        parse_citation("29 U.S.C. 207")
