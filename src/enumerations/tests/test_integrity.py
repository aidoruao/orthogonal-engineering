"""Falsification tests for the OE enumerations integrity checks."""
from typing import Any, Dict, List, Tuple
from unittest.mock import patch

from src.enumerations import integrity
from src.enumerations.integrity import (
    check_all_entries_have_falsifies_if,
    check_all_entries_have_keys,
    check_all_keys_unique_across_files,
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


def test_keys_unique_across_files_happy_path() -> None:
    ok, proof = check_all_keys_unique_across_files()
    assert ok is True
    assert "PASS" in proof.conclusion


def test_keys_unique_across_files_detects_two_way_collision() -> None:
    fake_catalogs: List[Tuple[str, List[Dict[str, Any]]]] = [
        ("file_a", [{"key": "shared", "falsifies_if": "x"}]),
        ("file_b", [{"key": "shared", "falsifies_if": "y"}]),
    ]
    with patch.object(integrity, "_all_catalogs", return_value=fake_catalogs):
        ok, proof = check_all_keys_unique_across_files()
    assert ok is False
    assert "shared:file_a+file_b" in proof.conclusion


def test_keys_unique_across_files_detects_three_way_collision() -> None:
    """All pairwise collisions must appear in the diagnostic, not just A+B."""
    fake_catalogs: List[Tuple[str, List[Dict[str, Any]]]] = [
        ("file_a", [{"key": "triple", "falsifies_if": "x"}]),
        ("file_b", [{"key": "triple", "falsifies_if": "y"}]),
        ("file_c", [{"key": "triple", "falsifies_if": "z"}]),
    ]
    with patch.object(integrity, "_all_catalogs", return_value=fake_catalogs):
        ok, proof = check_all_keys_unique_across_files()
    assert ok is False
    assert "triple:file_a+file_b+file_c" in proof.conclusion
