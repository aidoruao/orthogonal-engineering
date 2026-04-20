"""Falsification tests for the OE enumerations integrity checks."""
from src.enumerations.integrity import (
    check_all_entries_have_falsifies_if,
    check_all_entries_have_keys,
    check_all_keys_unique_per_file,
    load_black_box_antipatterns,
    load_hidden_failures,
    load_magic_numbers,
    run_all_invariants,
)


def test_black_box_antipatterns_nonempty() -> None:
    entries = load_black_box_antipatterns()
    assert len(entries) >= 10


def test_hidden_failures_nonempty() -> None:
    entries = load_hidden_failures()
    assert len(entries) >= 8


def test_magic_numbers_nonempty() -> None:
    entries = load_magic_numbers()
    assert len(entries) >= 10


def test_all_keys_present() -> None:
    ok, _ = check_all_entries_have_keys()
    assert ok is True


def test_all_falsifies_if_present() -> None:
    ok, _ = check_all_entries_have_falsifies_if()
    assert ok is True


def test_keys_unique_per_file() -> None:
    ok, _ = check_all_keys_unique_per_file()
    assert ok is True


def test_run_all_invariants_green() -> None:
    results = run_all_invariants()
    assert len(results) == 4
    for _name, ok, _proof in results:
        assert ok is True


def test_magic_number_entries_have_fraction_field() -> None:
    for entry in load_magic_numbers():
        assert "fraction" in entry
        assert entry["fraction"].startswith("Fraction") or entry["fraction"].startswith("approximant")
