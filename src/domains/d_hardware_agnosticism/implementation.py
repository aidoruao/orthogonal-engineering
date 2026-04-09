"""D_HARDWARE_AGNOSTICISM implementation — Universal Compatibility Layer.

Vendor lock-in detection, instruction set baseline, software fallback.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Set
from fractions import Fraction
from enum import Enum, auto
from pathlib import Path

from axioms.logic import ProofObject


class VendorAPI(Enum):
    """Vendor-specific APIs that may cause lock-in."""
    CUDA = "cuda"
    HIP = "hip"
    METAL = "metal"
    DIRECTML = "directml"
    VULKAN = "vulkan"
    OPENCL = "opencl"


class InstructionSet(Enum):
    """CPU instruction sets."""
    SSE2 = "SSE2"
    AVX = "AVX"
    AVX2 = "AVX2"
    AVX512 = "AVX-512"
    NEON = "NEON"
    WASM = "WASM"


@dataclass(frozen=True)
class APICall:
    """A single API call in code."""
    function_name: str
    vendor: VendorAPI
    has_fallback: bool


@dataclass(frozen=True)
class VendorLockinReport:
    """Report on vendor lock-in issues."""
    locked_calls: List[APICall]
    fallback_coverage: Fraction  # Ratio of calls with fallbacks
    
    def is_acceptable(self, threshold: Fraction = Fraction(9, 10)) -> Tuple[bool, ProofObject]:
        """Check if fallback coverage meets threshold."""
        acceptable = self.fallback_coverage >= threshold
        
        proof = ProofObject(
            rule="VendorLockinAcceptable",
            premises=[
                f"fallback_coverage={self.fallback_coverage}",
                f"threshold={threshold}",
                f"locked_calls={len(self.locked_calls)}"
            ],
            conclusion=f"acceptable={acceptable}"
        )
        
        return acceptable, proof


def check_no_vendor_lockin(api_calls: List[APICall]) -> Tuple[VendorLockinReport, ProofObject]:
    """Check for vendor lock-in in API calls.
    
    Flags calls like cudaMalloc without HIP/Vulkan fallback.
    
    Returns report with locked calls and fallback coverage ratio.
    """
    locked_calls = [call for call in api_calls if not call.has_fallback]
    
    if api_calls:
        coverage = Fraction(len(api_calls) - len(locked_calls)) / Fraction(len(api_calls))
    else:
        coverage = Fraction(1)
    
    report = VendorLockinReport(
        locked_calls=locked_calls,
        fallback_coverage=coverage
    )
    
    proof = ProofObject(
        rule="VendorLockinCheck",
        premises=[
            f"total_calls={len(api_calls)}",
            f"locked_calls={len(locked_calls)}",
            f"coverage={coverage}"
        ],
        conclusion=f"coverage={coverage}"
    )
    
    return report, proof


@dataclass(frozen=True)
class InstructionSetRequirement:
    """Instruction set requirement for code."""
    instruction: InstructionSet
    is_required: bool  # If True, code won't run without it
    is_gated: bool     # If True, there's a runtime check


def check_instruction_set_baseline(instructions: List[InstructionSetRequirement],
                                   baseline: InstructionSet) -> Tuple[bool, ProofObject]:
    """Check that no instructions exceed baseline unless gated.
    
    Ensures no AVX-512 unless gated.
    
    Args:
        instructions: List of instruction requirements
        baseline: Maximum allowed baseline instruction set
    
    Returns:
        (compliant, proof)
    """
    # Define instruction set hierarchy
    hierarchy = {
        InstructionSet.SSE2: 0,
        InstructionSet.AVX: 1,
        InstructionSet.AVX2: 2,
        InstructionSet.AVX512: 3,
        InstructionSet.NEON: 1,
        InstructionSet.WASM: 0,
    }
    
    baseline_level = hierarchy.get(baseline, 0)
    violations = []
    
    for req in instructions:
        instr_level = hierarchy.get(req.instruction, 0)
        if instr_level > baseline_level and req.is_required and not req.is_gated:
            violations.append(req.instruction.value)
    
    compliant = len(violations) == 0
    
    proof = ProofObject(
        rule="InstructionSetBaseline",
        premises=[
            f"baseline={baseline.value}",
            f"baseline_level={baseline_level}",
            f"violations={violations}"
        ],
        conclusion=f"compliant={compliant}"
    )
    
    return compliant, proof


@dataclass(frozen=True)
class SoftwareRenderer:
    """Software renderer fallback capability."""
    name: str
    available: bool
    performance_level: str  # "full", "reduced", "minimal"


def check_software_renderer_path(renderers: List[SoftwareRenderer]) -> Tuple[bool, ProofObject]:
    """Check that at least one software fallback exists.
    
    At least one of: SwiftShader, WARP, LLVMpipe must be available.
    """
    available_count = sum(1 for r in renderers if r.available)
    has_fallback = available_count > 0
    
    proof = ProofObject(
        rule="SoftwareRendererPath",
        premises=[
            f"renderers={[(r.name, r.available) for r in renderers]}",
            f"available_count={available_count}"
        ],
        conclusion=f"has_fallback={has_fallback}"
    )
    
    return has_fallback, proof


def check_cross_platform_paths(paths: List[str]) -> Tuple[bool, List[str], ProofObject]:
    """Check that paths are cross-platform compatible.
    
    No backslashes, no drive letters, all pathlib-compatible.
    
    Returns:
        (all_valid, violations, proof)
    """
    violations = []
    
    for path_str in paths:
        # Check for backslashes (Windows-only)
        if '\\\\' in path_str:
            violations.append(f"Backslash in: {path_str}")
        
        # Check for drive letters (Windows-only)
        if len(path_str) > 1 and path_str[1] == ':':
            violations.append(f"Drive letter in: {path_str}")
        
        # Try to create Path object
        try:
            p = Path(path_str)
            # Check if it's a valid POSIX-style path
            if not p.as_posix() == path_str.replace('\\', '/'):
                violations.append(f"Not POSIX-compatible: {path_str}")
        except Exception as e:
            violations.append(f"Invalid path '{path_str}': {e}")
    
    all_valid = len(violations) == 0
    
    proof = ProofObject(
        rule="CrossPlatformPaths",
        premises=[
            f"path_count={len(paths)}",
            f"violation_count={len(violations)}"
        ],
        conclusion=f"all_valid={all_valid}"
    )
    
    return all_valid, violations, proof


@dataclass(frozen=True)
class APIFallbackMapping:
    """Mapping from primary API to fallback APIs."""
    primary: VendorAPI
    fallbacks: List[VendorAPI]
    feature_parity: Fraction  # How much of primary API is covered by fallbacks


def check_api_fallback_parity(mapping: APIFallbackMapping,
                              min_parity: Fraction) -> Tuple[bool, ProofObject]:
    """Check that fallback APIs have sufficient feature parity.
    
    Args:
        mapping: API to fallback mapping
        min_parity: Minimum acceptable feature parity
    
    Returns:
        (sufficient, proof)
    """
    sufficient = mapping.feature_parity >= min_parity
    
    proof = ProofObject(
        rule="APIFallbackParity",
        premises=[
            f"primary={mapping.primary.value}",
            f"fallbacks={[f.value for f in mapping.fallbacks]}",
            f"feature_parity={mapping.feature_parity}",
            f"min_parity={min_parity}"
        ],
        conclusion=f"sufficient={sufficient}"
    )
    
    return sufficient, proof


# Common software renderers
SWIFTSHADER = SoftwareRenderer("SwiftShader", False, "reduced")
WARP = SoftwareRenderer("WARP", False, "minimal")
LLVMPIPE = SoftwareRenderer("LLVMpipe", False, "reduced")
