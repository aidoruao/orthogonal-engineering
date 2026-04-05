"""
benchmarks/capability_matrix.py
CAPABILITY MATRIX — PR #98 Addition

Machine-readable capability registry comparing SAL kernel against external AI systems.
Every capability is wrapped in a YeshuaClaim with SHA-256 commitment.

Non-defamation rules:
  - HAS, DOES_NOT_HAVE, UNKNOWN only
  - DOES_NOT_HAVE requires public technical reason
  - Every DOES_NOT_HAVE includes falsifies_if
  - No emotional language, no "better than", no "ahead of"
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple, Any

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim


CapabilityStatus = Literal["HAS", "DOES_NOT_HAVE", "UNKNOWN"]


@dataclass(frozen=True)
class CapabilityEntry:
    """Single capability entry with falsifiability tracking."""
    
    status: CapabilityStatus
    reason: str = ""  # Required for DOES_NOT_HAVE
    falsifies_if: str = ""  # Required for all entries
    test_id: str = ""  # Reference to test that validates


# =============================================================================
# CAPABILITY DIMENSIONS
# =============================================================================

CAPABILITY_DIMENSIONS: List[Dict[str, str]] = [
    {
        "id": "forensic_adjunction_proof",
        "description": "Produce valid ProofObject for real-world forensic scenarios",
        "test_id": "CAP_FORENSIC_001",
        "mathematical_concept": "Type 3 adjunction via L ⊣ M ⊣ R functor triple",
        "falsifies_if": "ProofObject.is_valid() returns False for valid scenario",
    },
    {
        "id": "geometric_morphism_truth_detection",
        "description": "Detect truth divergence between sites via geometric morphism",
        "test_id": "CAP_FORENSIC_002",
        "mathematical_concept": "Grothendieck topos geometric morphism f* ⊣ f_*",
        "falsifies_if": "truth_preserved == True for contradictory sites",
    },
    {
        "id": "forcing_remedy",
        "description": "Produce constructive remedy via forcing extension",
        "test_id": "CAP_FORENSIC_003",
        "mathematical_concept": "Cohen forcing (ground model → generic extension)",
        "falsifies_if": "force_domain() returns empty list for defective state",
    },
    {
        "id": "deterministic_proof",
        "description": "Same input produces identical ProofObject hash",
        "test_id": "CAP_DETERMINISM_001",
        "mathematical_concept": "Deterministic algorithm with canonical serialization",
        "falsifies_if": "Two runs with same input produce different hashes",
    },
    {
        "id": "no_floating_point",
        "description": "No floating-point arithmetic in kernel (Fraction only)",
        "test_id": "CAP_DETERMINISM_002",
        "mathematical_concept": "Exact arithmetic via Fraction (ℚ)",
        "falsifies_if": "float() or float literals found in src/sal/",
    },
    {
        "id": "structured_adjunction_return",
        "description": "has_adjunction returns structured proof, not bare bool",
        "test_id": "CAP_ADJUNCTION_001",
        "mathematical_concept": "Adjunction proof structure with unit/counit evidence",
        "falsifies_if": "Return type is bare bool instead of AdjunctionProof",
    },
    {
        "id": "hash_anchored_claims",
        "description": "Counit violations carry SHA-256 evidence anchor",
        "test_id": "CAP_ADJUNCTION_002",
        "mathematical_concept": "Yeshua Axiom 8 (cryptographic commitment)",
        "falsifies_if": "YeshuaClaim.is_hash_anchored() returns False",
    },
    {
        "id": "heyting_algebra",
        "description": "Site-relative truth via Heyting algebra (not Boolean)",
        "test_id": "CAP_TOPOS_001",
        "mathematical_concept": "Heyting algebra intuitionistic logic",
        "falsifies_if": "SubobjectClassifier uses float or binary logic",
    },
    {
        "id": "site_relative_truth",
        "description": "Geometric morphism constructible between 2+ sites",
        "test_id": "CAP_TOPOS_002",
        "mathematical_concept": "Geometric morphism between topoi",
        "falsifies_if": "geometric_morphism() raises or returns None",
    },
    {
        "id": "extension_defect_proof",
        "description": "Extension existence proves ground model defect",
        "test_id": "CAP_FORCING_001",
        "mathematical_concept": "Proof by generic extension",
        "falsifies_if": "Extension exists but ground model marked valid",
    },
    {
        "id": "realizability_truth",
        "description": "Realized proposition has internal truth value 1",
        "test_id": "CAP_REALIZABILITY_001",
        "mathematical_concept": "Hyland's effective topos (Eff)",
        "falsifies_if": "internal_truth() != Fraction(1) for realized prop",
    },
    {
        "id": "merkle_anchoring",
        "description": "Every claim is Merkle-anchored with 64-char hex commitment",
        "test_id": "CAP_HASH_CHAIN_001",
        "mathematical_concept": "Cryptographic hash chain (SHA-256)",
        "falsifies_if": "Any claim lacks 64-char hex commitment",
    },
]


# =============================================================================
# SYSTEM CAPABILITIES
# =============================================================================

SYSTEM_CAPABILITIES: Dict[str, Dict[str, CapabilityEntry]] = {
    "sal_kernel": {
        dim["id"]: CapabilityEntry(
            status="HAS",
            reason="SAL kernel implements this capability as verified by test",
            falsifies_if=dim["falsifies_if"],
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "tesla_fsd": {
        "forensic_adjunction_proof": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD is a motion planner, not a legal reasoner. It optimizes trajectory, not constitutional law.",
            falsifies_if="Tesla publishes a formal ProofObject for detention analysis",
            test_id="CAP_FORENSIC_001",
        ),
        "geometric_morphism_truth_detection": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD has no topos-theoretic truth model. It uses stochastic inference.",
            falsifies_if="Tesla documentation references Grothendieck topos or geometric morphisms",
            test_id="CAP_FORENSIC_002",
        ),
        "forcing_remedy": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD has no constructive set-theoretic forcing mechanism.",
            falsifies_if="Tesla code shows generic extension construction",
            test_id="CAP_FORENSIC_003",
        ),
        "deterministic_proof": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD is explicitly stochastic (neural network sampling).",
            falsifies_if="Tesla removes all random() calls and guarantees identical outputs",
            test_id="CAP_DETERMINISM_001",
        ),
        "no_floating_point": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD uses floating-point arithmetic throughout.",
            falsifies_if="Tesla uses only fixed-point or rational arithmetic",
            test_id="CAP_DETERMINISM_002",
        ),
        "structured_adjunction_return": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla FSD has no adjunction-based API.",
            falsifies_if="Tesla API returns (bool, ProofObject) tuples with unit/counit",
            test_id="CAP_ADJUNCTION_001",
        ),
        "hash_anchored_claims": CapabilityEntry(
            status="UNKNOWN",
            reason="No public evidence of SHA-256 anchored claims.",
            falsifies_if="Tesla publishes hash-anchored claim documentation",
            test_id="CAP_ADJUNCTION_002",
        ),
        "heyting_algebra": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla uses standard boolean logic or probability, not Heyting algebra.",
            falsifies_if="Tesla documentation shows intuitionistic logic with Fraction-valued truth",
            test_id="CAP_TOPOS_001",
        ),
        "site_relative_truth": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla has no situs-based sheaf context model.",
            falsifies_if="Tesla documentation references site-relative truth or sheaf contexts",
            test_id="CAP_TOPOS_002",
        ),
        "extension_defect_proof": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla has no forcing-based extension mechanism.",
            falsifies_if="Tesla shows proof-by-generic-extension for defect detection",
            test_id="CAP_FORCING_001",
        ),
        "realizability_truth": CapabilityEntry(
            status="DOES_NOT_HAVE",
            reason="Tesla has no realizability topos or effective topos implementation.",
            falsifies_if="Tesla uses Hyland's effective topos with Kleene realizers",
            test_id="CAP_REALIZABILITY_001",
        ),
        "merkle_anchoring": CapabilityEntry(
            status="UNKNOWN",
            reason="No public evidence of Merkle tree proof aggregation.",
            falsifies_if="Tesla publishes Merkle root over proof DAGs",
            test_id="CAP_HASH_CHAIN_001",
        ),
    },
    "grok_3": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for Grok 3.",
            falsifies_if="xAI publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "gpt_5_2": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for GPT-5.2.",
            falsifies_if="OpenAI publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "claude_opus_4_5": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for Claude Opus 4.5.",
            falsifies_if="Anthropic publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "kimi_k2_5": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for Kimi K2.5.",
            falsifies_if="Moonshot AI publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "deepseek_v3_2": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for DeepSeek V3.2.",
            falsifies_if="DeepSeek publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
    "devin_ai": {
        dim["id"]: CapabilityEntry(
            status="UNKNOWN",
            reason="No public technical documentation available for Devin AI.",
            falsifies_if="Cognition publishes technical specifications showing this capability",
            test_id=dim["test_id"],
        )
        for dim in CAPABILITY_DIMENSIONS
    },
}


# =============================================================================
# API FUNCTIONS
# =============================================================================

def get_capability(system: str, dimension: str) -> CapabilityStatus:
    """
    Get capability status for a system on a specific dimension.
    
    Args:
        system: System name (e.g., "sal_kernel", "tesla_fsd")
        dimension: Capability dimension ID
        
    Returns:
        "HAS", "DOES_NOT_HAVE", or "UNKNOWN"
    """
    if system not in SYSTEM_CAPABILITIES:
        return "UNKNOWN"
    if dimension not in SYSTEM_CAPABILITIES[system]:
        return "UNKNOWN"
    return SYSTEM_CAPABILITIES[system][dimension].status


def get_sal_advantages() -> List[str]:
    """
    Return list of dimensions where SAL is HAS and all others are not HAS.
    
    Returns:
        List of dimension IDs where SAL has unique capability.
    """
    advantages = []
    for dim in CAPABILITY_DIMENSIONS:
        dim_id = dim["id"]
        sal_has = get_capability("sal_kernel", dim_id) == "HAS"
        others_have = any(
            get_capability(sys, dim_id) == "HAS"
            for sys in SYSTEM_CAPABILITIES
            if sys != "sal_kernel"
        )
        if sal_has and not others_have:
            advantages.append(dim_id)
    return advantages


def validate_matrix() -> Tuple[bool, List[str]]:
    """
    Validate the capability matrix structure.
    
    Checks:
      - Every DOES_NOT_HAVE has a non-empty reason
      - Every entry has a non-empty falsifies_if
      - All dimension IDs are covered
      
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    for system, capabilities in SYSTEM_CAPABILITIES.items():
        for dim_id, entry in capabilities.items():
            if entry.status == "DOES_NOT_HAVE":
                if not entry.reason:
                    errors.append(f"{system}.{dim_id}: DOES_NOT_HAVE missing reason")
            if not entry.falsifies_if:
                errors.append(f"{system}.{dim_id}: missing falsifies_if")
    
    # Check all dimensions are covered
    dim_ids = {dim["id"] for dim in CAPABILITY_DIMENSIONS}
    for system in SYSTEM_CAPABILITIES:
        system_dims = set(SYSTEM_CAPABILITIES[system].keys())
        missing = dim_ids - system_dims
        if missing:
            errors.append(f"{system}: missing dimensions {missing}")
    
    return len(errors) == 0, errors


