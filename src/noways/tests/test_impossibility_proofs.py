"""Falsification tests for the impossibility-proof catalog."""
from fractions import Fraction

import pytest

from src.noways.impossibility_proofs import (
    Noway,
    by_key,
    catalog,
    check_catalog_size_at_floor,
    check_certainty_bounded,
    check_domains_covered,
    check_every_entry_has_falsifier,
    check_keys_unique,
    run_all_invariants,
)


def test_catalog_has_fifteen_entries() -> None:
    # TODO: Expand test_catalog_has_fifteen_entries() - stub detected by Yeshua Agent
    assert len(catalog()) >= 15


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) == 5
    for _name, success, _proof in results:
        assert success is True


def test_by_key_roundtrip() -> None:
    entry = by_key("halting")
    assert isinstance(entry, Noway)
    assert entry.domain == "computability"


def test_by_key_missing_raises() -> None:
    with pytest.raises(KeyError):
        by_key("this-key-does-not-exist")


def test_required_domains_all_present() -> None:
    required = {
        "computability", "logic", "physics", "quantum",
        "relativity", "distributed", "thermodynamics",
        "social_choice", "optimization",
    }
    present = {n.domain for n in catalog()}
    missing = required - present
    assert missing == set(), f"missing domains: {missing}"


def test_every_entry_is_frozen_dataclass() -> None:
    for entry in catalog():
        assert isinstance(entry, Noway)
        with pytest.raises(Exception):
            entry.key = "mutated"  # type: ignore[misc]


def test_keys_unique() -> None:
    keys = [n.key for n in catalog()]
    assert len(keys) == len(set(keys))


def test_certainty_is_fraction_in_unit_interval() -> None:
    for entry in catalog():
        assert isinstance(entry.certainty, Fraction)
        assert Fraction(0) <= entry.certainty <= Fraction(1)


def test_catalog_size_check_direct() -> None:
    ok, proof = check_catalog_size_at_floor()
    assert ok is True
    assert "PASS" in proof.conclusion


def test_falsifier_check_direct() -> None:
    ok, _ = check_every_entry_has_falsifier()
    assert ok is True


def test_unique_check_direct() -> None:
    ok, _ = check_keys_unique()
    assert ok is True


def test_certainty_check_direct() -> None:
    ok, _ = check_certainty_bounded()
    assert ok is True


def test_domains_check_direct() -> None:
    ok, _ = check_domains_covered()
    assert ok is True
