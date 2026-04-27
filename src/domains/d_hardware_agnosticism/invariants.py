"""D_HARDWARE_AGNOSTICISM invariant checks."""

from typing import Tuple, List
from fractions import Fraction

from axioms.logic import ProofObject
from src.domains.d_hardware_agnosticism.implementation import (
    APICall,
    InstructionSetRequirement,
    SoftwareRenderer,
    InstructionSet,
    VendorAPI,
    check_no_vendor_lockin,
    check_instruction_set_baseline,
    check_software_renderer_path,
    check_cross_platform_paths,
)


def check_no_vendor_lockin_invariant(api_calls: List[APICall]) -> Tuple[bool, ProofObject]:
    """Invariant: No vendor-specific API calls without fallback.

    Falsifies if: vendor-specific calls lack fallbacks such that acceptable
    falsifies_if: vendor-specific calls lack fallbacks such that acceptable
    coverage drops below 90%.
    """
    report, proof = check_no_vendor_lockin(api_calls)
    
    # Acceptable if coverage >= 90%
    acceptable, _ = report.is_acceptable(Fraction(9, 10))
    
    final_proof = ProofObject(
        rule="NoVendorLockinInvariant",
        premises=proof.premises,
        conclusion=f"acceptable={acceptable}"
    )
    
    return acceptable, final_proof


def check_instruction_set_baseline_invariant(
    instructions: List[InstructionSetRequirement],
    baseline: InstructionSet = InstructionSet.SSE2
) -> Tuple[bool, ProofObject]:
    """Invariant: No ungated instructions above baseline.

    Falsifies if: required instructions exceed baseline without proper gating.
    falsifies_if: required instructions exceed baseline without proper gating.
    """
    return check_instruction_set_baseline(instructions, baseline)


def check_software_renderer_path_invariant(
    # TODO: Expand check_software_renderer_path_invariant() - stub detected by Yeshua Agent
    renderers: List[SoftwareRenderer]
) -> Tuple[bool, ProofObject]:
    """Invariant: At least one software fallback available.

    Falsifies if: no software renderer fallback is available.
    falsifies_if: no software renderer fallback is available.
    """
    return check_software_renderer_path(renderers)


def check_cross_platform_paths_invariant(paths: List[str]) -> Tuple[bool, ProofObject]:
    """Invariant: All paths are cross-platform compatible.

    Falsifies if: any path violates cross-platform compatibility rules.
    falsifies_if: any path violates cross-platform compatibility rules.
    """
    valid, violations, proof = check_cross_platform_paths(paths)
    
    final_proof = ProofObject(
        rule="CrossPlatformPathsInvariant",
        premises=proof.premises + [f"violations={violations}"],
        conclusion=f"valid={valid}"
    )
    
    return valid, final_proof


def run_all_invariants() -> dict:
    """Run all invariant checks and return results.

    Falsifies if: any hardware agnosticism invariant check fails or raises an exception.
    falsifies_if: any hardware agnosticism invariant check fails or raises an exception.
    """
    results = {}
    
    # Test cases
    test_calls = [
        APICall("cudaMalloc", VendorAPI.CUDA, False),
        APICall("vkAllocateMemory", VendorAPI.VULKAN, True),
    ]
    
    report, _ = check_no_vendor_lockin(test_calls)
    acceptable, _ = report.is_acceptable()
    results["vendor_lockin"] = "PASS" if acceptable else "FAIL"
    
    # Test instruction set
    test_instrs = [
        InstructionSetRequirement(InstructionSet.SSE2, True, False),
        InstructionSetRequirement(InstructionSet.AVX512, False, True),  # Gated, not required
    ]
    compliant, _ = check_instruction_set_baseline(test_instrs, InstructionSet.AVX2)
    results["instruction_set"] = "PASS" if compliant else "FAIL"
    
    # Test software renderer
    test_renderers = [
        SoftwareRenderer("SwiftShader", True, "reduced"),
        SoftwareRenderer("WARP", False, "minimal"),
    ]
    has_fallback, _ = check_software_renderer_path(test_renderers)
    results["software_renderer"] = "PASS" if has_fallback else "FAIL"
    
    # Test paths
    test_paths = ["/home/user/file.txt", "data/config.json"]
    valid, _, _ = check_cross_platform_paths(test_paths)
    results["cross_platform_paths"] = "PASS" if valid else "FAIL"
    
    return results
