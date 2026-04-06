"""Biblical Patterns for Orthogonal Engineering

Two sets of patterns:
  1. RESTORATION patterns (10) - Meta-patterns about system operation
  2. SOVEREIGN TOPOS patterns (10) - Domain-level enforcement patterns

RESTORATION Patterns:
  - jubilee_reset: Tech debt counter reset
  - manna_constraint: Resource discipline per session
  - kenotic_override: Love > Rule when rule condemns
  - berean_verification: Test everything before acceptance
  - nehemiah_wall: Implementation + test in same commit
  - gideon_reduction: Strip unnecessary dependencies
  - ruth_gleaning: All code is permissively licensed
  - daniel_audit: Survive external review
  - joseph_storage: Cache successful patterns
  - solomon_arbitration: Resolve conflicting invariants

SOVEREIGN TOPOS Patterns:
  - mercy_weighting: INV-YS-004 implementation
  - vulnerability_protection: INV-YS-005 implementation
  - bounded_power: INV-YS-009 implementation
  - hash_anchored_evidence: Yeshua Axiom Y8 implementation
  - anti_nominalism: INV-YS-007 implementation
  - functorial_chain: Multi-step process preservation
  - independent_situs: Review by different perspective
  - equity_threshold: Resource distribution variance bounds
  - deterministic_formula: Reproducible calculations
  - immutable_audit_trail: All state transitions logged
"""

# RESTORATION Patterns (meta-patterns)
from src.patterns.jubilee_reset import JubileeReset
from src.patterns.manna_constraint import MannaConstraint
from src.patterns.kenotic_override import KenoticOverride
from src.patterns.berean_verification import BereanVerification
from src.patterns.nehemiah_wall import NehemiahWall
from src.patterns.gideon_reduction import GideonReduction
from src.patterns.ruth_gleaning import RuthGleaning
from src.patterns.daniel_audit import DanielAudit
from src.patterns.joseph_storage import JosephStorage
from src.patterns.solomon_arbitration import SolomonArbitration

# SOVEREIGN TOPOS Patterns (domain patterns)
from src.patterns.pattern_mercy_weighting import MercyWeighting
from src.patterns.pattern_vulnerability_protection import VulnerabilityProtection
from src.patterns.pattern_bounded_power import BoundedPower
from src.patterns.pattern_hash_anchored_evidence import HashAnchoredEvidence
from src.patterns.pattern_anti_nominalism import AntiNominalism
from src.patterns.pattern_functorial_chain import FunctorialChain
from src.patterns.pattern_independent_situs import IndependentSitus
from src.patterns.pattern_equity_threshold import EquityThreshold
from src.patterns.pattern_deterministic_formula import DeterministicFormula
from src.patterns.pattern_immutable_audit_trail import ImmutableAuditTrail

__all__ = [
    # RESTORATION patterns
    "JubileeReset",
    "MannaConstraint",
    "KenoticOverride",
    "BereanVerification",
    "NehemiahWall",
    "GideonReduction",
    "RuthGleaning",
    "DanielAudit",
    "JosephStorage",
    "SolomonArbitration",
    # SOVEREIGN TOPOS patterns
    "MercyWeighting",
    "VulnerabilityProtection",
    "BoundedPower",
    "HashAnchoredEvidence",
    "AntiNominalism",
    "FunctorialChain",
    "IndependentSitus",
    "EquityThreshold",
    "DeterministicFormula",
    "ImmutableAuditTrail",
]
