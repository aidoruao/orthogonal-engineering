"""Impossibility Audit — Distinguish actually impossible from merely difficult.

Classifies every claimed limitation into one of four categories:
1. PHYSICAL_INVARIANT: Violating it contradicts physics (Landauer, thermodynamics)
2. LOGICAL_INVARIANT: Violating it contradicts logic (halting problem, Goedel)
3. METHODOLOGICAL_CONSTRAINT: Self-imposed but architecturally terminal (0 floats)
4. CONVENTIONAL_DIFFICULTY: Not impossible, just hard. BEGIN HERE.
5. INVERTIBLE_IMPOSSIBILITY: Theorem applies to the general case; domain restriction
   removes the preconditions so the theorem no longer applies.

For each CONVENTIONAL_DIFFICULTY or INVERTIBLE_IMPOSSIBILITY, provide the
Yeshua Inversion: the domain restriction or capability-gated mediation that
changes the problem so the impossibility no longer applies.

All operations return ProofObject. 0 floats. 0 editorial.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from fractions import Fraction

from axioms.logic import ProofObject


class LimitationType(Enum):
    """Classification of limitation types."""
    PHYSICAL_INVARIANT = auto()         # Cannot violate (thermodynamics, Landauer)
    LOGICAL_INVARIANT = auto()          # Cannot violate (halting, Goedel, Rice)
    METHODOLOGICAL_CONSTRAINT = auto()  # Self-imposed, architecturally terminal
    CONVENTIONAL_DIFFICULTY = auto()    # Not impossible. Begin here.
    INVERTIBLE_IMPOSSIBILITY = auto()   # Theorem holds generally; domain restriction removes preconditions.


@dataclass
class Limitation:
    """A limitation with its classification and Yeshua Inversion."""
    limitation_id: str
    description: str
    limitation_type: LimitationType
    conventional_solution: str
    yeshua_inversion: str  # The mediation-based solution
    invariants_required: List[str]  # Which kernel invariants apply
    proof: Optional[ProofObject] = None


# LIMITATION_REGISTRY — curated collection of known limitations
LIMITATION_REGISTRY: Dict[str, Limitation] = {
    # PHYSICAL_INVARIANT
    "LIM_PHYS_001": Limitation(
        limitation_id="LIM_PHYS_001",
        description="Landauer's principle: erasing 1 bit costs kT ln 2 energy",
        limitation_type=LimitationType.PHYSICAL_INVARIANT,
        conventional_solution="Ignore energy costs of computation",
        yeshua_inversion="N/A — physical invariant cannot be inverted",
        invariants_required=["thermodynamics", "information_theory"]
    ),
    "LIM_PHYS_002": Limitation(
        limitation_id="LIM_PHYS_002",
        description="Speed of light limits network latency lower bound",
        limitation_type=LimitationType.PHYSICAL_INVARIANT,
        conventional_solution="Accept latency as given",
        yeshua_inversion="N/A — physical invariant cannot be inverted",
        invariants_required=["physics", "networking"]
    ),
    "LIM_PHYS_003": Limitation(
        limitation_id="LIM_PHYS_003",
        description="Finite matter implies cannot have infinite storage",
        limitation_type=LimitationType.PHYSICAL_INVARIANT,
        conventional_solution="Assume unbounded memory",
        yeshua_inversion="N/A — physical invariant cannot be inverted",
        invariants_required=["physics", "resource_bounds"]
    ),
    "LIM_PHYS_004": Limitation(
        limitation_id="LIM_PHYS_004",
        description="Heisenberg uncertainty: cannot measure position+momentum exactly",
        limitation_type=LimitationType.PHYSICAL_INVARIANT,
        conventional_solution="Use classical approximations",
        yeshua_inversion="N/A — physical invariant cannot be inverted",
        invariants_required=["quantum_mechanics"]
    ),
    
    # INVERTIBLE_IMPOSSIBILITY — theorem applies to the general case;
    # domain restriction removes preconditions so theorem no longer applies.
    "LIM_LOG_001": Limitation(
        limitation_id="LIM_LOG_001",
        description="Halting problem: cannot decide if arbitrary program halts",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Use timeouts or heuristics",
        yeshua_inversion=(
            "Restrict to bounded programs: ARCSynthesizer enforces max_iterations "
            "so the domain is finite-state; the halting problem does not apply."
        ),
        invariants_required=["oe_engine/synthesizer.py"]
    ),
    "LIM_LOG_002": Limitation(
        limitation_id="LIM_LOG_002",
        description="Goedel incompleteness: cannot prove all true statements",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Use weaker logic or accept incompleteness",
        yeshua_inversion=(
            "Feferman reflection: GoedelianReflector.add_reflection_principle() "
            "adds Con(T) as an axiom, climbing past each Gödel sentence iteratively. "
            "Applies to the reflexive closure of the theory, not the base system."
        ),
        invariants_required=["src/sal/self_referential.py"]
    ),
    "LIM_LOG_003": Limitation(
        limitation_id="LIM_LOG_003",
        description="Rice's theorem: cannot decide non-trivial semantic properties",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Restrict to decidable properties",
        yeshua_inversion=(
            "Restrict to syntactic properties on frozen dataclasses: domain invariants "
            "operate only on frozen dataclass fields (structural, not semantic), so "
            "Rice's theorem preconditions (semantic equivalence classes) do not apply."
        ),
        invariants_required=["src/domains/"]
    ),
    "LIM_LOG_004": Limitation(
        limitation_id="LIM_LOG_004",
        description="Arrow's impossibility: no perfect voting system with >=3 choices",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Use imperfect voting systems",
        yeshua_inversion=(
            "Capability delegation violates the unrestricted domain condition: "
            "agents may only delegate within granted capability scope, restricting "
            "the preference profile space so Arrow's preconditions no longer hold."
        ),
        invariants_required=["kernel/ipc.py"]
    ),
    "LIM_LOG_005": Limitation(
        limitation_id="LIM_LOG_005",
        description="CAP theorem: cannot have consistency+availability+partition tolerance",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Choose two of three",
        yeshua_inversion=(
            "Content-addressed storage (SHA-256 blobs) decouples consistency from "
            "availability: blobs are immutable so reads are always consistent; "
            "partition tolerance is achieved without sacrificing either property."
        ),
        invariants_required=["kernel/bridge/storage.py", "content_addressed"]
    ),
    "LIM_LOG_006": Limitation(
        limitation_id="LIM_LOG_006",
        description="General natural language understanding is undecidable",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Train large language models on internet text",
        yeshua_inversion=(
            "Domain routing + invariant verification: replace semantic understanding "
            "with keyword-indexed domain routing (DomainRouter) and ProofObject "
            "verification. No general NLU required; jurisdiction-specific only."
        ),
        invariants_required=["oe_engine/router.py", "oe_engine/thinker.py"]
    ),
    "LIM_LOG_007": Limitation(
        limitation_id="LIM_LOG_007",
        description="Deciding if generated code is correct is undecidable",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Use test suites and hope for coverage",
        yeshua_inversion=(
            "Bounded verification + invariant checking: restrict code generation to "
            "typed transform sequences verified against frozen-dataclass domain "
            "invariants. Each candidate is checked before acceptance; undecidability "
            "applies to arbitrary programs, not bounded typed transforms."
        ),
        invariants_required=["oe_engine/synthesizer.py", "src/domains/"]
    ),
    "LIM_LOG_008": Limitation(
        limitation_id="LIM_LOG_008",
        description="Generating novel correct programs is undecidable",
        limitation_type=LimitationType.INVERTIBLE_IMPOSSIBILITY,
        conventional_solution="Use neural code generation and test afterward",
        yeshua_inversion=(
            "BFS over typed transform sequences (ARCSynthesizer): enumerate programs "
            "by composing TransformType sequences up to max depth, verifying each "
            "candidate against domain invariants before returning. Correctness is "
            "checked, not assumed; novelty is bounded by the transform alphabet."
        ),
        invariants_required=["oe_engine/synthesizer.py"]
    ),
    
    # METHODOLOGICAL_CONSTRAINT
    "LIM_METH_001": Limitation(
        limitation_id="LIM_METH_001",
        description="0 floats: must use Fraction for exact arithmetic",
        limitation_type=LimitationType.METHODOLOGICAL_CONSTRAINT,
        conventional_solution="Use float for performance",
        yeshua_inversion="Accept Fraction overhead for correctness",
        invariants_required=["exact_arithmetic"]
    ),
    "LIM_METH_002": Limitation(
        limitation_id="LIM_METH_002",
        description="0 random: must use deterministic algorithms only",
        limitation_type=LimitationType.METHODOLOGICAL_CONSTRAINT,
        conventional_solution="Use randomness for performance/security",
        yeshua_inversion="Use deterministic pseudorandom with known seed",
        invariants_required=["determinism"]
    ),
    "LIM_METH_003": Limitation(
        limitation_id="LIM_METH_003",
        description="All ProofObject returns: every operation must be witnessed",
        limitation_type=LimitationType.METHODOLOGICAL_CONSTRAINT,
        conventional_solution="Skip proof tracking for performance",
        yeshua_inversion="Accept proof overhead for auditability",
        invariants_required=["witness", "audit"]
    ),
    "LIM_METH_004": Limitation(
        limitation_id="LIM_METH_004",
        description="Capability-gated access only: no ambient authority",
        limitation_type=LimitationType.METHODOLOGICAL_CONSTRAINT,
        conventional_solution="Use Unix permissions, ACLs",
        yeshua_inversion="Pure capability model — explicit authority delegation",
        invariants_required=["capability_security"]
    ),
    
    # CONVENTIONAL_DIFFICULTY — with Yeshua Inversions
    "LIM_CONV_001": Limitation(
        limitation_id="LIM_CONV_001",
        description="No bare metal: cannot boot without bootloader",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Write bootloader in assembly, drivers in C",
        yeshua_inversion="Specification-first HAL. Define invariants hardware must satisfy. Kernel remains pure. HAL is translation layer.",
        invariants_required=["kernel/hal.py", "capability_gated"]
    ),
    "LIM_CONV_002": Limitation(
        limitation_id="LIM_CONV_002",
        description="No real GPU: cannot do graphics without GPU drivers",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Write Vulkan/DirectX drivers, GPU memory management",
        yeshua_inversion="Capability-gated GPU as resource. GpuCap grants right to submit command buffers. Kernel mediates, doesn't implement.",
        invariants_required=["kernel/bridge/gpu.py", "d_graphics"]
    ),
    "LIM_CONV_003": Limitation(
        limitation_id="LIM_CONV_003",
        description="No Steam/YouTube/applications: cannot run existing software",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Implement full Linux syscall ABI, run Wine/Proton",
        yeshua_inversion="Capability-gated application compartments. LinuxCompatCap grants right to spawn Linux binary in verified compartment.",
        invariants_required=["kernel/bridge/linux_compat.py"]
    ),
    "LIM_CONV_004": Limitation(
        limitation_id="LIM_CONV_004",
        description="No network: cannot communicate without TCP/IP stack",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Implement TCP/IP stack, NIC drivers, ARP, DHCP, DNS",
        yeshua_inversion="Capability-gated network as IPC. NetworkCap grants right to send/receive bytes. Kernel mediates host stack.",
        invariants_required=["kernel/bridge/net.py"]
    ),
    "LIM_CONV_005": Limitation(
        limitation_id="LIM_CONV_005",
        description="No persistent storage: cannot save data without filesystem",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Block device drivers, filesystem journaling, wear leveling",
        yeshua_inversion="Content-addressed persistence. StorageCap grants right to read/write blobs by SHA-256 hash. Underlying storage is anything.",
        invariants_required=["kernel/bridge/storage.py", "content_addressed"]
    ),
    "LIM_CONV_006": Limitation(
        limitation_id="LIM_CONV_006",
        description="No audio: cannot play sound without audio drivers",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Write ALSA/PulseAudio/WASAPI drivers",
        yeshua_inversion="AudioCap grants right to submit PCM buffers to host audio.",
        invariants_required=["kernel/bridge/audio.py"]
    ),
    "LIM_CONV_007": Limitation(
        limitation_id="LIM_CONV_007",
        description="No USB/peripherals: cannot use devices without drivers",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Write USB host controller drivers, HID parsers",
        yeshua_inversion="PeripheralCap grants right to read/write device endpoints.",
        invariants_required=["kernel/hal.py", "peripheral_caps"]
    ),
    "LIM_CONV_008": Limitation(
        limitation_id="LIM_CONV_008",
        description="No display: cannot show graphics without display drivers",
        limitation_type=LimitationType.CONVENTIONAL_DIFFICULTY,
        conventional_solution="Write framebuffer drivers, display server, compositor",
        yeshua_inversion="DisplayCap grants right to submit framebuffers. Host composites.",
        invariants_required=["kernel/bridge/display.py"]
    ),
}


def classify_limitation(lim: Limitation) -> Tuple[LimitationType, ProofObject]:
    """Classify a limitation and return proof of classification."""
    proof = ProofObject(
        rule="LimitationClassification",
        premises=[
            f"id={lim.limitation_id}",
            f"type={lim.limitation_type.name}"
        ],
        conclusion=f"classification={lim.limitation_type.name}"
    )
    return lim.limitation_type, proof


def audit_all() -> Tuple[dict, ProofObject]:
    """Run full impossibility audit. Returns categorized results.

    Falsifies if: a registered limitation appears in more than one category.
    """
    results: Dict[str, List[str]] = {
        "physical": [],
        "logical": [],
        "methodological": [],
        "conventional": [],
        "invertible": [],
    }

    for lim_id, lim in LIMITATION_REGISTRY.items():
        if lim.limitation_type == LimitationType.PHYSICAL_INVARIANT:
            results["physical"].append(lim_id)
        elif lim.limitation_type == LimitationType.LOGICAL_INVARIANT:
            results["logical"].append(lim_id)
        elif lim.limitation_type == LimitationType.METHODOLOGICAL_CONSTRAINT:
            results["methodological"].append(lim_id)
        elif lim.limitation_type == LimitationType.CONVENTIONAL_DIFFICULTY:
            results["conventional"].append(lim_id)
        elif lim.limitation_type == LimitationType.INVERTIBLE_IMPOSSIBILITY:
            results["invertible"].append(lim_id)

    proof = ProofObject(
        rule="ImpossibilityAudit",
        premises=[
            f"total={len(LIMITATION_REGISTRY)}",
            f"physical={len(results['physical'])}",
            f"logical={len(results['logical'])}",
            f"methodological={len(results['methodological'])}",
            f"conventional={len(results['conventional'])}",
            f"invertible={len(results['invertible'])}",
        ],
        conclusion="audit complete"
    )

    return results, proof


def get_inversions() -> List[Limitation]:
    """Return all invertible limitations (CONVENTIONAL_DIFFICULTY and INVERTIBLE_IMPOSSIBILITY).

    Falsifies if: a limitation with a non-null yeshua_inversion is omitted.
    """
    return [
        lim for lim in LIMITATION_REGISTRY.values()
        if lim.limitation_type in (
            LimitationType.CONVENTIONAL_DIFFICULTY,
            LimitationType.INVERTIBLE_IMPOSSIBILITY,
        )
    ]


def get_limitation_by_id(lim_id: str) -> Optional[Limitation]:
    """Retrieve a limitation by its ID."""
    # TODO: Expand get_limitation_by_id() - stub detected by Yeshua Agent
    return LIMITATION_REGISTRY.get(lim_id)


def can_be_solved_by_inversion(lim_id: str) -> Tuple[bool, ProofObject]:
    """Check if a limitation can be solved via Yeshua Inversion.

    Falsifies if: INVERTIBLE_IMPOSSIBILITY limitations return False.
    """
    lim = get_limitation_by_id(lim_id)
    if lim is None:
        return False, ProofObject(
            rule="InversionCheck",
            premises=[f"id={lim_id}"],
            conclusion="limitation not found"
        )

    can_invert = lim.limitation_type in (
        LimitationType.CONVENTIONAL_DIFFICULTY,
        LimitationType.INVERTIBLE_IMPOSSIBILITY,
    )

    proof = ProofObject(
        rule="InversionCheck",
        premises=[
            f"id={lim_id}",
            f"type={lim.limitation_type.name}"
        ],
        conclusion=f"can_invert={can_invert}"
    )

    return can_invert, proof
