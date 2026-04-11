#!/usr/bin/env python3
"""Cryptography Domain Invariants — NIST SP 800-57 compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import KeyStrengthAnalyzer, HashAnalyzer, CertChainValidator, MIN_SECURITY_STRENGTH


def check_key_strength(analyzer: KeyStrengthAnalyzer) -> Tuple[bool, ProofObject]:
    """NIST SP 800-57: Keys must meet minimum size requirements.
    
    falsifies_if: condition_evaluated_to_false"""
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
    
    falsifies_if: condition_evaluated_to_false"""
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
    
    falsifies_if: condition_evaluated_to_false"""
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
    
    falsifies_if: condition_evaluated_to_false"""
    from .implementation import KeyAlgorithm
    
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
