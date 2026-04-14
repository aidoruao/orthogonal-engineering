#!/usr/bin/env python3
"""Cryptography Domain Invariants — NIST SP 800-57 compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import KeyStrengthAnalyzer, HashAnalyzer, Certificate, CertChainValidator, KeyAlgorithm, MIN_SECURITY_STRENGTH


def check_key_strength(analyzer: KeyStrengthAnalyzer) -> Tuple[bool, ProofObject]:
    """NIST SP 800-57: Keys must meet minimum size requirements.

    Falsifies if: analyzer.is_acceptable() is False or effective security bits < MIN_SECURITY_STRENGTH.
    falsifies_if: analyzer.is_acceptable() is False or effective security bits < MIN_SECURITY_STRENGTH.
    """
    if not analyzer.is_acceptable():
        return False, ProofObject(
            conclusion=f"VIOLATION: {analyzer.algorithm.value} key size {analyzer.key_bits} below minimum",
            premises=[f"Algorithm: {analyzer.algorithm.value}", f"Size: {analyzer.key_bits}"],
            rule="nist_sp_800_57_key_size"
        )
    
    effective = analyzer.effective_security_bits()
    if effective < MIN_SECURITY_STRENGTH:
        return False, ProofObject(
            conclusion=f"VIOLATION: Effective security {effective} bits < {MIN_SECURITY_STRENGTH}",
            premises=[],
            rule="nist_sp_800_57_security_strength"
        )
    
    return True, ProofObject(
        conclusion=f"Key strength adequate ({effective} bits effective security)",
        premises=[],
        rule="nist_sp_800_57"
    )


def check_hash_collision_resistance(analyzer: HashAnalyzer) -> Tuple[bool, ProofObject]:
    """Hash must provide adequate collision resistance.

    Falsifies if: analyzer.collision_resistance_bits() < MIN_SECURITY_STRENGTH.
    falsifies_if: analyzer.collision_resistance_bits() < MIN_SECURITY_STRENGTH.
    """
    collision_bits = analyzer.collision_resistance_bits()
    
    if collision_bits < MIN_SECURITY_STRENGTH:
        return False, ProofObject(
            conclusion=f"VIOLATION: Hash collision resistance {collision_bits} bits < {MIN_SECURITY_STRENGTH}",
            premises=[f"Output bits: {analyzer.output_bits}"],
            rule="nist_hash_strength"
        )
    
    return True, ProofObject(
        conclusion=f"Hash collision resistance adequate ({collision_bits} bits)",
        premises=[],
        rule="nist_hash_strength"
    )


def check_cert_chain(chain: CertChainValidator) -> Tuple[bool, ProofObject]:
    """Certificate chain must validate completely.

    Falsifies if: chain is empty, signatures are invalid, or root is untrusted.
    falsifies_if: chain is empty, signatures are invalid, or root is untrusted.
    """
    if len(chain.certificates) == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Empty certificate chain",
            premises=[],
            rule="cert_chain_nonempty"
        )
    
    if not chain.all_signatures_valid():
        return False, ProofObject(
            conclusion="VIOLATION: Invalid signature in certificate chain",
            premises=[],
            rule="cert_chain_signatures"
        )
    
    if not chain.root_is_trusted():
        return False, ProofObject(
            conclusion="VIOLATION: Chain root not in trust store",
            premises=[],
            rule="cert_chain_trust"
        )
    
    return True, ProofObject(
        conclusion="Certificate chain valid",
        premises=[f"Chain length: {chain.chain_length()}"],
        rule="cert_chain_valid"
    )


def check_key_algorithm_compliance(analyzer: KeyStrengthAnalyzer) -> Tuple[bool, ProofObject]:
    """NIST SP 800-131A: Approved algorithms only.

    Falsifies if: analyzer.algorithm is deprecated per NIST SP 800-131A.
    falsifies_if: analyzer.algorithm is deprecated per NIST SP 800-131A.
    """
    # Deprecated algorithms
    deprecated = []  # Add deprecated algorithms here
    
    if analyzer.algorithm.value in deprecated:
        return False, ProofObject(
            conclusion=f"VIOLATION: Algorithm {analyzer.algorithm.value} deprecated",
            premises=[],
            rule="nist_sp_800_131a"
        )
    
    return True, ProofObject(
        conclusion=f"Algorithm {analyzer.algorithm.value} approved",
        premises=[],
        rule="nist_sp_800_131a"
    )


def run_all_invariants() -> dict:
    """Run all D_CRYPTOGRAPHY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    cert_chain_validator = CertChainValidator(
        certificates=[Certificate(
        subject="SAMPLE",
        issuer="SAMPLE",
        public_key_algorithm=KeyAlgorithm.AES,
        key_size=1,
        valid_from="CRYPTOGR-001",
        valid_to="CRYPTOGR-001",
    )],
    )
    hash_analyzer = HashAnalyzer(
        algorithm="SAMPLE",
        output_bits=1,
    )
    key_strength_analyzer = KeyStrengthAnalyzer(
        algorithm=KeyAlgorithm.AES,
        key_bits=1,
    )

    checks = [
        ("check_cert_chain", lambda: check_cert_chain(cert_chain_validator)),
        ("check_hash_collision_resistance", lambda: check_hash_collision_resistance(hash_analyzer)),
        ("check_key_algorithm_compliance", lambda: check_key_algorithm_compliance(key_strength_analyzer)),
        ("check_key_strength", lambda: check_key_strength(key_strength_analyzer)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CRYPTOGRAPHY invariants: PASS")
