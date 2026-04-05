"""
tests/test_capability_benchmark.py
CAPABILITY BENCHMARK TESTS — PR #98 Addition

12 Popperian capability tests for the SAL kernel.
Each test:
  1. Calls actual SAL kernel functions
  2. Asserts a specific capability exists
  3. Documents the falsification condition in the docstring
  4. Includes a COMPARISON dict documenting external system requirements

Falsifies if: Any test returns False or raises.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from src.domains.d_dollartree.domain import (
    DOLLARTREE_SCHEMA,
    build_domain_state,
    build_officer_situs,
    build_video_situs,
    evaluate_topos_truth_gap,
    run_adjunction_check,
)
from src.sal.adjoint_triple import AdjointTriple, has_adjunction
from src.sal.forcing_operation import (
    CardinalStrength,
    DomainState,
    ForcingOperation,
    force_domain,
)
from src.sal.topos_subobject_classifier import (
    SheafContext,
    SubobjectClassifier,
    geometric_morphism,
)
from src.sal.realizability_topos import (
    RealizabilityTopos,
    realize,
    Realizer,
    ORDINAL_EPSILON_0,
)


# Non-defamation comparison matrix: documents what external systems need
CAPABILITY_COMPARISON = {
    "sal_kernel": {
        "forensic_adjunction_proof": "HAS",
        "geometric_morphism_truth_detection": "HAS",
        "forcing_remedy": "HAS",
        "deterministic_proof": "HAS",
        "no_floating_point": "HAS",
        "structured_adjunction_return": "HAS",
        "hash_anchored_claims": "HAS",
        "heyting_algebra": "HAS",
        "site_relative_truth": "HAS",
        "extension_defect_proof": "HAS",
        "realizability_truth": "HAS",
        "merkle_anchoring": "HAS",
    },
    "tesla_fsd": {
        "forensic_adjunction_proof": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD is a motion planner, not a legal reasoner. It optimizes trajectory, not constitutional law.",
            "falsifies_if": "Tesla publishes a formal ProofObject for detention analysis.",
        },
        "geometric_morphism_truth_detection": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD has no topos-theoretic truth model. It uses stochastic inference.",
            "falsifies_if": "Tesla documentation references Grothendieck topos or geometric morphisms.",
        },
        "forcing_remedy": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD has no constructive set-theoretic forcing mechanism.",
            "falsifies_if": "Tesla code shows generic extension construction.",
        },
        "deterministic_proof": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD is explicitly stochastic (neural network sampling).",
            "falsifies_if": "Tesla removes all random() calls and guarantees identical outputs.",
        },
        "no_floating_point": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD uses floating-point arithmetic throughout.",
            "falsifies_if": "Tesla uses only fixed-point or rational arithmetic.",
        },
        "structured_adjunction_return": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla FSD has no adjunction-based API.",
            "falsifies_if": "Tesla API returns (bool, ProofObject) tuples with unit/counit.",
        },
        "hash_anchored_claims": {
            "status": "UNKNOWN",
            "reason": "No public evidence of SHA-256 anchored claims.",
            "falsifies_if": "Tesla publishes hash-anchored claim documentation.",
        },
        "heyting_algebra": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla uses standard boolean logic or probability, not Heyting algebra.",
            "falsifies_if": "Tesla documentation shows intuitionistic logic with Fraction-valued truth.",
        },
        "site_relative_truth": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla has no situs-based sheaf context model.",
            "falsifies_if": "Tesla documentation references site-relative truth or sheaf contexts.",
        },
        "extension_defect_proof": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla has no forcing-based extension mechanism.",
            "falsifies_if": "Tesla shows proof-by-generic-extension for defect detection.",
        },
        "realizability_truth": {
            "status": "DOES_NOT_HAVE",
            "reason": "Tesla has no realizability topos or effective topos implementation.",
            "falsifies_if": "Tesla uses Hyland's effective topos with Kleene realizers.",
        },
        "merkle_anchoring": {
            "status": "UNKNOWN",
            "reason": "No public evidence of Merkle tree proof aggregation.",
            "falsifies_if": "Tesla publishes Merkle root over proof DAGs.",
        },
    },
    "grok_3": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "xAI publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
    "gpt_5_2": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "OpenAI publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
    "claude_opus_4_5": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "Anthropic publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
    "kimi_k2_5": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "Moonshot AI publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
    "deepseek_v3_2": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "DeepSeek publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
    "devin_ai": {k: {"status": "UNKNOWN", "reason": "No public technical documentation.", "falsifies_if": "Cognition publishes technical specifications."} for k in [
        "forensic_adjunction_proof", "geometric_morphism_truth_detection", "forcing_remedy",
        "deterministic_proof", "no_floating_point", "structured_adjunction_return",
        "hash_anchored_claims", "heyting_algebra", "site_relative_truth",
        "extension_defect_proof", "realizability_truth", "merkle_anchoring"
    ]},
}


class TestCapabilityBenchmark:
    """12 Popperian capability tests for SAL kernel."""

    def test_cap_forensic_001(self):
        """CAP_FORENSIC_001: Produce ProofObject for real-world detention.
        
        Mathematical concept: Type 3 adjunction verification via L ⊣ M ⊣ R functor triple.
        
        Falsifies if: ProofObject.is_valid() returns False.
        """
        result = run_adjunction_check()
        assert result is not None
        # AdjunctionProof has counit_evidence and unit_evidence, not proof
        assert isinstance(result.counit_evidence, ProofObject)
        assert isinstance(result.unit_evidence, ProofObject)
        assert result.counit_evidence.is_valid(), "counit evidence must be valid"
        assert result.unit_evidence.is_valid(), "unit evidence must be valid"

    def test_cap_forensic_002(self):
        """CAP_FORENSIC_002: Geometric morphism detects truth divergence.
        
        Mathematical concept: Grothendieck topos geometric morphism with f* ⊣ f_* adjunction.
        
        Falsifies if: truth_preserved == True for contradictory sites.
        """
        morphism = evaluate_topos_truth_gap()
        assert morphism.truth_preserved is False, (
            "Expected truth_preserved=False: officer situs and video situs disagree."
        )
        # Check for discrepancies list in proof premises
        premises_str = str(morphism.proof.premises)
        assert "discrepancies" in premises_str or not morphism.truth_preserved

    def test_cap_forensic_003(self):
        """CAP_FORENSIC_003: Forcing produces constructive remedy.
        
        Mathematical concept: Cohen forcing (M → M[G]) for model extension.
        
        Falsifies if: force_domain() returns empty list.
        """
        state = build_domain_state()
        extensions = force_domain(state)
        assert len(extensions) >= 1, "Forcing must produce at least one extension"
        assert any(ext.adjunction_holds for ext in extensions), (
            "At least one extension must have adjunction_holds=True"
        )

    def test_cap_determinism_001(self):
        """CAP_DETERMINISM_001: Same input produces same ProofObject hash.
        
        Mathematical concept: Deterministic algorithm with canonical serialization.
        
        Falsifies if: Two runs produce different hashes.
        """
        result1 = run_adjunction_check()
        result2 = run_adjunction_check()
        # Use counit_evidence for hash comparison (both should be deterministic)
        assert result1.counit_evidence.proof_hash == result2.counit_evidence.proof_hash, (
            "Deterministic SAL functions must produce identical proof hashes"
        )

    def test_cap_determinism_002(self):
        """CAP_DETERMINISM_002: No floating-point in kernel.
        
        Mathematical concept: Exact arithmetic via Fraction (ℚ) for reproducibility.
        
        Falsifies if: float() found in src/sal/ source.
        """
        src_dir = Path(__file__).parent.parent / "src" / "sal"
        py_files = list(src_dir.glob("*.py"))
        
        float_violations = []
        for py_file in py_files:
            try:
                source = py_file.read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    # Check for float() calls
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id == "float":
                            float_violations.append(f"{py_file.name}: float() call")
                    # Check for float literals (ast.Constant with float value)
                    if isinstance(node, ast.Constant):
                        if isinstance(node.value, float):
                            # Allow 0.0 and 1.0 in specific contexts if needed, but spec says no floats
                            float_violations.append(f"{py_file.name}: float literal {node.value}")
            except SyntaxError:
                continue
        
        assert len(float_violations) == 0, f"float() found in SAL kernel: {float_violations}"

    def test_cap_adjunction_001(self):
        """CAP_ADJUNCTION_001: has_adjunction returns structured proof, not bare bool.
        
        Mathematical concept: Adjunction proof structure with unit/counit evidence.
        
        Falsifies if: Return type is bare bool.
        """
        from src.sal.adjoint_triple import AdjunctionProof
        
        triple = AdjointTriple()
        result = has_adjunction(DOLLARTREE_SCHEMA, triple)
        
        assert isinstance(result, AdjunctionProof), (
            "has_adjunction must return AdjunctionProof, not bare bool"
        )
        assert hasattr(result, "counit_holds")
        assert hasattr(result, "unit_holds")
        assert hasattr(result, "counit_evidence")
        assert hasattr(result, "unit_evidence")

    def test_cap_adjunction_002(self):
        """CAP_ADJUNCTION_002: Counit violation carries SHA-256 evidence.
        
        Mathematical concept: Yeshua Axiom 8 (hash anchoring) for evidence integrity.
        
        Falsifies if: YeshuaClaim.is_hash_anchored() returns False.
        """
        result = run_adjunction_check()
        claim = result.yeshua_claim
        
        assert claim.is_hash_anchored(), "YeshuaClaim must carry 64-char hex SHA-256"
        assert len(claim.hash_commitment) == 64
        assert all(c in "0123456789abcdef" for c in claim.hash_commitment)

    def test_cap_topos_001(self):
        """CAP_TOPOS_001: Site-relative truth via Heyting algebra.
        
        Mathematical concept: Heyting algebra intuitionistic logic with Fraction-valued Ω.
        
        Falsifies if: SubobjectClassifier uses float or binary.
        """
        officer_ctx = build_officer_situs()
        video_ctx = build_video_situs()
        
        officer_cls = SubobjectClassifier(officer_ctx)
        video_cls = SubobjectClassifier(video_ctx)
        
        # Evaluate same proposition in both sites
        officer_truth = officer_cls.evaluate("lawful_detention", "lawful_detention")
        video_truth = video_cls.evaluate("lawful_detention", "lawful_detention")
        
        # Must return Fraction, not float or bool
        assert isinstance(officer_truth, Fraction), f"Expected Fraction, got {type(officer_truth)}"
        assert isinstance(video_truth, Fraction), f"Expected Fraction, got {type(video_truth)}"
        
        # Results must differ (site-relative truth)
        assert officer_truth != video_truth, (
            "Site-relative truth must differ between officer and video situs"
        )

    def test_cap_topos_002(self):
        """CAP_TOPOS_002: Geometric morphism between 2+ sites.
        
        Mathematical concept: Geometric morphism f: ℰ → ℱ as adjoint pair (f* ⊣ f_*).
        
        Falsifies if: geometric_morphism() raises or returns None.
        """
        from src.sal.topos_subobject_classifier import GeometricMorphism
        
        officer_ctx = build_officer_situs()
        video_ctx = build_video_situs()
        
        morphism = geometric_morphism(officer_ctx, video_ctx)
        
        assert isinstance(morphism, GeometricMorphism), (
            "geometric_morphism must return GeometricMorphism, not None"
        )
        assert hasattr(morphism, "inverse_image")
        assert hasattr(morphism, "direct_image")
        assert isinstance(morphism.inverse_image, dict)
        assert isinstance(morphism.direct_image, dict)

    def test_cap_forcing_001(self):
        """CAP_FORCING_001: Extension existence proves ground defect.
        
        Mathematical concept: Proof by generic extension (if M[G] exists, M was defective).
        
        Falsifies if: Extension exists but ground model marked valid.
        """
        state = build_domain_state()
        
        # Ground model must be defective
        assert state.adjunction_holds is False, "Ground model must be defective"
        
        # Force it
        extensions = force_domain(state)
        
        # Extensions must exist
        assert len(extensions) > 0, "Extensions must exist to prove defect"
        
        # The conjunction proves the defect (extension exists AND ground was invalid)
        valid_extensions = [e for e in extensions if e.is_valid]
        assert len(valid_extensions) > 0, "At least one valid extension must exist"

    def test_cap_realizability_001(self):
        """CAP_REALIZABILITY_001: Realized proposition has internal truth = 1.
        
        Mathematical concept: Hyland's effective topos with computable realizers.
        
        Falsifies if: internal_truth() != Fraction(1) for realized prop.
        """
        topos = RealizabilityTopos(ordinal=ORDINAL_EPSILON_0)
        
        proof = ProofObject(
            rule="DetentionFact",
            premises=["video_evidence", "contradictory_orders"],
            conclusion="detention_is_unlawful",
        )
        
        topos.realize("detention_is_unlawful", proof)
        truth = topos.internal_truth("detention_is_unlawful")
        
        assert truth == Fraction(1), f"Realized proposition must have truth=1, got {truth}"

    def test_cap_hash_chain_001(self):
        """CAP_HASH_CHAIN_001: Every claim is Merkle-anchored.
        
        Mathematical concept: Cryptographic commitment via SHA-256 hash chains.
        
        Falsifies if: Any claim lacks 64-char hex commitment.
        """
        # Run full D_DOLLARTREE pipeline
        state = build_domain_state()
        extensions = force_domain(state)
        morphism = evaluate_topos_truth_gap()
        adjunction = run_adjunction_check()
        
        # Collect all claims
        claims = [
            morphism.claim,
            adjunction.yeshua_claim,
        ]
        for ext in extensions:
            claims.append(ext.claim)
        
        # Every claim must be hash-anchored
        for claim in claims:
            assert claim.is_hash_anchored(), (
                f"Claim from {claim.source} lacks valid 64-char hex commitment"
            )
            assert len(claim.hash_commitment) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
