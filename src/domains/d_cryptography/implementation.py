#!/usr/bin/env python3
"""
Cryptography Domain — NIST SP 800-57 Key Management

Key standards:
- NIST SP 800-57: Recommendation for Key Management
- NIST SP 800-131A: Transitioning cryptographic algorithms
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum, auto


class KeyAlgorithm(Enum):
    AES = "AES"
    RSA = "RSA"
    ECC = "ECC"
    SHA256 = "SHA-256"
    SHA3 = "SHA-3"


@dataclass
class KeyStrengthAnalyzer:
    """Analyze cryptographic key strength per NIST SP 800-57."""
    algorithm: KeyAlgorithm
    key_bits: int
    
    # NIST SP 800-57 minimum key sizes (bits)
    MIN_AES = 128
    MIN_RSA = 2048
    MIN_ECC = 256
    
    def is_acceptable(self) -> bool:
        """Check if key size meets minimum requirements."""
        if self.algorithm == KeyAlgorithm.AES:
            return self.key_bits >= self.MIN_AES
        if self.algorithm == KeyAlgorithm.RSA:
            return self.key_bits >= self.MIN_RSA
        if self.algorithm == KeyAlgorithm.ECC:
            return self.key_bits >= self.MIN_ECC
        return True
    
    def effective_security_bits(self) -> Fraction:
        """Calculate effective security strength in bits."""
        if self.algorithm == KeyAlgorithm.AES:
            return Fraction(self.key_bits)
        if self.algorithm == KeyAlgorithm.RSA:
            # Rough approximation: log2(sqrt(N)) for RSA
            return Fraction(self.key_bits, 2)
        if self.algorithm == KeyAlgorithm.ECC:
            return Fraction(self.key_bits)
        return Fraction(0)


@dataclass
class HashAnalyzer:
    """Hash function collision resistance analysis."""
    algorithm: str
    output_bits: int
    
    def collision_resistance_bits(self) -> Fraction:
        """Birthday bound: 2^(n/2) operations for collision."""
        return Fraction(self.output_bits, 2)
    
    def preimage_resistance_bits(self) -> Fraction:
        """2^n operations for preimage."""
        return Fraction(self.output_bits)


@dataclass
class Certificate:
    """X.509 certificate for chain validation."""
    subject: str
    issuer: str
    public_key_algorithm: KeyAlgorithm
    key_size: int
    valid_from: str
    valid_to: str
    signature_valid: bool = False
    is_ca: bool = False


@dataclass
class CertChainValidator:
    """Certificate chain validation."""
    certificates: List[Certificate]
    trusted_roots: List[str] = field(default_factory=list)
    
    def chain_length(self) -> int:
        return len(self.certificates)
    
    def all_signatures_valid(self) -> bool:
        return all(c.signature_valid for c in self.certificates)
    
    def root_is_trusted(self) -> bool:
        if not self.certificates:
            return False
        root = self.certificates[-1]
        return root.is_ca and root.subject in self.trusted_roots
    
    def validate(self) -> bool:
        """Full chain validation."""
        if len(self.certificates) == 0:
            return False
        return self.all_signatures_valid() and self.root_is_trusted()


# Security strength thresholds (bits)
MIN_SECURITY_STRENGTH = Fraction(128)  # 128-bit security minimum
