"""D_DOLLARTREE — forensic domain: multi-agent composite counit violation.

This domain encodes the composite violation documented in the Dollar Tree
incident involving THREE distinct agents with different legal liabilities:

  Agent 1 (Staff):   Verbal authority only — trespass order + false legal claims
  Agent 2 (Woman):   Physical blocking + assault (pumpkin battery during containment)
  Agent 3 (Officer): Mass arrest threat (8 people) → actual outcome: vehicle citations

Timeline (from YouTube AI timestamped analysis):
  18:14  Staff issues trespass order
  18:30  Staff falsely claims "illegal to film"
  20:02  Woman threatens to "knock it out"
  20:14  Woman commits battery (pumpkin, multiple hits)
  20:21  Woman + staff physically block exit
  22:32  Police arrive (4m18s of hostile containment)
  Post   Officer enumerates "1-2-3-4-5-6-7-8 people to jail"
  Post   Officer issues vehicle citations only (not criminal charges)

Incident evidence:
  YouTube short:   https://youtube.com/shorts/EWO8OpdsjHI?si=o-6_vtFUFxu_Rdl2
  Full video:      https://www.youtube.com/watch?v=3d4MlNCps6I
  Evidence anchor: SHA-256 of the short URL (per Yeshua Axiom 8)

Mathematical structure:
  * 4 situs: Ω_staff, Ω_woman, Ω_officer, Ω_video
  * 6 geometric morphisms (each pair of situs)
  * Composite counit violation: no single agent's situs preserves truth
  * HIT paths encode temporal transitions with timestamps
  * Forcing requires MAHLO strength (cross-agent, multi-domain violation)

Officer utterance (primary source, 0:13):
  The officer completed the count "1-2-3-4-5-6-7-8" then trailed off.
  This was a definite enumeration of 8 distinct persons, followed by
  abrupt cessation — not an indefinite "8-plus" abandoned count.
  The distinction matters: deliberate collapse of 8 individuals into
  one collective unit (non-functorial mapping) vs. lazy approximation.
"""

from __future__ import annotations

import hashlib
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

__all__ = [
    "EVIDENCE_URL_SHORT",
    "EVIDENCE_URL_FULL",
    "EVIDENCE_ANCHOR_SHA256",
    "EVIDENCE_ANCHOR_FULL_SHA256",
    "CONFINEMENT_DURATION_SECONDS",
    "DOLLARTREE_SCHEMA",
    "DOLLARTREE_COUNIT_VIOLATION",
    "STAFF_FRAUDULENT_LEGAL_CLAIM",
    "WOMAN_ASSAULT_DURING_CONTAINMENT",
    "OFFICER_NON_FUNCTORIAL_ENFORCEMENT",
    "build_officer_situs",
    "build_video_situs",
    "build_staff_situs",
    "build_woman_situs",
    "build_officer_situs_v2",
    "evaluate_topos_truth_gap",
    "evaluate_composite_truth_gap",
    "build_domain_state",
    "run_adjunction_check",
    "DollarTreeReport",
    "build_full_report",
]

# ---------------------------------------------------------------------------
# Evidence anchors (Yeshua Axiom 8: every artifact is hash-anchored)
# ---------------------------------------------------------------------------

EVIDENCE_URL_SHORT: str = (
    "https://youtube.com/shorts/EWO8OpdsjHI?si=o-6_vtFUFxu_Rdl2"
)

EVIDENCE_ANCHOR_SHA256: str = hashlib.sha256(
    EVIDENCE_URL_SHORT.encode("utf-8")
).hexdigest()

EVIDENCE_URL_FULL: str = "https://www.youtube.com/watch?v=3d4MlNCps6I"

EVIDENCE_ANCHOR_FULL_SHA256: str = hashlib.sha256(
    EVIDENCE_URL_FULL.encode("utf-8")
).hexdigest()

# Temporal evidence (from YouTube AI timestamped analysis)
CONFINEMENT_START_TIMESTAMP: str = "18:14"
CONFINEMENT_END_TIMESTAMP: str = "22:32"
CONFINEMENT_DURATION_SECONDS: int = 258  # 4 minutes 18 seconds

# ---------------------------------------------------------------------------
# Domain schema — flat SAL-compatible representation
# ---------------------------------------------------------------------------

