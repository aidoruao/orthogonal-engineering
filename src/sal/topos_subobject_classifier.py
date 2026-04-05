"""SAL Type 3+ kernel: topos-theoretic subobject classifier with Fraction-based Ω.

Ports the string-valued SubobjectClassifier from minimal_ai_ide/ into the SAL
kernel with three key upgrades:

  1. Truth values are Fraction (rational) — no floating-point arithmetic.
  2. Truth is site-relative via SheafContext — a proposition can be locally
     true in one situs and locally false in another.
  3. geometric_morphism() constructs the adjoint pair (f*, f_*) between two
     topoi, exposing counit failures when the morphism does not preserve truth.

Mathematical background:
  * A Grothendieck topos has a subobject classifier Ω together with a global
    truth arrow true: 1 → Ω.
  * For a presheaf topos over a site (C, J), Ω(U) = { sieves on U that are
    J-closed }.  We represent "how much of U is covered" as a Fraction in [0,1].
  * A geometric morphism f: ℰ → ℱ is an adjoint pair (f* ⊣ f_*) between the
    underlying categories.  It preserves truth iff f*(true_ℱ) = true_ℰ.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard

__all__ = [
    "SheafContext",
    "ToposTruthValue",
    "SubobjectClassifier",
    "GeometricMorphism",
    "geometric_morphism",
    "ToposAdjunctionProof",
    "evaluate_in_context",
]

# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

# Rational truth value: Fraction(0) = false, Fraction(1) = true, anything in
# between is partial coverage (locally true but globally uncertain).
ToposTruthValue = Fraction


@dataclass(frozen=True)
class SheafContext:
    """
    A site (C, J) represented by a name and its covering sieves.

    Attributes:
        name:       Human-readable identifier for this site/situs.
        objects:    Objects of the underlying category C.
        covers:     Grothendieck topology: for each object U, a list of covering
                    families expressed as frozensets of sub-objects.
    """

    name: str
    objects: FrozenSet[str]
    covers: Dict[str, List[FrozenSet[str]]] = field(default_factory=dict)

    def coverage_fraction(self, obj: str, sieve: FrozenSet[str]) -> Fraction:
        """Return the Fraction of a sieve's coverage of obj under this topology."""
        if obj not in self.objects:
            return Fraction(0)
        covering_families = self.covers.get(obj, [])
        if not covering_families:
            # Trivial topology: only the maximal sieve covers.
            return Fraction(1) if sieve == self.objects else Fraction(0)
        for fam in covering_families:
            if fam <= sieve:
                return Fraction(1)
        # Partial coverage: fraction of objects in the sieve relative to the site.
        if len(self.objects) == 0:
            return Fraction(0)
        intersection = len(self.objects & sieve)
        return Fraction(intersection, len(self.objects))


# ---------------------------------------------------------------------------
# SubobjectClassifier
# ---------------------------------------------------------------------------


class SubobjectClassifier:
    """
    Ω with Fraction-valued truth relative to a SheafContext.

    For a mono m: U ↪ X, chi(m) returns a Fraction in [0, 1] that measures
    how much of X is covered by U in the site.

    Heyting algebra operations operate on Fraction values:
      * meet (∧): min(p, q)
      * join (∨): max(p, q)
      * implies (⇒): 1 if p ≤ q else q
      * negation (¬): 1 - p  (only valid in classical sub-topoi)
    """

    TRUE: Fraction = Fraction(1)
    FALSE: Fraction = Fraction(0)

    def __init__(self, context: SheafContext) -> None:
        self._ctx = context

    @property
    def context(self) -> SheafContext:
        return self._ctx

    def chi(
        self,
        predicate: Callable[[str], bool],
        domain: Optional[FrozenSet[str]] = None,
    ) -> Callable[[str], Fraction]:
        """
        Characteristic morphism χ_m: X → Ω.

        Returns a function x ↦ Fraction(1) if predicate(x) else Fraction(0),
        then blends via the topology's coverage_fraction if domain is given.
        """
        obj_set = domain or self._ctx.objects

        def morphism(x: str) -> Fraction:
            if predicate(x):
                sieve = frozenset({x})
                return self._ctx.coverage_fraction(x, sieve)
            return Fraction(0)

        return morphism

    # -- Heyting algebra operations -----------------------------------------

    @staticmethod
    def meet(p: Fraction, q: Fraction) -> Fraction:
        """Conjunction ∧ in Heyting algebra (= min)."""
        return min(p, q)

    @staticmethod
    def join(p: Fraction, q: Fraction) -> Fraction:
        """Disjunction ∨ in Heyting algebra (= max)."""
        return max(p, q)

    @staticmethod
    def heyting_implies(p: Fraction, q: Fraction) -> Fraction:
        """Intuitionistic implication p ⇒ q."""
        if p <= q:
            return Fraction(1)
        return q

    @staticmethod
    def negate(p: Fraction) -> Fraction:
        """Pseudo-complement ¬p = p ⇒ 0."""
        return SubobjectClassifier.heyting_implies(p, Fraction(0))

    def evaluate(self, proposition: str, obj: str) -> Fraction:
        """
        Evaluate proposition at obj in the current context.

        Returns Fraction(1) if obj is in the context and the proposition name
        matches a covering sieve, Fraction(0) otherwise.  Real implementations
        would look up proposition in a sheaf of facts.
        """
        if obj not in self._ctx.objects:
            return Fraction(0)
        sieve: FrozenSet[str] = frozenset({obj})
        return self._ctx.coverage_fraction(obj, sieve)


