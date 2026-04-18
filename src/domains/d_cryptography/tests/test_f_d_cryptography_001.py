"""Falsification tests for D_CRYPTOGRAPHY."""

from fractions import Fraction

from src.domains.d_cryptography.implementation import KeyAlgorithm, KeyStrengthAnalyzer
from src.domains.d_cryptography.invariants import check_key_strength, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, result in results.items():
        assert result.startswith("PASS")


def test_failure_path_detected() -> None:
    analyzer = KeyStrengthAnalyzer(
        algorithm=KeyAlgorithm.RSA,
        key_bits=512,
    )
    success, proof = check_key_strength(analyzer)
    assert success is False
    assert "VIOLATION" in proof.conclusion