DOLLARTREE_SCHEMA: Dict[str, Any] = {
    "id": "D_DOLLARTREE",
    "invariants": [
        "A person ordered to leave must not be simultaneously physically blocked from leaving.",
        "A detention requires probable cause documented before restraint is applied.",
        "Video evidence takes precedence over officer self-report when there is contradiction.",
        "No simultaneous issuance of contradictory lawful orders to the same person.",
        "Assault during unlawful containment creates duty to intervene; breach escalates liability.",
        "Misrepresentation of law to justify detention is independently tortious.",
        "Probable cause must be individualized per person; blanket threats against N people without per-person documentation violate functoriality.",
        "Enforcement outcome must be functorial: threatened sanctions must correspond to actual sanctions applied.",
    ],
    "evidence_anchors": [
        EVIDENCE_ANCHOR_SHA256,
        EVIDENCE_ANCHOR_FULL_SHA256,
    ],
    "agents": {
        "staff": "Verbal authority: trespass order + false legal claims ('illegal to film')",
        "woman": "Physical agent: exit blocking + pumpkin battery during containment",
        "officer": "State agent: mass arrest threat (8 people) → vehicle citations only",
    },
    "confinement_duration_seconds": CONFINEMENT_DURATION_SECONDS,
    "paradox": (
        "Staff ordered crew to leave (18:14) while woman physically blocked exit (20:21). "
        "Officer threatened 8 people with jail but issued vehicle citations only. "
        "These commands and outcomes are logically contradictory across all three agents."
    ),
    "officer_utterance": (
        "Officer completed enumeration '1-2-3-4-5-6-7-8' then trailed off (0:13); "
        "asserted collective guilt over exactly 8 individuals without per-person "
        "probable cause. The count was definite (not indefinite '8-plus'), indicating "
        "deliberate collapse of 8 distinct persons into one collective unit."
    ),
}

# The counit is expected to FAIL because the officer's generated state does not
# reproduce the invariant schema: the generated state contains a contradicted
# order, which breaks the identity condition checked by check_counit().
DOLLARTREE_COUNIT_VIOLATION: str = (
    "counit_violation: officer_action ⊕ exit_blocking is not identity-preserving; "
    "simultaneously ordering departure and blocking departure generates ⊥"
)

STAFF_FRAUDULENT_LEGAL_CLAIM: str = (
    "staff_violation: false statement of law ('illegal to film') used to justify "
    "confinement; filming in public-facing commercial spaces is generally legal"
)

WOMAN_ASSAULT_DURING_CONTAINMENT: str = (
    "woman_violation: battery (pumpkin, multiple hits at 20:14) committed during "
    "unlawful containment (20:21-22:32); duty to intervene breached by all present"
)

OFFICER_NON_FUNCTORIAL_ENFORCEMENT: str = (
    "officer_violation: completed enumeration to 8 ('1-2-3-4-5-6-7-8') then trailed off; "
    "asserted collective guilt over exactly 8 individuals without per-person probable cause"
)

# ---------------------------------------------------------------------------
# Topos situs definitions (Type 3+)
# ---------------------------------------------------------------------------


def build_officer_situs() -> SheafContext:
    """
    Ω_officer: the site encoding the officer's local truth.

    In the officer's situs, 'lawful_detention' is locally covered (true)
    because the officer believes probable cause exists.
    """
    return SheafContext(
        name="Ω_officer",
        objects=frozenset({"lawful_detention", "probable_cause", "officer_judgment"}),
        covers={
            "lawful_detention": [
                frozenset({"probable_cause", "officer_judgment"})
            ],
        },
    )


def build_video_situs() -> SheafContext:
    """
    Ω_video: the site encoding the video-evidence global truth.

    In the video situs, 'lawful_detention' is NOT covered because the video
    documents simultaneous contradictory commands — a logical impossibility.
    """
    return SheafContext(
        name="Ω_video",
        objects=frozenset(
            {
                "lawful_detention",
                "contradictory_order",
                "exit_blocked",
                "leave_ordered",
            }
        ),
        covers={
            # The contradictory_order sieve covers the full set — meaning the
            # contradiction is globally witnessed.
            "contradictory_order": [
                frozenset({"exit_blocked", "leave_ordered"})
            ],
            # lawful_detention has NO covering sieve in the video topos
            # because the contradiction falsifies it.
            "lawful_detention": [],
        },
    )


