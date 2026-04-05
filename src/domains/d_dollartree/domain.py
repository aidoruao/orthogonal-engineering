"""D_DOLLARTREE — forensic domain: unlawful detention / logical paradox of contradictory orders.

This domain encodes the logical paradox documented in the Dollar Tree incident:
a law-enforcement officer simultaneously ordered a citizen to leave the premises
AND physically blocked their exit.  These two commands are logically contradictory
and constitute a counit failure in the SAL L ⊣ M ⊣ R adjoint triple.

Incident evidence:
  YouTube short:   https://youtube.com/shorts/EWO8OpdsjHI?si=o-6_vtFUFxu_Rdl2
  Full video:      https://www.youtube.com/watch?v=3d4MlNCps6I
  Evidence anchor: SHA-256 of the short URL (per Yeshua Axiom 8)

Mathematical structure (Type 3+ Topos):
  * Officer's situs Ω_officer:  "lawful_detention=True"  (his local truth)
  * Video evidence situs Ω_video: "lawful_detention=False" (global truth)
  * The geometric morphism between these two sites does NOT preserve truth.
  * Counit ε: L∘M → Id fails because the generated state from the mediated
    schema does not reproduce the video-evidence situs.

Forcing (Type 5):
  * DomainState has adjunction_holds=False and records the logical paradox as
    a violation.
  * ForcingOperation produces a branch where the officer acts lawfully (does
    not block the exit) and the adjunction holds in that extension.
  * Existence of that branch proves the original state was defective.
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
    "EVIDENCE_ANCHOR_SHA256",
    "DOLLARTREE_SCHEMA",
    "build_officer_situs",
    "build_video_situs",
    "evaluate_topos_truth_gap",
    "build_domain_state",
    "run_adjunction_check",
    "DollarTreeReport",
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
    ],
    "evidence_anchors": [
        EVIDENCE_ANCHOR_SHA256,
        EVIDENCE_ANCHOR_FULL_SHA256,
    ],
    "paradox": (
        "Officer simultaneously issued 'leave the premises' AND 'do not leave' "
        "by physically blocking the exit — these commands are logically contradictory."
    ),
}

# The counit is expected to FAIL because the officer's generated state does not
# reproduce the invariant schema: the generated state contains a contradicted
# order, which breaks the identity condition checked by check_counit().
DOLLARTREE_COUNIT_VIOLATION: str = (
    "counit_violation: officer_action ⊕ exit_blocking is not identity-preserving; "
    "simultaneously ordering departure and blocking departure generates ⊥"
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


# ---------------------------------------------------------------------------
# Forcing domain state (Type 5)
# ---------------------------------------------------------------------------


def build_domain_state() -> DomainState:
    """
    Construct the DomainState for D_DOLLARTREE with adjunction_holds=False.

    The violations list encodes the logical paradox.
    """
    return DomainState(
        domain_id="D_DOLLARTREE",
        invariants=DOLLARTREE_SCHEMA["invariants"],
        adjunction_holds=False,
        violations=[
            DOLLARTREE_COUNIT_VIOLATION,
            "constitutional_rights_violation: unlawful detention without probable cause",
        ],
        strength=CardinalStrength.PREDICATIVE,
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
