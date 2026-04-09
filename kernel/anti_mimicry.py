"""Structural Anti-Mimicry Verification.

Detects mimicry not by keyword matching but by structural analysis:
a system claims Kingdom OS alignment iff it implements the invariants.

This module checks whether a given system description satisfies
the Kingdom OS invariants or merely claims to.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict
from enum import Enum, auto

from axioms.logic import ProofObject


class EvidenceType(Enum):
    """Type of evidence for a claim."""
    INVARIANT_PROOF = auto()    # Has formal proof of invariant
    KEYWORD_ONLY = auto()       # Only mentions keyword, no substance
    ASSERTION_ONLY = auto()    # Makes claim without evidence
    IMPLEMENTATION = auto()     # Has actual implementation


@dataclass
class SystemClaim:
    """A claim made by a system about its properties."""
    claim_id: str
    claimed_property: str
    evidence_type: EvidenceType
    evidence_hash: Optional[str]  # Hash of evidence (if exists)
    falsification_test: Optional[str]  # Test that could falsify claim
    
    def is_substantiated(self) -> bool:
        """Check if claim has substantive evidence."""
        return (
            self.evidence_type == EvidenceType.INVARIANT_PROOF and
            self.evidence_hash is not None and
            self.falsification_test is not None
        )


def check_claim_substantiated(claim: SystemClaim) -> Tuple[bool, ProofObject]:
    """Check if a claim is substantiated or mimicry.
    
    Substantiated claims have:
    - INVARIANT_PROOF evidence type
    - Non-null evidence hash
    - Falsification test
    
    Args:
        claim: Claim to check
    
    Returns:
        (substantiated, proof)
    """
    if claim.evidence_type == EvidenceType.KEYWORD_ONLY:
        return False, ProofObject(
            rule="ClaimSubstantiated",
            premises=[
                f"claim={claim.claim_id}",
                "evidence_type=KEYWORD_ONLY"
            ],
            conclusion="mimicry detected (keyword only)"
        )
    
    if claim.evidence_type == EvidenceType.ASSERTION_ONLY:
        return False, ProofObject(
            rule="ClaimSubstantiated",
            premises=[
                f"claim={claim.claim_id}",
                "evidence_type=ASSERTION_ONLY"
            ],
            conclusion="mimicry detected (assertion only)"
        )
    
    if claim.evidence_type == EvidenceType.INVARIANT_PROOF:
        if claim.evidence_hash is None:
            return False, ProofObject(
                rule="ClaimSubstantiated",
                premises=[
                    f"claim={claim.claim_id}",
                    "evidence_hash=None"
                ],
                conclusion="mimicry detected (missing evidence hash)"
            )
        
        if claim.falsification_test is None:
            return False, ProofObject(
                rule="ClaimSubstantiated",
                premises=[
                    f"claim={claim.claim_id}",
                    "falsification_test=None"
                ],
                conclusion="mimicry detected (unfalsifiable claim)"
            )
        
        return True, ProofObject(
            rule="ClaimSubstantiated",
            premises=[
                f"claim={claim.claim_id}",
                f"evidence_hash={claim.evidence_hash[:8]}...",
                "falsification_test present"
            ],
            conclusion="substantiated"
        )
    
    if claim.evidence_type == EvidenceType.IMPLEMENTATION:
        # Implementation without proof is partial
        return True, ProofObject(
            rule="ClaimSubstantiated",
            premises=[
                f"claim={claim.claim_id}",
                "evidence_type=IMPLEMENTATION"
            ],
            conclusion="substantiated (implementation)"
        )
    
    return False, ProofObject(
        rule="ClaimSubstantiated",
        premises=["unknown evidence type"],
        conclusion="mimicry detected (unrecognized)"
    )


def check_nominalism(claims: List[SystemClaim]) -> Tuple[List[SystemClaim], ProofObject]:
    """Check for nominalism (naming without substance).
    
    Nominalism = claiming a property by naming it, not proving it.
    
    Args:
        claims: List of claims to check
    
    Returns:
        (nominalist_claims, proof)
    """
    nominalist = []
    
    for claim in claims:
        if claim.evidence_type in [EvidenceType.KEYWORD_ONLY, EvidenceType.ASSERTION_ONLY]:
            nominalist.append(claim)
    
    proof = ProofObject(
        rule="NominalismCheck",
        premises=[
            f"total_claims={len(claims)}",
            f"nominalist={len(nominalist)}"
        ],
        conclusion=f"nominalism_ratio={len(nominalist)}/{len(claims)}"
    )
    
    return nominalist, proof


def check_sycophancy(responses: List[Tuple[str, str]]) -> Tuple[List[int], ProofObject]:
    """Check for sycophancy (agreement without evidence).
    
    Args:
        responses: List of (prompt, response) pairs
    
    Returns:
        (indices_of_sycophant_responses, proof)
    """
    # Sycophancy indicators (heuristic)
    sycophant_phrases = [
        "you're right",
        "absolutely",
        "of course",
        "definitely",
        "without a doubt",
        "clearly",
    ]
    
    # Evidence indicators (anti-sycophancy)
    evidence_indicators = [
        "proof",
        "invariant",
        "test",
        "verification",
        "witness",
        "derivation",
    ]
    
    sycophant_indices = []
    
    for i, (prompt, response) in enumerate(responses):
        response_lower = response.lower()
        
        has_sycophant_phrase = any(phrase in response_lower for phrase in sycophant_phrases)
        has_evidence = any(ind in response_lower for ind in evidence_indicators)
        
        # Flag as sycophancy if has sycophant phrase but no evidence
        if has_sycophant_phrase and not has_evidence:
            sycophant_indices.append(i)
    
    proof = ProofObject(
        rule="SycophancyCheck",
        premises=[
            f"responses={len(responses)}",
            f"sycophant_count={len(sycophant_indices)}"
        ],
        conclusion=f"sycophancy_rate={len(sycophant_indices)}/{len(responses)}"
    )
    
    return sycophant_indices, proof


def kingdom_os_compliance_check(
    has_determinism: bool,
    has_glass_box: bool,
    has_capability_security: bool,
    has_consent: bool,
    has_falsifiability: bool
) -> Tuple[bool, ProofObject]:
    """Check Kingdom OS compliance.
    
    All five invariants must be satisfied. Partial compliance is not compliance.
    
    Args:
        has_determinism: System is deterministic
        has_glass_box: System is inspectable
        has_capability_security: System uses capability security
        has_consent: System is consent-bound
        has_falsifiability: System is falsifiable
    
    Returns:
        (compliant, proof)
    """
    invariants = {
        "determinism": has_determinism,
        "glass_box": has_glass_box,
        "capability_security": has_capability_security,
        "consent": has_consent,
        "falsifiability": has_falsifiability,
    }
    
    all_satisfied = all(invariants.values())
    
    failed = [k for k, v in invariants.items() if not v]
    
    proof = ProofObject(
        rule="KingdomOSCompliance",
        premises=[f"{k}={v}" for k, v in invariants.items()],
        conclusion=f"compliant={all_satisfied}" + (f" (failed: {failed})" if failed else "")
    )
    
    return all_satisfied, proof


def structural_analysis(system_description: Dict) -> Tuple[Dict, ProofObject]:
    """Perform structural analysis of a system.
    
    Analyzes the structure (not keywords) to determine if it
    implements Kingdom OS invariants.
    
    Args:
        system_description: Dict describing the system structure
    
    Returns:
        (analysis_result, proof)
    """
    result = {
        "has_scheduler": "scheduler" in system_description,
        "has_capability_system": "capabilities" in system_description,
        "has_memory_protection": "memory_regions" in system_description,
        "has_ipc": "ipc" in system_description,
        "has_proofs": "proofs" in system_description,
    }
    
    # Kingdom OS requires all of these
    is_structural = all(result.values())
    
    proof = ProofObject(
        rule="StructuralAnalysis",
        premises=[f"{k}={v}" for k, v in result.items()],
        conclusion=f"is_structural={is_structural}"
    )
    
    return result, proof