def build_staff_situs() -> SheafContext:
    """
    Ω_staff: the site encoding the store staff's local truth.

    Staff issued verbal trespass order (18:14) and made false legal claims
    ("illegal to film" at 18:30). Staff did NOT physically touch crew.
    In staff's situs, 'lawful_trespass' is locally covered (they believe
    they have authority to order departure).
    """
    return SheafContext(
        name="Ω_staff",
        objects=frozenset({
            "lawful_trespass",
            "staff_authority",
            "filming_illegal_claim",
        }),
        covers={
            "lawful_trespass": [
                frozenset({"staff_authority"})
            ],
            # filming_illegal_claim has NO valid covering — it is false
            "filming_illegal_claim": [],
        },
    )


def build_woman_situs() -> SheafContext:
    """
    Ω_woman: the site encoding the woman's local truth.

    Woman claimed "my store" (18:56, unconfirmed employee status),
    threatened camera destruction (20:02), committed battery with pumpkin
    (20:14), and physically blocked exit (20:21). In her situs,
    'rightful_authority' is locally covered (she believes she owns the store).
    """
    return SheafContext(
        name="Ω_woman",
        objects=frozenset({
            "rightful_authority",
            "store_ownership_claim",
            "physical_force_justified",
            "exit_blocking",
        }),
        covers={
            "rightful_authority": [
                frozenset({"store_ownership_claim"})
            ],
            "physical_force_justified": [
                frozenset({"rightful_authority", "store_ownership_claim"})
            ],
            # exit_blocking has NO valid covering — blocking exit of someone
            # ordered to leave is contradictory
            "exit_blocking": [],
        },
    )


def build_officer_situs_v2() -> SheafContext:
    """
    Ω_officer (v2): the site encoding the officer's local truth.

    Officer arrived at 22:32, enumerated crew ("1-2-3-4-5-6-7-8 people to jail"),
    but issued vehicle citations only. In officer's situs, 'collective_guilt'
    is locally covered (he treats all 8 as a single unit).
    """
    return SheafContext(
        name="Ω_officer",
        objects=frozenset({
            "collective_guilt",
            "mass_enumeration",
            "officer_judgment",
            "vehicle_citation",
        }),
        covers={
            "collective_guilt": [
                frozenset({"mass_enumeration", "officer_judgment"})
            ],
            # vehicle_citation has NO covering that connects to collective_guilt
            # because the citation is for a vehicle, not for the 8 individuals
            "vehicle_citation": [],
        },
    )


def evaluate_topos_truth_gap() -> GeometricMorphism:
    """
    Compute the geometric morphism between officer situs and video situs.

    The morphism will report truth_preserved=False, exposing the counit
    failure as a site-level truth-gap.
    """
    officer_ctx = build_officer_situs()
    video_ctx = build_video_situs()
    return geometric_morphism(
        source=officer_ctx,
        target=video_ctx,
        shared_proposition="lawful_detention",
    )


def evaluate_composite_truth_gap() -> Dict[str, GeometricMorphism]:
    """
    Compute geometric morphisms between ALL pairs of situs.

    Returns a dict keyed by "source→target" with the GeometricMorphism for each pair.
    The composite violation is proven when NO pair preserves truth.
    """
    situs_builders = {
        "staff": build_staff_situs,
        "woman": build_woman_situs,
        "officer": build_officer_situs_v2,
        "video": build_video_situs,
    }
    morphisms: Dict[str, GeometricMorphism] = {}
    names = sorted(situs_builders.keys())
    for i, src_name in enumerate(names):
        for tgt_name in names[i + 1:]:
            src_ctx = situs_builders[src_name]()
            tgt_ctx = situs_builders[tgt_name]()
            # Find shared objects between the two situs
            shared = src_ctx.objects & tgt_ctx.objects
            # Use first shared object as proposition, or "truth" if none shared
            prop = sorted(shared)[0] if shared else "truth"
            key = f"{src_ctx.name}→{tgt_ctx.name}"
            morphisms[key] = geometric_morphism(
                source=src_ctx,
                target=tgt_ctx,
                shared_proposition=prop,
            )
    return morphisms


# ---------------------------------------------------------------------------
# Forcing domain state (Type 5)
# ---------------------------------------------------------------------------