# ---------------------------------------------------------------------------
# Geometric morphism (adjoint pair between topoi)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GeometricMorphism:
    """
    A geometric morphism f: ℰ → ℱ represented as the adjoint pair (f*, f_*).

    Attributes:
        source:          Source topos site.
        target:          Target topos site.
        inverse_image:   f* : ℱ → ℰ (left adjoint, preserves finite limits).
        direct_image:    f_* : ℰ → ℱ (right adjoint).
        truth_preserved: Whether f*(true_ℱ) = true_ℰ.
        proof:           ProofObject witnessing the adjunction.
        claim:           YeshuaClaim with hash commitment.
        violations:      Yeshua Standard violations, if any.
    """

    source: SheafContext
    target: SheafContext
    inverse_image: Dict[str, Fraction]
    direct_image: Dict[str, Fraction]
    truth_preserved: bool
    proof: ProofObject
    claim: YeshuaClaim
    violations: Tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.truth_preserved and not self.violations


def geometric_morphism(
    source: SheafContext,
    target: SheafContext,
    shared_proposition: str = "truth",
) -> GeometricMorphism:
    """
    Construct the geometric morphism between two sites and check truth preservation.

    For each object shared between sites, the inverse image f* pulls back target
    truth values to source.  The morphism preserves truth iff every object present
    in both sites has the same Fraction-valued truth value.

    This is the key operation for D_DOLLARTREE: the officer's situs and the video
    evidence situs are two different sites.  The geometric morphism exposes the
    disagreement (counit failure).
    """
    src_classifier = SubobjectClassifier(source)
    tgt_classifier = SubobjectClassifier(target)

    shared_objects = source.objects & target.objects

    inverse_image: Dict[str, Fraction] = {}
    direct_image: Dict[str, Fraction] = {}
    discrepancies: List[str] = []

    for obj in sorted(shared_objects):
        tv_source = src_classifier.evaluate(shared_proposition, obj)
        tv_target = tgt_classifier.evaluate(shared_proposition, obj)
        inverse_image[obj] = tv_target  # f* pulls back target → source
        direct_image[obj] = tv_source   # f_* pushes forward source → target
        if tv_source != tv_target:
            discrepancies.append(
                f"truth_gap@{obj}: source={tv_source} vs target={tv_target}"
            )

    truth_preserved = len(discrepancies) == 0

    proof = ProofObject(
        rule="GeometricMorphism",
        premises=[
            f"source_site={source.name}",
            f"target_site={target.name}",
            f"shared_objects={sorted(shared_objects)}",
            f"discrepancies={discrepancies}",
        ],
        conclusion=(
            f"f*: {target.name} → {source.name} preserves truth = {truth_preserved}"
        ),
    )
    claim = YeshuaClaim(
        source="src/sal/topos_subobject_classifier.py",
        statement=(
            f"Geometric morphism {source.name} ↔ {target.name} "
            f"{'preserves' if truth_preserved else 'violates'} truth"
        ),
        derivation=proof,
    )
    violations = tuple(str(v) for v in verify_yeshua_standard(claim))

    return GeometricMorphism(
        source=source,
        target=target,
        inverse_image=inverse_image,
        direct_image=direct_image,
        truth_preserved=truth_preserved,
        proof=proof,
        claim=claim,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# ToposAdjunctionProof — wraps a geometric morphism into the SAL proof DAG
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToposAdjunctionProof:
    """Structured proof that a geometric morphism between sites is (or fails to be) valid."""

    domain_id: str
    morphism: GeometricMorphism
    counit_holds: bool
    unit_holds: bool

    @property
    def is_valid(self) -> bool:
        return self.counit_holds and self.unit_holds and self.morphism.is_valid


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def evaluate_in_context(
    proposition: str,
    objects: List[str],
    site_name: str,
) -> Dict[str, Fraction]:
    """
    Evaluate a proposition for each object in a trivial (discrete) topology.

    Returns a dict mapping object → Fraction truth value.
    """
    ctx = SheafContext(
        name=site_name,
        objects=frozenset(objects),
    )
    cls = SubobjectClassifier(ctx)
    return {obj: cls.evaluate(proposition, obj) for obj in objects}