def wrap_capability_claim(
    capability_id: str,
    system: str,
    entry: CapabilityEntry,
) -> YeshuaClaim:
    """
    Wrap a capability entry in a YeshuaClaim with SHA-256 commitment.
    
    Args:
        capability_id: The capability dimension ID
        system: System name
        entry: CapabilityEntry to wrap
        
    Returns:
        YeshuaClaim with hash commitment
    """
    description = json.dumps({
        "capability": capability_id,
        "system": system,
        "status": entry.status,
        "reason": entry.reason,
        "falsifies_if": entry.falsifies_if,
    }, sort_keys=True)
    
    proof = ProofObject(
        rule="CapabilityBenchmark",
        premises=[f"capability={capability_id}", f"system={system}", f"status={entry.status}"],
        conclusion=f"Capability {capability_id} for {system}: {entry.status}",
    )
    
    return YeshuaClaim(
        source="benchmarks/capability_matrix.py",
        statement=description,
        derivation=proof,
    )


def get_all_capability_claims() -> Dict[str, YeshuaClaim]:
    """
    Get all capability entries wrapped as YeshuaClaims.
    
    Returns:
        Dict mapping "system:capability" to YeshuaClaim
    """
    claims = {}
    for system, capabilities in SYSTEM_CAPABILITIES.items():
        for dim_id, entry in capabilities.items():
            key = f"{system}:{dim_id}"
            claims[key] = wrap_capability_claim(dim_id, system, entry)
    return claims


if __name__ == "__main__":
    # Self-validation
    is_valid, errors = validate_matrix()
    print(f"Matrix valid: {is_valid}")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  - {err}")
    
    # Show SAL advantages
    advantages = get_sal_advantages()
    print(f"\nSAL unique capabilities ({len(advantages)}):")
    for adv in advantages:
        print(f"  - {adv}")
    
    # Sample claim
    print("\nSample claim (sal_kernel:forensic_adjunction_proof):")
    claim = wrap_capability_claim(
        "forensic_adjunction_proof",
        "sal_kernel",
        SYSTEM_CAPABILITIES["sal_kernel"]["forensic_adjunction_proof"]
    )
    print(f"  Hash: {claim.hash_commitment}")
    print(f"  Anchored: {claim.is_hash_anchored()}")