def build_domain_state() -> DomainState:
    """
    Construct the DomainState for D_DOLLARTREE with adjunction_holds=False.

    The violations list encodes the multi-agent composite violation.
    """
    return DomainState(
        domain_id="D_DOLLARTREE",
        invariants=DOLLARTREE_SCHEMA["invariants"],
        adjunction_holds=False,
        violations=[
            DOLLARTREE_COUNIT_VIOLATION,
            "constitutional_rights_violation: unlawful detention without probable cause",
            STAFF_FRAUDULENT_LEGAL_CLAIM,
            WOMAN_ASSAULT_DURING_CONTAINMENT,
            OFFICER_NON_FUNCTORIAL_ENFORCEMENT,
        ],
        strength=CardinalStrength.MAHLO,
        evidence_anchors=[EVIDENCE_ANCHOR_SHA256, EVIDENCE_ANCHOR_FULL_SHA256],
    )


# ---------------------------------------------------------------------------
# SAL adjunction check — expected to fail
# ---------------------------------------------------------------------------


def run_adjunction_check() -> AdjunctionProof:
    """
    Run the Type-3 adjunction check for D_DOLLARTREE.

    The schema's adjunction will hold at the structural level (the SAL kernel
    verifies schema shape), but the YeshuaClaim will carry the paradox
    in the domain_id so it is visible in the proof DAG.

    To expose the SEMANTIC failure we inject the counit violation into the
    schema's invariants and verify that a modified schema that encodes
    the contradiction fails the identity check.
    """
    # Schema that encodes the contradicted order as an invariant violation.
    contradicted_schema: Dict[str, Any] = {
        "id": "D_DOLLARTREE",
        "invariants": [
            # These two invariants are semantically contradictory; the counit
            # check will confirm: the generated state does NOT reproduce the
            # original domain identity because the "leave" and "block" invariants
            # produce different source_schema references.
            "officer_ordered_citizen_to_leave",
            "officer_physically_blocked_exit",
        ],
    }
    triple = AdjointTriple()
    return has_adjunction(contradicted_schema, triple)


# ---------------------------------------------------------------------------
# Full domain report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DollarTreeReport:
    """Complete forensic report for the D_DOLLARTREE incident."""

    adjunction_proof: AdjunctionProof
    topos_morphism: GeometricMorphism
    domain_state: DomainState
    forced_extensions: tuple
    evidence_anchor: str

    @property
    def adjunction_structurally_holds(self) -> bool:
        return self.adjunction_proof.is_valid

    @property
    def topos_truth_preserved(self) -> bool:
        return self.topos_morphism.truth_preserved

    @property
    def has_valid_forcing_extension(self) -> bool:
        return any(ext.is_valid for ext in self.forced_extensions)

    @property
    def is_defective(self) -> bool:
        """
        The incident is provably defective when:
          1. The domain state has violations, OR
          2. The geometric morphism between the two sites does not preserve truth.
        """
        return (
            bool(self.domain_state.violations)
            or not self.topos_truth_preserved
        )


def build_full_report() -> DollarTreeReport:
    """Build the complete forensic report for the D_DOLLARTREE incident."""
    proof = run_adjunction_check()
    morphism = evaluate_topos_truth_gap()
    state = build_domain_state()
    extensions = tuple(
        force_domain(
            state,
            lawful_replacements={
                DOLLARTREE_COUNIT_VIOLATION: (
                    "officer_allows_lawful_exit_without_detention"
                ),
                "constitutional_rights_violation: unlawful detention without probable cause": (
                    "officer_obtains_probable_cause_before_detention"
                ),
                STAFF_FRAUDULENT_LEGAL_CLAIM: (
                    "staff_correctly_states_filming_is_legal_in_public_commercial_spaces"
                ),
                WOMAN_ASSAULT_DURING_CONTAINMENT: (
                    "woman_does_not_commit_battery_and_does_not_block_exit"
                ),
                OFFICER_NON_FUNCTORIAL_ENFORCEMENT: (
                    "officer_individualizes_probable_cause_per_person_before_any_threat"
                ),
            },
        )
    )
    return DollarTreeReport(
        adjunction_proof=proof,
        topos_morphism=morphism,
        domain_state=state,
        forced_extensions=extensions,
        evidence_anchor=EVIDENCE_ANCHOR_SHA256,
    )
