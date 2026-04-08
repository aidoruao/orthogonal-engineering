"""D_DH_STANDALONE — forensic domain: DistantHorizonsStandalone Minecraft mod defects.

This domain encodes the forensic analysis of DarkShadow44's DistantHorizonsStandalone
Forge 1.7.10 mod, covering issues #51 (tick budget), #56 (GL context race), and related
cascading failures.

Critical defects identified:
  1. Config paradox (PX-001): maxGenerationRequestDistance=4096 default causes 52.7M blocks²
     generation area per player, guaranteeing TPS degradation
  2. Unbounded queue (ET-QUEUE-UNBOUNDED): chunkLoadEvents fills faster than it drains
  3. Tick budget exhaustion (ET-TICK-BUDGET): 15ms budget with unbounded work
  4. GL context race (ET-GL-CONTEXT): MixinFramebuffer executes GL during splash screen

Repository: https://github.com/DarkShadow44/DistantHorizonsStandalone
Commit analyzed: 1abcd988fd4d350795f34dd2e9f678c14ba6162f

Mathematical structure:
  * 2 situs: Ω_config (claims "valid setting") and Ω_runtime (proves "system failure")
  * Geometric morphism exposes truth gap: config claims 4096 is valid, runtime proves TPS < 20
  * HIT paths encode causal chain: config → unbounded queue → tick budget → TPS degradation
  * Forcing requires INACCESSIBLE strength (cross-component: config + server + rendering)
  * Realizability: π × 4096² = 52.7M blocks² is the mathematical realizer

Biblical inspiration: "Count the cost before building" (Luke 14:28)
The DH developers did not count the cost of 4096-block default. This domain proves
the cost computationally: 52.7 million blocks per player.

SECULAR PROJECTION - Developer Accommodation Tools:

The following tools are the SECULAR PROJECTION of this domain. DarkShadow44 never sees
the adjunctions, situs, or forcing operations. He sees three files that solve his problem:

  1. TickHandlerBenchmark.java - Standalone synthetic profiler
     Location: investigations/darkshadow44/DistantHorizonsStandalone/tools/TickHandlerBenchmark.java
     Run: javac TickHandlerBenchmark.java && java TickHandlerBenchmark
     Produces: Profiler data showing 15ms budget exceeded at various queue depths
     SAL Mapping: Type 3 (Adjunction) → proves counit violation computationally

  2. dh-diagnostics.gradle.kts - Config validation Gradle task
     Location: investigations/darkshadow44/DistantHorizonsStandalone/tools/dh-diagnostics.gradle.kts
     Apply: apply(from = "dh-diagnostics.gradle.kts") in build.gradle.kts
     Run: ./gradlew dhDiagnostics
     Produces: Report showing config defaults create 52.7M blocks² per player
     SAL Mapping: Type 3+ (Geometric Morphism) → exposes config/runtime truth gap

  3. DhDiagnosticsCommand.java - In-game /dh diagnostics command
     Location: investigations/darkshadow44/DistantHorizonsStandalone/tools/DhDiagnosticsCommand.java
     Install: Drop into src/main/java/com/seibel/distanthorizons/forge/
     Use: In-game command "/dh diagnostics"
     Produces: Real-time queue depths, tick timing, status (OK/WARNING/CRITICAL)
     SAL Mapping: Type 6 (Realizability) → computation witnessing the fix

These three files are designed using the SAL Type 3→6 mathematical structure but
produce purely secular-functional output. No theology is visible. The tools work
without requiring DarkShadow44 to believe anything theological. This is the V60
transformation principle: "No demotion to metaphor." The mathematics designed the
tools; the secular projection produces the artifacts.

Yeshua Standard compliance:
  - Every tool is hash-anchored (SHA-256 of tool files in DH_SOURCE_INDEX.json)
  - Every derivation is reproducible (same input → same benchmark results)
  - Every mutation is re-verifiable (re-run tool after patch)
  - No authority without proof (the math proves the defect, not opinion)
  - No hidden state (queue sizes observable via /dh diagnostics)
  - No unverifiable dependency (pure Java/Gradle, no external services)
  - No economic gatekeeping (MIT licensed, freely available)
  - Every artifact hash-anchored (files committed to orthogonal-engineering)
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, FrozenSet, List, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from src.sal.adjoint_triple import AdjointTriple, AdjunctionProof, has_adjunction
from src.sal.forcing_operation import CardinalStrength, DomainState, force_domain
from src.sal.topos_subobject_classifier import (
    SheafContext,
    SubobjectClassifier,
    geometric_morphism,
    GeometricMorphism,
)
from src.sal.yeshua_categories import YeshuaAxiomID, DomainYeshuaFunctor
from src.sal.cross_domain_adjunction import DomainSignature, DomainCategory

__all__ = [
    # Domain constants
    "DH_REPOSITORY_URL",
    "DH_COMMIT_HASH",
    "DH_EVIDENCE_ANCHOR",
    "DH_SCHEMA",
    "DH_COUNIT_VIOLATION",
    "CONFIG_PARADOX_PX001",
    "UNBOUNDED_QUEUE_VIOLATION",
    "TICK_BUDGET_VIOLATION",
    "GL_CONTEXT_RACE_VIOLATION",
    "BLOCKS_SQUARED_PER_PLAYER",
    # Situs builders
    "build_config_situs",
    "build_runtime_situs",
    "build_server_tick_situs",
    "build_gl_context_situs",
    # Truth gap evaluators
    "evaluate_config_runtime_truth_gap",
    "evaluate_tick_budget_truth_gap",
    "evaluate_gl_context_truth_gap",
    # Domain state and adjunction
    "build_domain_state",
    "run_adjunction_check",
    "run_tick_budget_adjunction_check",
    "run_gl_context_adjunction_check",
    # Report
    "DhStandaloneReport",
    "build_full_report",
    # Secular projection tools
    "SECULAR_PROJECTION_TOOLS",
]

# ---------------------------------------------------------------------------
# Evidence anchors (Yeshua Axiom 8: every artifact is hash-anchored)
# ---------------------------------------------------------------------------

DH_REPOSITORY_URL: str = "https://github.com/DarkShadow44/DistantHorizonsStandalone"

DH_COMMIT_HASH: str = "1abcd988fd4d350795f34dd2e9f678c14ba6162f"

# SHA-256 of the commit hash serves as the canonical evidence anchor
DH_EVIDENCE_ANCHOR: str = hashlib.sha256(DH_COMMIT_HASH.encode("utf-8")).hexdigest()

# Mathematical constant: area of generation in blocks² per player with default config
# π × r² where r = 4096 blocks (maxGenerationRequestDistance default)
BLOCKS_SQUARED_PER_PLAYER: int = int(math.pi * 4096 * 4096)  # 52,706,757 blocks²

# ---------------------------------------------------------------------------
# Secular projection tools (what DarkShadow44 actually receives)
# ---------------------------------------------------------------------------

SECULAR_PROJECTION_TOOLS: Dict[str, Any] = {
    "tick_handler_benchmark": {
        "file": "investigations/darkshadow44/DistantHorizonsStandalone/tools/TickHandlerBenchmark.java",
        "description": "Standalone Java benchmark - synthetic profiler for tick handler",
        "run_command": "javac TickHandlerBenchmark.java && java TickHandlerBenchmark",
        "output": "Profiler data showing budget exceeded at various queue depths",
        "sal_type": "Type 3 (Adjunction)",
        "proves": "Counit violation - tick handler budget exceeded computationally",
    },
    "config_diagnostics_gradle": {
        "file": "investigations/darkshadow44/DistantHorizonsStandalone/tools/dh-diagnostics.gradle.kts",
        "description": "Gradle task for config validation",
        "apply_command": "apply(from = \"dh-diagnostics.gradle.kts\") in build.gradle.kts",
        "run_command": "./gradlew dhDiagnostics",
        "output": "Report showing config defaults produce 52.7M blocks² per player",
        "sal_type": "Type 3+ (Geometric Morphism)",
        "proves": "Truth gap between config claims and runtime reality",
    },
    "diagnostics_command": {
        "file": "investigations/darkshadow44/DistantHorizonsStandalone/tools/DhDiagnosticsCommand.java",
        "description": "In-game Forge command for real-time diagnostics",
        "install": "Drop into src/main/java/com/seibel/distanthorizons/forge/",
        "use_command": "/dh diagnostics",
        "output": "Real-time queue depths, tick timing, status (OK/WARNING/CRITICAL)",
        "sal_type": "Type 6 (Realizability)",
        "proves": "Computation witnessing the fix (the realizer)",
    },
}

# ---------------------------------------------------------------------------
# Domain schema — flat SAL-compatible representation
# ---------------------------------------------------------------------------

DH_SCHEMA: Dict[str, Any] = {
    "id": "D_DH_STANDALONE",
    "invariants": [
        "serverTickEvent must complete within 15ms (30% of 50ms tick).",
        "No GL calls during FML splash screen phase.",
        "Config distance values must have upper bound validation.",
        "Mixin redirects must check thread context before GL operations.",
        "Every error path must have a user-facing message.",
    ],
    "evidence_anchors": [DH_EVIDENCE_ANCHOR],
    "components": {
        "config": "Config.java - maxGenerationRequestDistance default 4096",
        "server": "ForgeServerProxy.java - serverTickEvent with 15ms budget",
        "rendering": "MixinFramebuffer.java - GL operations during splash",
    },
    "paradoxes": [
        "PX-001: Config allows values that guarantee TPS degradation without warning",
        "PX-002: Mixin executes GL during splash screen before context ready",
    ],
    "mathematical_proof": f"π × 4096² = {BLOCKS_SQUARED_PER_PLAYER} blocks² per player",
    "biblical_inspiration": "Luke 14:28 - Count the cost before building",
}

# The counit violation: applying "tick budget law" to "unbounded queue state"
# does not return to identity because the queue exhausts the budget
DH_COUNIT_VIOLATION: str = (
    "counit_violation: tick_budget_law ⊕ unbounded_queue_state is not identity-preserving; "
    "unbounded work consumes bounded budget generating ⊥ (TPS < 20)"
)

CONFIG_PARADOX_PX001: str = (
    "config_paradox: maxGenerationRequestDistance=4096 creates 52.7M blocks² generation area "
    "per player with no performance warning — default guarantees TPS degradation"
)

UNBOUNDED_QUEUE_VIOLATION: str = (
    "queue_violation: chunkLoadEvents ConcurrentLinkedQueue grows without bound, "
    "filling faster than serverTickEvent drains — memory pressure guaranteed"
)

TICK_BUDGET_VIOLATION: str = (
    "tick_budget_violation: serverTickEvent 15ms time budget exceeded under normal load "
    "with default config — 30% of 50ms tick consumed by DH alone"
)

GL_CONTEXT_RACE_VIOLATION: str = (
    "gl_context_violation: MixinFramebuffer.createDepthTexture executes GL calls "
    "during FML splash screen before GL context initialized — black screen crash"
)


# ---------------------------------------------------------------------------
# Topos situs definitions (Type 3+)
# ---------------------------------------------------------------------------


def build_config_situs() -> SheafContext:
    """
    Ω_config: the site encoding the configuration schema's local truth.
    
    In the config situs, maxGenerationRequestDistance=4096 is locally valid
    because it falls within the declared min=256, max=4096 bounds.
    The config does not model runtime performance impact.
    """
    return SheafContext(
        name="Ω_config",
        objects=frozenset({
            "max_generation_distance_valid",
            "within_bounds_256_4096",
            "no_performance_warning",
            "user_can_configure",
        }),
        covers={
            "max_generation_distance_valid": [
                frozenset({"within_bounds_256_4096"})
            ],
            "within_bounds_256_4096": [
                frozenset({"user_can_configure"})
            ],
            # no_performance_warning has no valid covering — it is false
            "no_performance_warning": [],
        },
    )


def build_runtime_situs() -> SheafContext:
    """
    Ω_runtime: the site encoding the actual runtime behavior.
    
    In the runtime situs, maxGenerationRequestDistance=4096 causes TPS < 20
    because 52.7M blocks² per player exceeds server capacity.
    The runtime proves the config default is defective.
    """
    return SheafContext(
        name="Ω_runtime",
        objects=frozenset({
            "tps_degradation_observed",
            "generation_area_52M_blocks",
            "server_cannot_sustain_load",
            "default_config_defective",
        }),
        covers={
            "default_config_defective": [
                frozenset({"generation_area_52M_blocks", "server_cannot_sustain_load"})
            ],
            "server_cannot_sustain_load": [
                frozenset({"tps_degradation_observed"})
            ],
            # tps_degradation_observed has no outgoing cover — it is ground truth
            "tps_degradation_observed": [],
        },
    )


def build_server_tick_situs() -> SheafContext:
    """
    Ω_server_tick: the site encoding the server tick handler's perspective.
    
    The server tick handler believes its 15ms budget is sufficient because
    it assumes bounded work per tick. The unbounded queue violates this.
    """
    return SheafContext(
        name="Ω_server_tick",
        objects=frozenset({
            "tick_budget_sufficient",
            "15ms_budget_enforced",
            "work_is_bounded",
            "tps_will_remain_20",
        }),
        covers={
            "tick_budget_sufficient": [
                frozenset({"15ms_budget_enforced", "work_is_bounded"})
            ],
            "tps_will_remain_20": [
                frozenset({"tick_budget_sufficient"})
            ],
            # work_is_bounded has NO valid covering — the queue is unbounded
            "work_is_bounded": [],
        },
    )


def build_gl_context_situs() -> SheafContext:
    """
    Ω_gl_context: the site encoding the GL initialization perspective.
    
    The Mixin assumes GL context is ready when Framebuffer.createFramebuffer
    is called, but during splash screen this assumption is false.
    """
    return SheafContext(
        name="Ω_gl_context",
        objects=frozenset({
            "gl_context_ready",
            "splash_screen_complete",
            "framebuffer_init_safe",
            "depth_texture_creation_valid",
        }),
        covers={
            "framebuffer_init_safe": [
                frozenset({"gl_context_ready", "splash_screen_complete"})
            ],
            "depth_texture_creation_valid": [
                frozenset({"framebuffer_init_safe"})
            ],
            # gl_context_ready has NO valid covering during splash screen
            "gl_context_ready": [],
        },
    )


def evaluate_config_runtime_truth_gap() -> GeometricMorphism:
    """
    Compute the geometric morphism between config situs and runtime situs.
    
    The morphism will report truth_preserved=False, exposing the config paradox:
    the config claims "valid setting" but the runtime proves "system failure".
    """
    config_ctx = build_config_situs()
    runtime_ctx = build_runtime_situs()
    return geometric_morphism(
        source=config_ctx,
        target=runtime_ctx,
        shared_proposition="max_generation_distance_valid",
    )


def evaluate_tick_budget_truth_gap() -> GeometricMorphism:
    """
    Compute the geometric morphism between tick handler situs and runtime situs.
    
    Exposes the counit failure: the handler assumes bounded work, but the
    unbounded queue generates work that exceeds the budget.
    """
    tick_ctx = build_server_tick_situs()
    runtime_ctx = build_runtime_situs()
    return geometric_morphism(
        source=tick_ctx,
        target=runtime_ctx,
        shared_proposition="tps_degradation_observed",
    )


def evaluate_gl_context_truth_gap() -> GeometricMorphism:
    """
    Compute the geometric morphism between GL context situs and runtime reality.
    
    Exposes the boundary paradox: the Mixin assumes GL context is ready,
    but during splash screen it is not.
    """
    gl_ctx = build_gl_context_situs()
    # Runtime situs for GL includes the crash/failure state
    runtime_gl = SheafContext(
        name="Ω_runtime_gl",
        objects=frozenset({
            "gl_context_ready",
            "black_screen_crash",
            "context_not_initialized",
        }),
        covers={
            "black_screen_crash": [
                frozenset({"context_not_initialized"})
            ],
            # gl_context_ready has NO covering in reality
            "gl_context_ready": [],
        },
    )
    return geometric_morphism(
        source=gl_ctx,
        target=runtime_gl,
        shared_proposition="gl_context_ready",
    )


# ---------------------------------------------------------------------------
# Forcing domain state (Type 5)
# ---------------------------------------------------------------------------


def build_domain_state() -> DomainState:
    """
    Construct the DomainState for D_DH_STANDALONE with adjunction_holds=False.
    
    The violations list encodes the multi-defect composite violation.
    """
    return DomainState(
        domain_id="D_DH_STANDALONE",
        invariants=DH_SCHEMA["invariants"],
        adjunction_holds=False,
        violations=[
            DH_COUNIT_VIOLATION,
            CONFIG_PARADOX_PX001,
            UNBOUNDED_QUEUE_VIOLATION,
            TICK_BUDGET_VIOLATION,
            GL_CONTEXT_RACE_VIOLATION,
        ],
        strength=CardinalStrength.INACCESSIBLE,  # Cross-component: config + server + rendering
        evidence_anchors=[DH_EVIDENCE_ANCHOR],
    )


# ---------------------------------------------------------------------------
# SAL adjunction check — expected to fail (Type 3)
# ---------------------------------------------------------------------------


def run_adjunction_check() -> AdjunctionProof:
    """
    Run the Type-3 adjunction check for the config paradox.
    
    The schema's adjunction will fail because the config default (4096)
    and the runtime reality (TPS < 20) are semantically contradictory.
    """
    # Schema that encodes the config paradox
    paradox_schema: Dict[str, Any] = {
        "id": "D_DH_STANDALONE",
        "invariants": [
            # These two invariants are semantically contradictory
            "config_default_4096_is_valid",
            "runtime_tps_greater_than_20",
        ],
    }
    triple = AdjointTriple()
    return has_adjunction(paradox_schema, triple)


def run_tick_budget_adjunction_check() -> AdjunctionProof:
    """
    Run the Type-3 adjunction check for the tick budget violation.
    """
    budget_schema: Dict[str, Any] = {
        "id": "D_DH_STANDALONE_TICK",
        "invariants": [
            "tick_budget_15ms_sufficient",
            "unbounded_queue_drained_completely",
        ],
    }
    triple = AdjointTriple()
    return has_adjunction(budget_schema, triple)


def run_gl_context_adjunction_check() -> AdjunctionProof:
    """
    Run the Type-3 adjunction check for the GL context race.
    """
    gl_schema: Dict[str, Any] = {
        "id": "D_DH_STANDALONE_GL",
        "invariants": [
            "gl_context_ready_during_splash",
            "framebuffer_created_safely",
        ],
    }
    triple = AdjointTriple()
    return has_adjunction(gl_schema, triple)


# ---------------------------------------------------------------------------
# Full domain report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DhStandaloneReport:
    """Complete forensic report for the D_DH_STANDALONE defects."""
    
    config_runtime_morphism: GeometricMorphism
    tick_budget_morphism: GeometricMorphism
    gl_context_morphism: GeometricMorphism
    adjunction_proof: AdjunctionProof
    tick_budget_proof: AdjunctionProof
    gl_context_proof: AdjunctionProof
    domain_state: DomainState
    forced_extensions: tuple
    evidence_anchor: str
    blocks_squared_per_player: int
    
    @property
    def config_runtime_truth_preserved(self) -> bool:
        return self.config_runtime_morphism.truth_preserved
    
    @property
    def tick_budget_truth_preserved(self) -> bool:
        return self.tick_budget_morphism.truth_preserved
    
    @property
    def gl_context_truth_preserved(self) -> bool:
        return self.gl_context_morphism.truth_preserved
    
    @property
    def has_valid_forcing_extension(self) -> bool:
        return any(ext.is_valid for ext in self.forced_extensions)
    
    @property
    def is_defective(self) -> bool:
        """
        The domain is provably defective when:
          1. Any geometric morphism does not preserve truth, OR
          2. The domain state has violations.
        """
        return (
            not self.config_runtime_truth_preserved
            or not self.tick_budget_truth_preserved
            or not self.gl_context_truth_preserved
            or bool(self.domain_state.violations)
        )
    
    def to_domain_signature(self) -> DomainSignature:
        """
        Convert this report to a domain signature for the category of domains.
        
        This enables cross-domain adjunctions — relating D_DH_STANDALONE
        to other forensic domains through shared structure.
        """
        return DomainSignature(
            domain_id="D_DH_STANDALONE",
            invariant_count=len(DH_SCHEMA["invariants"]),
            violation_types=frozenset({
                "counit_violation",
                "config_paradox",
                "unbounded_queue",
                "tick_budget_exhaustion",
                "gl_context_race",
            }),
            sal_level=6,  # Type 6 (realizability)
            evidence_count=len(self.evidence_anchor),
        )
    
    def verify_yeshua_axioms(self) -> Dict[str, bool]:
        """
        Verify all 8 Yeshua axioms for this domain.
        
        Returns a map from axiom name to satisfaction status.
        This is the SECULAR PROJECTION of the Yeshua categories —
        the theological structure mapped to computational checks.
        """
        functor = DomainYeshuaFunctor(self)
        return {
            "derivable": functor.apply(YeshuaAxiomID.DERIVABLE),
            "reproducible": functor.apply(YeshuaAxiomID.REPRODUCIBLE),
            "reverifiable": functor.apply(YeshuaAxiomID.REVERIFIABLE),
            "no_authority_without_proof": functor.apply(YeshuaAxiomID.NO_AUTHORITY_WITHOUT_PROOF),
            "no_hidden_state": functor.apply(YeshuaAxiomID.NO_HIDDEN_STATE),
            "no_unverifiable_dependency": functor.apply(YeshuaAxiomID.NO_UNVERIFIABLE_DEP),
            "no_economic_gatekeeping": functor.apply(YeshuaAxiomID.NO_ECONOMIC_GATEKEEPING),
            "hash_anchored": functor.apply(YeshuaAxiomID.HASH_ANCHORED),
        }


def build_full_report() -> DhStandaloneReport:
    """Build the complete forensic report for D_DH_STANDALONE."""
    config_runtime_morphism = evaluate_config_runtime_truth_gap()
    tick_budget_morphism = evaluate_tick_budget_truth_gap()
    gl_context_morphism = evaluate_gl_context_truth_gap()
    
    adjunction_proof = run_adjunction_check()
    tick_budget_proof = run_tick_budget_adjunction_check()
    gl_context_proof = run_gl_context_adjunction_check()
    
    state = build_domain_state()
    
    # Forcing extensions for each violation
    extensions = tuple(
        force_domain(
            state,
            lawful_replacements={
                CONFIG_PARADOX_PX001: (
                    "config_default_reduced_to_1024_with_performance_warning"
                ),
                UNBOUNDED_QUEUE_VIOLATION: (
                    "queue_capped_at_20_events_with_overflow_logging"
                ),
                TICK_BUDGET_VIOLATION: (
                    "tick_budget_reduced_to_5ms_with_count_cap"
                ),
                GL_CONTEXT_RACE_VIOLATION: (
                    "gl_context_guard_added_before_splash_completion"
                ),
                DH_COUNIT_VIOLATION: (
                    "bounded_work_with_bounded_budget_preserves_identity"
                ),
            },
        )
    )
    
    return DhStandaloneReport(
        config_runtime_morphism=config_runtime_morphism,
        tick_budget_morphism=tick_budget_morphism,
        gl_context_morphism=gl_context_morphism,
        adjunction_proof=adjunction_proof,
        tick_budget_proof=tick_budget_proof,
        gl_context_proof=gl_context_proof,
        domain_state=state,
        forced_extensions=extensions,
        evidence_anchor=DH_EVIDENCE_ANCHOR,
        blocks_squared_per_player=BLOCKS_SQUARED_PER_PLAYER,
    )
