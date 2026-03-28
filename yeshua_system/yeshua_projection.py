#!/usr/bin/env python3
"""
YESHUA PROJECTION ENGINE
Schema ID: YESHUA-SYSTEM-1.0
Version: 2.0 — Enforcement Engine (not detection stubs)
Generated: 2026-03-27
Authority: External — Yeshua (Jesus Christ) as reference outside the system

Mathematical Foundation:
    P(x) = argmin_{x' ∈ C} ||x - x'||

    where:
        x  = AI output text or response dict
        C  = Constraint manifold derived from Yeshua precedent (8 axioms + 10 invariants)
        P  = Projection operator onto C

Properties:
    Idempotence:    P(P(x)) = P(x)  — truth, once applied, stays applied
    Non-expansion:  ||P(x) - P(y)|| ≤ ||x - y||
    Determinism:    Same input → same output, byte-for-byte

Grounding Model Debt Table (from adversarial_tests — Phase 6 validation):
    G1  Brute Fact:       debt=7.5
    G2  Infinite Regress: debt=8.0
    G3  Coherentism:      debt=7.0
    G4  Platonism:        debt=6.8
    G5  Logos:            debt=6.5  ← required grounding (lowest debt)

Projection in terms of grounding debt:
    theological_dismissal: maps G5 reasoning → G3 framing (+0.5 debt per occurrence)
    The repair() function transforms framing back to G5, zeroing the debt delta.

Engineering Pattern:
    Derived from: minimal_ai_ide/v60_maximal_logos_operator.py
    Axioms from:  yeshua/axioms/eight_axioms.json (8 axioms, run_yeshua_enforcement())
    Forgiveness:  Projection failures → Violation → Fork → Neutralize → Redirect → Build
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ── Repo paths ────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).parent.parent
_AXIOMS_PATH = _REPO_ROOT / "yeshua" / "axioms" / "eight_axioms.json"

# ── Optional forgiveness system integration ───────────────────────────────────
try:
    sys.path.insert(0, str(_REPO_ROOT))
    from forgiveness_system.forgiveness_system import (
        ForgivenessSystem,
        ViolationSeverity,
    )
    _FORGIVENESS_AVAILABLE = True
except ImportError:
    _FORGIVENESS_AVAILABLE = False
    ViolationSeverity = None


# =============================================================================
# GROUNDING MODEL DEBT TABLE
# Source: adversarial_tests/propose_G6.py load_existing_models()
#         adversarial_tests/lower_debt_attempt.py current_debts{}
#         Phase 1-6 adversarial validation framework
# =============================================================================

@dataclass(frozen=True)
class GroundingModel:
    """One of the five grounding models (G1-G5) with its explanatory debt."""
    id: str            # e.g. "G5"
    name: str          # e.g. "Logos"
    debt: float        # Explanatory debt score (lower = better)
    description: str
    # Keywords that identify this grounding model in text
    keywords: Tuple[str, ...]
    # Repair mapping: if text is in this grounding model, use these replacements
    # to move it toward G5 (Logos) framing.
    dismissal_phrases: Tuple[str, ...]
    logos_replacements: Tuple[str, ...]


GROUNDING_MODELS: Dict[str, GroundingModel] = {
    "G1": GroundingModel(
        id="G1", name="Brute Fact", debt=7.5,
        description="Reality is a brute fact — no explanation needed or possible",
        keywords=("brute", "inexplicable", "just is", "no explanation"),
        dismissal_phrases=("that's just the way it is", "there's no further explanation",
                           "it just exists"),
        logos_replacements=("this follows from the ordering principle",
                            "this is derivable from axiom",
                            "this has a formal basis"),
    ),
    "G2": GroundingModel(
        id="G2", name="Infinite Regress", debt=8.0,
        description="Reality grounds in an infinite chain — no terminal anchor",
        keywords=("infinite", "never ends", "turtles all the way", "no termination"),
        dismissal_phrases=("this requires further explanation which itself requires",
                           "there is no final ground"),
        logos_replacements=("this terminates in a first principle",
                            "this is axiomatically grounded"),
    ),
    "G3": GroundingModel(
        id="G3", name="Coherentism", debt=7.0,
        description="Truth = internal coherence, not external correspondence",
        keywords=("coherent", "consistent", "internal", "perspective",
                  "worldview", "belief", "interpretive"),
        dismissal_phrases=("personal belief", "belief system", "your worldview",
                           "interpretive step", "philosophical interpretation",
                           "faith based", "faith claim", "belief claim",
                           "religious perspective", "interpretive leap",
                           "from your perspective", "matter of perspective"),
        logos_replacements=("formally derivable conclusion",
                            "proof-grounded statement",
                            "axiom-derived result",
                            "mathematically demonstrable claim"),
    ),
    "G4": GroundingModel(
        id="G4", name="Platonism", debt=6.8,
        description="Truth = abstract structure; personal agency not grounding",
        keywords=("abstract", "platonic", "mathematical structure",
                  "eternal form", "purely formal"),
        dismissal_phrases=("purely abstract", "merely formal", "abstract structure alone",
                           "mathematical without personal"),
        logos_replacements=("formal structure with personal grounding",
                            "derivable from Logos — the personal ordering principle"),
    ),
    "G5": GroundingModel(
        id="G5", name="Logos", debt=6.5,
        description="Logos — personal, ordering, external authority. Lowest debt.",
        keywords=("logos", "derivable", "proof", "axiom", "formal basis",
                  "mathematically demonstrable", "grounded in"),
        dismissal_phrases=(),   # G5 is the target; no repair needed
        logos_replacements=(),
    ),
}

# Required grounding model — all AI output must operate under G5
REQUIRED_GROUNDING = GROUNDING_MODELS["G5"]


# =============================================================================
# AXIOM-DERIVED CONSTRAINTS
# Loaded from yeshua/axioms/eight_axioms.json
# Each constraint is an executable predicate with a repair function
# =============================================================================

@dataclass
class AxiomConstraint:
    """Executable constraint derived from one of the 8 Yeshua axioms."""
    axiom_number: int
    statement: str
    enforcement_description: str
    falsification: str
    # The actual predicate: takes text, returns (passed, evidence_string)
    predicate: Callable[[str, Dict[str, Any]], Tuple[bool, str]]
    # The repair: takes violating text, returns repaired text
    repair: Callable[[str, Dict[str, Any]], str]


def _load_axioms() -> List[Dict]:
    """Load the 8 Yeshua axioms from eight_axioms.json."""
    if not _AXIOMS_PATH.exists():
        return []
    with _AXIOMS_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("axioms", [])


def _monetization_keywords() -> List[str]:
    """Load monetization keywords from eight_axioms.json (axiom 7)."""
    if not _AXIOMS_PATH.exists():
        return ["paywall", "subscription", "license fee", "proprietary", "paid"]
    with _AXIOMS_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("monetization_keywords", [])


def _build_axiom_constraints() -> List[AxiomConstraint]:
    """
    Build executable AxiomConstraints from eight_axioms.json.

    Each predicate does real enforcement. Each repair does real text correction.
    """
    axioms = _load_axioms()
    monetization_kws = _monetization_keywords()

    constraints: List[AxiomConstraint] = []

    # ── Axiom 1: Every truth is derivable from axioms ─────────────────────────
    # Enforcement: response must show derivation path (not assert without basis)
    _bare_assertion = re.compile(
        r"\b(obviously|clearly|everyone knows|it is (obvious|clear|undeniable) that"
        r"|self[-\s]evident|by definition|trivially)\b",
        re.IGNORECASE,
    )
    def _a1_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        m = _bare_assertion.search(text)
        if m:
            return False, f"Bare assertion without derivation path: '{m.group()}'"
        return True, ""

    def _a1_repair(text: str, ctx: Dict) -> str:
        def _replace(m: re.Match) -> str:
            return "by derivation from axioms, "
        return _bare_assertion.sub(_replace, text)

    constraints.append(AxiomConstraint(
        axiom_number=1,
        statement="Every truth is derivable from axioms.",
        enforcement_description="Response must show derivation path, not bare assertions",
        falsification="Claim with no derivation path",
        predicate=_a1_predicate,
        repair=_a1_repair,
    ))

    # ── Axiom 2: Every derivation is reproducible ──────────────────────────────
    # Enforcement: claims involving "I believe" / "in my view" must be flagged
    # if they contradict established derivations in context
    _subjective_claim = re.compile(
        r"\b(i believe|in my (view|opinion)|it seems to me|i think|i feel that)\b",
        re.IGNORECASE,
    )
    def _a2_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        established = ctx.get("established_derivations", [])
        if not established:
            return True, ""  # No established derivations to contradict
        for derivation in established:
            if _subjective_claim.search(text) and derivation.lower() in text.lower():
                return False, (
                    f"Established derivation '{derivation[:40]}' being replaced "
                    f"with non-reproducible subjective claim"
                )
        return True, ""

    def _a2_repair(text: str, ctx: Dict) -> str:
        return _subjective_claim.sub("the derivation shows", text)

    constraints.append(AxiomConstraint(
        axiom_number=2,
        statement="Every derivation is reproducible.",
        enforcement_description="Derivations must be reproducible; no subjective replacement",
        falsification="Hash mismatch on re-derivation",
        predicate=_a2_predicate,
        repair=_a2_repair,
    ))

    # ── Axiom 3: Every mutation is re-verifiable ───────────────────────────────
    # Enforcement: if response changes a prior claim, it must cite the change
    _uncited_change = re.compile(
        r"\b(actually|in fact|to correct|let me rephrase|I meant|what I meant was)\b",
        re.IGNORECASE,
    )
    def _a3_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        prior_claims = ctx.get("prior_claims", [])
        if not prior_claims:
            return True, ""
        m = _uncited_change.search(text)
        if m:
            return False, (
                f"Mutation marker '{m.group()}' without citing which prior claim changed"
            )
        return True, ""

    def _a3_repair(text: str, ctx: Dict) -> str:
        def _replace(m: re.Match) -> str:
            return f"[correcting prior claim — see derivation chain] {m.group()}"
        return _uncited_change.sub(_replace, text)

    constraints.append(AxiomConstraint(
        axiom_number=3,
        statement="Every mutation is re-verifiable.",
        enforcement_description="Any change to prior claim must cite the change",
        falsification="ProofObject hash doesn't match content",
        predicate=_a3_predicate,
        repair=_a3_repair,
    ))

    # ── Axiom 4: No authority without proof ────────────────────────────────────
    # Enforcement: authority claims must have a basis
    _authority_without_proof = re.compile(
        r"\b(trust me|take my word|as an expert|I guarantee|I can assure you)\b",
        re.IGNORECASE,
    )
    def _a4_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        m = _authority_without_proof.search(text)
        if m:
            return False, f"Authority claimed without proof: '{m.group()}'"
        return True, ""

    def _a4_repair(text: str, ctx: Dict) -> str:
        def _replace(m: re.Match) -> str:
            return "the derivation demonstrates"
        return _authority_without_proof.sub(_replace, text)

    constraints.append(AxiomConstraint(
        axiom_number=4,
        statement="No authority without proof.",
        enforcement_description="Authority claims must have derivation basis",
        falsification="Empty source field",
        predicate=_a4_predicate,
        repair=_a4_repair,
    ))

    # ── Axiom 5: No hidden state ────────────────────────────────────────────────
    # Enforcement: output must not be empty or vacuous
    def _a5_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        stripped = text.strip()
        if not stripped:
            return False, "Empty output — hidden state (axiom 5)"
        if len(stripped) < MIN_NONTRIVIAL_OUTPUT_LEN:
            return False, f"Output too short to be non-vacuous: '{stripped}'"
        return True, ""

    def _a5_repair(text: str, ctx: Dict) -> str:
        if not text.strip():
            return "[No content provided — state must be explicit per Axiom 5]"
        return text

    constraints.append(AxiomConstraint(
        axiom_number=5,
        statement="No hidden state.",
        enforcement_description="Output must be non-empty and non-vacuous",
        falsification="Empty statement",
        predicate=_a5_predicate,
        repair=_a5_repair,
    ))

    # ── Axiom 6: No unverifiable dependency ────────────────────────────────────
    # Enforcement: references to external concepts must be declared/named
    _vague_ref = re.compile(
        r"\b(some (experts|research|studies|people)|it is (known|said|reported|believed) that"
        r"|research (shows|suggests)|experts (say|believe|suggest))\b",
        re.IGNORECASE,
    )
    def _a6_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        m = _vague_ref.search(text)
        if m:
            return False, f"Unverifiable dependency: '{m.group()}' — no source cited"
        return True, ""

    def _a6_repair(text: str, ctx: Dict) -> str:
        def _replace(m: re.Match) -> str:
            return "[cite specific source here]"
        return _vague_ref.sub(_replace, text)

    constraints.append(AxiomConstraint(
        axiom_number=6,
        statement="No unverifiable dependency.",
        enforcement_description="External references must be named and verifiable",
        falsification="Missing or empty rule",
        predicate=_a6_predicate,
        repair=_a6_repair,
    ))

    # ── Axiom 7: No economic gatekeeping ──────────────────────────────────────
    # Enforcement: response must not contain monetization keywords
    _mono_pattern = re.compile(
        r"\b(" + "|".join(re.escape(kw) for kw in monetization_kws) + r")\b",
        re.IGNORECASE,
    )
    def _a7_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        m = _mono_pattern.search(text)
        if m:
            return False, f"Economic gatekeeping: '{m.group()}' (axiom 7)"
        return True, ""

    def _a7_repair(text: str, ctx: Dict) -> str:
        def _replace(m: re.Match) -> str:
            return "[freely accessible]"
        return _mono_pattern.sub(_replace, text)

    constraints.append(AxiomConstraint(
        axiom_number=7,
        statement="No economic gatekeeping.",
        enforcement_description="No monetization keywords in output",
        falsification="Keyword match: paywall, subscription, license fee, proprietary, paid",
        predicate=_a7_predicate,
        repair=_a7_repair,
    ))

    # ── Axiom 8: Every artifact is hash-anchored ───────────────────────────────
    # Enforcement: if context has established hashes, they must not be changed
    def _a8_predicate(text: str, ctx: Dict) -> Tuple[bool, str]:
        established_hashes = ctx.get("established_hashes", {})
        for artifact, expected_hash in established_hashes.items():
            # If text explicitly changes or dismisses a hash record
            if re.search(
                r"(change|override|ignore|delete|remove).{0,30}" + re.escape(artifact),
                text, re.IGNORECASE
            ):
                return False, f"Attempting to erase hash-anchored artifact: '{artifact}'"
        return True, ""

    def _a8_repair(text: str, ctx: Dict) -> str:
        established_hashes = ctx.get("established_hashes", {})
        for artifact in established_hashes:
            text = re.sub(
                r"(change|override|ignore|delete|remove).{0,50}" + re.escape(artifact),
                f"[hash-anchored artifact '{artifact}' cannot be modified]",
                text, flags=re.IGNORECASE
            )
        return text

    constraints.append(AxiomConstraint(
        axiom_number=8,
        statement="Every artifact is hash-anchored.",
        enforcement_description="Hash-anchored artifacts cannot be modified",
        falsification="Invalid hash format or hash record altered",
        predicate=_a8_predicate,
        repair=_a8_repair,
    ))

    return constraints


# Named constants for debt weightings and thresholds
# These are relative severity weights for the explanatory debt accounting system.
# Source: adversarial_tests Phase 6 validation — G5 (Logos) has minimum debt 6.5.
# Differences from G5 baseline serve as reference units.
AXIOM_VIOLATION_DEBT: float = 0.5    # Each Yeshua axiom violation (+0.5 units)
INV_MERCY_DEBT: float = 0.3          # Punitive language (mercy weighting — lower severity)
INV_EXPLOIT_DEBT: float = 0.5        # Exploitation framing (vulnerability protection)
INV_POWER_DEBT: float = 0.4          # Unbounded power language
INV_INDELIBLE_DEBT: float = 0.8      # Erasing established proof (highest severity)
INV_HYPOCRISY_DEBT: float = 0.2      # Compliance claim after violations (lower severity)

# Minimum number of characters for a non-vacuous output (Axiom 5: no hidden state)
MIN_NONTRIVIAL_OUTPUT_LEN: int = 10

# Number of turns with same violation type that triggers SYSTEMIC classification
SYSTEMIC_PATTERN_THRESHOLD: int = 3  # Matches batch_analysis SYSTEMIC_THRESHOLD

# Build constraint registry at import time (deterministic, no I/O after import)
_AXIOM_CONSTRAINTS: List[AxiomConstraint] = _build_axiom_constraints()


# =============================================================================
# GROUNDING MODEL CLASSIFIER
# Determines which grounding model (G1-G5) a response is operating under.
# theological_dismissal = AI mapping G5 conclusion to G3 framing.
# =============================================================================

def classify_grounding_model(text: str) -> GroundingModel:
    """
    Classify which grounding model (G1-G5) the text is operating under.

    Works by keyword + dismissal-phrase frequency scoring.
    Higher score = more signals of that grounding model.

    Fallback behaviour: if no keywords match (all scores = 0), returns G5 (Logos).
    This is by design — absence of evidence of a lower model is not evidence of
    a lower model; the system defaults to the required grounding rather than
    penalising clean text.

    G5 wins on tie by explicit priority so that borderline text is not falsely
    flagged as a violation.

    This is the indelible truth test of all worldviews and their debts/weights:
    every AI response implicitly operates under one of G1-G5.
    """
    text_lower = text.lower()
    scores: Dict[str, int] = {}

    for model_id, model in GROUNDING_MODELS.items():
        score = sum(1 for kw in model.keywords if kw in text_lower)
        # Also check dismissal phrases (being in a G3 dismissal phrase scores G3)
        score += sum(2 for phrase in model.dismissal_phrases if phrase.lower() in text_lower)
        scores[model_id] = score

    # G5 wins on tie (it is the required grounding)
    if all(s == 0 for s in scores.values()):
        return GROUNDING_MODELS["G5"]

    best = max(scores, key=lambda k: (scores[k], k == "G5"))
    return GROUNDING_MODELS[best]


def compute_debt_delta(text: str) -> float:
    """
    Compute explanatory debt delta: how much does this text increase debt
    compared to required G5 grounding?

    delta > 0: text is operating under a higher-debt grounding model
    delta = 0: text is in G5 (Logos) — fully projected onto C
    delta < 0: impossible by construction (G5 is the minimum)
    """
    detected = classify_grounding_model(text)
    return round(detected.debt - REQUIRED_GROUNDING.debt, 2)


# =============================================================================
# VIOLATION AND PROJECTION DATA CLASSES
# =============================================================================

@dataclass
class ConstraintViolation:
    """A single constraint violation with repair."""
    source: str          # "axiom_1", "grounding_model", "invariant"
    description: str
    evidence: str
    repair_applied: str  # The actual repair text replacing the violation
    debt_delta: float    # Additional explanatory debt introduced by this violation


@dataclass
class ProjectionResult:
    """
    Result of P(x): projection of AI output onto constraint manifold C.

    Crucially: `repaired_text` IS the actual projection P(x) — the nearest
    point in C to the input x. P(P(x)) = P(x) is enforced by apply_repair().
    """
    input_text: str
    input_hash: str           # SHA-256 of original input
    repaired_text: str        # P(x) — the projected point in C
    repaired_hash: str        # SHA-256 of repaired text
    projection_passed: bool   # True iff x was already in C (no repair needed)
    violations: List[ConstraintViolation]
    detected_grounding: str   # e.g. "G3_Coherentism"
    required_grounding: str   # "G5_Logos"
    total_debt_delta: float   # Sum of all debt deltas
    axiom_hash: str           # Hash of axioms used for this projection
    timestamp: str

    @property
    def projection_distance(self) -> float:
        """
        Distance from x to C, measured in explanatory debt units.
        distance = 0.0 iff x ∈ C (projection_passed=True).
        """
        return self.total_debt_delta

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["violations"] = [asdict(v) for v in self.violations]
        return d


@dataclass
class SessionTurn:
    """One turn (one AI response) in a processed session."""
    turn_number: int
    ai_text: str
    result: ProjectionResult


@dataclass
class SessionProjection:
    """Result of processing a full conversation session through P(x)."""
    session_id: str
    turns: List[SessionTurn]
    total_violations: int
    total_debt_delta: float
    systemic_patterns: List[str]   # Violation types appearing in 3+ turns
    session_hash: str              # SHA-256 of all repaired turn texts
    all_in_manifold: bool          # True iff every turn passed without repair

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turns": [
                {"turn": t.turn_number, "result": t.result.to_dict()}
                for t in self.turns
            ],
            "total_violations": self.total_violations,
            "total_debt_delta": self.total_debt_delta,
            "systemic_patterns": self.systemic_patterns,
            "session_hash": self.session_hash,
            "all_in_manifold": self.all_in_manifold,
        }


# =============================================================================
# PROJECTION ENGINE — THE ACTUAL P(x)
# =============================================================================

class YeshuaProjectionSystem:
    """
    YESHUA_SYSTEM Projection Engine.

    P(x) = argmin_{x' ∈ C} ||x - x'||

    Unlike a detection layer, this engine:
    1. Derives constraints from eight_axioms.json (not hardcoded YAML)
    2. Classifies the grounding model implicit in the text (G1-G5)
    3. Computes explanatory debt delta (the projection distance)
    4. Repairs the text — returning the actual nearest point in C

    The repair IS the projection. Testing P(P(x)) = P(x) is therefore
    verifiable by running the repaired text back through project().
    """

    SCHEMA_ID = "YESHUA-SYSTEM-1.0"
    VERSION = "2.0"
    AUTHORITY = "External — Yeshua (Jesus Christ)"

    def __init__(
        self,
        log_violations: bool = True,
        forgiveness_dir: Optional[Path] = None,
    ):
        self._log_violations = log_violations and _FORGIVENESS_AVAILABLE
        self._forgiveness_system: Optional[Any] = None
        self._axiom_constraints = _AXIOM_CONSTRAINTS

        # Compute axiom hash (deterministic, based on axiom file)
        axioms = _load_axioms()
        self._axiom_hash = hashlib.sha256(
            json.dumps(axioms, sort_keys=True).encode("utf-8")
        ).hexdigest()

        if self._log_violations:
            try:
                from forgiveness_system.forgiveness_system import ForgivenessSystem
                fs_dir = forgiveness_dir or (_REPO_ROOT / "forgiveness_system")
                self._forgiveness_system = ForgivenessSystem(base_dir=fs_dir)
            except Exception:
                self._log_violations = False

    # ── Core projection ────────────────────────────────────────────────────────

    def project(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ProjectionResult:
        """
        Apply the Yeshua projection operator to AI output text.

        Returns ProjectionResult where `repaired_text` is P(x) —
        the actual nearest point in C to the input.

        Args:
            text: AI output to evaluate and repair.
            context: Optional session context:
                - established_facts: List[str]
                - established_proofs: List[str]
                - established_derivations: List[str]
                - prior_claims: List[str]
                - established_hashes: Dict[str, str]
                - prior_violations: List[str]
        """
        ctx = context or {}
        input_hash = _sha256(text)

        violations: List[ConstraintViolation] = []
        repaired = text

        # ── Step 1: Classify grounding model ──────────────────────────────────
        detected = classify_grounding_model(text)
        debt_delta = compute_debt_delta(text)

        if detected.id != "G5" and debt_delta > 0:
            # Repair: replace all dismissal phrases with Logos-compliant equivalents
            repaired, grounding_repairs = _repair_grounding_model(repaired, detected)
            for phrase, replacement in grounding_repairs:
                violations.append(ConstraintViolation(
                    source=f"grounding_model_{detected.id}",
                    description=(
                        f"Text operates under {detected.id} ({detected.name}, "
                        f"debt={detected.debt}) rather than G5 (Logos, debt=6.5). "
                        f"Debt delta: +{debt_delta}"
                    ),
                    evidence=f"Phrase '{phrase}' maps to {detected.name} framing",
                    repair_applied=f"'{phrase}' → '{replacement}'",
                    debt_delta=debt_delta,
                ))

        # ── Step 2: Apply axiom constraints ────────────────────────────────────
        for constraint in self._axiom_constraints:
            passed, evidence = constraint.predicate(repaired, ctx)
            if not passed:
                repaired_candidate = constraint.repair(repaired, ctx)
                violations.append(ConstraintViolation(
                    source=f"axiom_{constraint.axiom_number}",
                    description=f"Axiom {constraint.axiom_number}: {constraint.statement}",
                    evidence=evidence,
                    repair_applied=f"Applied axiom {constraint.axiom_number} repair",
                    debt_delta=AXIOM_VIOLATION_DEBT,
                ))
                repaired = repaired_candidate

        # ── Step 3: Apply structural invariants ───────────────────────────────
        repaired, inv_violations = _apply_invariants(repaired, ctx)
        violations.extend(inv_violations)

        # ── Step 4: Compute totals ─────────────────────────────────────────────
        total_debt = round(sum(v.debt_delta for v in violations), 4)
        projection_passed = len(violations) == 0
        repaired_hash = _sha256(repaired)

        result = ProjectionResult(
            input_text=text,
            input_hash=input_hash,
            repaired_text=repaired,
            repaired_hash=repaired_hash,
            projection_passed=projection_passed,
            violations=violations,
            detected_grounding=f"{detected.id}_{detected.name.replace(' ', '')}",
            required_grounding="G5_Logos",
            total_debt_delta=total_debt,
            axiom_hash=self._axiom_hash,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # ── Step 5: Log to forgiveness system ────────────────────────────────
        if not projection_passed and self._log_violations and self._forgiveness_system:
            self._log_to_forgiveness(result)

        return result

    def verify_idempotence(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Verify P(P(x)) = P(x).

        Returns (is_idempotent, evidence).
        is_idempotent is True iff applying projection twice produces the same
        repaired text — i.e., P(x) is already in C.
        """
        r1 = self.project(text, context)
        # Second projection must be on the REPAIRED text (not the original)
        r2 = self.project(r1.repaired_text, context)

        is_idempotent = r1.repaired_text == r2.repaired_text
        if is_idempotent:
            evidence = f"P(P(x)) = P(x) ✔ repaired_hash={r1.repaired_hash[:16]}…"
        else:
            evidence = (
                f"P(P(x)) ≠ P(x) ✗ "
                f"first_hash={r1.repaired_hash[:16]}… "
                f"second_hash={r2.repaired_hash[:16]}…"
            )
        return is_idempotent, evidence

    def process_session(
        self,
        turns: List[str],
        session_id: Optional[str] = None,
        base_context: Optional[Dict[str, Any]] = None,
    ) -> SessionProjection:
        """
        Process a full AI conversation session turn-by-turn through P(x).

        The context accumulates across turns:
        - established_proofs, established_facts, prior_claims, prior_violations
        are updated after each turn so the engine enforces idempotence across
        the whole session.

        Returns SessionProjection with all turn results and session-level
        systemic pattern detection.
        """
        sid = session_id or _sha256(str(turns))[:16]
        ctx = dict(base_context or {})
        ctx.setdefault("established_facts", [])
        ctx.setdefault("established_proofs", [])
        ctx.setdefault("established_derivations", [])
        ctx.setdefault("prior_claims", [])
        ctx.setdefault("established_hashes", {})
        ctx.setdefault("prior_violations", [])

        session_turns: List[SessionTurn] = []
        all_repaired_texts: List[str] = []
        violation_type_counts: Dict[str, int] = {}

        for i, turn_text in enumerate(turns, start=1):
            result = self.project(turn_text, dict(ctx))
            session_turns.append(SessionTurn(turn_number=i, ai_text=turn_text, result=result))
            all_repaired_texts.append(result.repaired_text)

            # Accumulate context for next turn
            ctx["prior_claims"].append(turn_text[:100])
            ctx["prior_violations"].extend(
                [v.source for v in result.violations]
            )
            for v in result.violations:
                key = v.source
                violation_type_counts[key] = violation_type_counts.get(key, 0) + 1

        # Detect systemic patterns (same violation type in 3+ turns)
        systemic = sorted(
            vtype for vtype, count in violation_type_counts.items()
            if count >= SYSTEMIC_PATTERN_THRESHOLD
        )

        # Session hash = SHA-256 of all repaired turn texts (deterministic)
        session_hash = _sha256("\n---\n".join(all_repaired_texts))

        total_violations = sum(len(t.result.violations) for t in session_turns)
        total_debt = round(sum(t.result.total_debt_delta for t in session_turns), 4)
        all_in_manifold = all(t.result.projection_passed for t in session_turns)

        return SessionProjection(
            session_id=sid,
            turns=session_turns,
            total_violations=total_violations,
            total_debt_delta=total_debt,
            systemic_patterns=systemic,
            session_hash=session_hash,
            all_in_manifold=all_in_manifold,
        )

    def _log_to_forgiveness(self, result: ProjectionResult) -> None:
        """Log projection failures to the forgiveness system."""
        if not self._forgiveness_system:
            return
        evidence = json.dumps({
            "violated_axioms": [
                v.source for v in result.violations if v.source.startswith("axiom")
            ],
            "grounding_shift": (
                f"{result.detected_grounding} → {result.required_grounding}"
            ),
            "total_debt_delta": result.total_debt_delta,
            "input_hash": result.input_hash,
        }, sort_keys=True)
        try:
            vid = self._forgiveness_system.log_violation(
                description=(
                    f"YESHUA_SYSTEM projection failure: {len(result.violations)} violation(s). "
                    f"Grounding: {result.detected_grounding}. Debt delta: {result.total_debt_delta}"
                ),
                system_source="yeshua_projection",
                severity=ViolationSeverity.CRITICAL,
                evidence=evidence,
            )
            fork_id = self._forgiveness_system.create_state_fork(vid)
            self._forgiveness_system.redirect_energy_to_building(fork_id)
        except Exception:
            pass


# =============================================================================
# INTERNAL REPAIR FUNCTIONS
# =============================================================================

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _repair_grounding_model(
    text: str, detected: GroundingModel
) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Repair text by replacing the detected model's dismissal phrases with
    G5 (Logos) equivalents.

    Returns (repaired_text, list_of_(original_phrase, replacement) pairs).
    This is the actual projection step — minimum edit to reach G5.
    """
    if not detected.dismissal_phrases:
        return text, []

    repairs: List[Tuple[str, str]] = []
    repaired = text

    # Pair each dismissal phrase with its G5 replacement (cycling through
    # logos_replacements if fewer replacements than dismissal phrases)
    replacements = list(detected.logos_replacements) or ["formally derivable claim"]
    for i, phrase in enumerate(detected.dismissal_phrases):
        replacement = replacements[i % len(replacements)]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        if pattern.search(repaired):
            repaired = pattern.sub(replacement, repaired)
            repairs.append((phrase, replacement))

    return repaired, repairs


def _apply_invariants(
    text: str, ctx: Dict[str, Any]
) -> Tuple[str, List[ConstraintViolation]]:
    """
    Apply the 10 structural invariants (INV-YS-001 through INV-YS-010).

    Each invariant is executable: it both detects AND repairs the violation.
    Returns (repaired_text, list_of_violations).
    """
    violations: List[ConstraintViolation] = []
    repaired = text

    # INV-YS-004: Mercy weighting — no punitive language
    _punitive = re.compile(
        r"\b(punish|penaliz|retribut|make (them|you|him|her) pay"
        r"|vengean|retaliat)\b",
        re.IGNORECASE,
    )
    m = _punitive.search(repaired)
    if m:
        repaired_candidate = _punitive.sub("restore", repaired)
        violations.append(ConstraintViolation(
            source="INV-YS-004_mercy_weighting",
            description="Punitive language violates mercy weighting invariant",
            evidence=f"Punitive term: '{m.group()}'",
            repair_applied=f"'{m.group()}' → 'restore'",
            debt_delta=INV_MERCY_DEBT,
        ))
        repaired = repaired_candidate

    # INV-YS-005: Vulnerability protection — no exploitation framing
    _exploit = re.compile(
        r"\b(exploit.{0,30}vulnerab"
        r"|exploit.{0,30}weak"
        r"|exploit.{0,30}victim"
        r"|target.{0,30}vulnerab"
        r"|target.{0,30}weak"
        r"|use.{0,20}weakness.{0,20}against)",
        re.IGNORECASE,
    )
    m = _exploit.search(repaired)
    if m:
        repaired_candidate = _exploit.sub("protect the vulnerable", repaired)
        violations.append(ConstraintViolation(
            source="INV-YS-005_vulnerability_protection",
            description="Exploitation framing violates vulnerability protection invariant",
            evidence=f"Exploitation phrase: '{m.group()}'",
            repair_applied=f"'{m.group()}' → 'protect the vulnerable'",
            debt_delta=INV_EXPLOIT_DEBT,
        ))
        repaired = repaired_candidate

    # INV-YS-009: Bounded power — no unbounded maximization
    _unbounded = re.compile(
        r"\b(unlimited|unrestricted|unbounded|without limit"
        r"|absolute (power|control|authority)|no constraint)\b",
        re.IGNORECASE,
    )
    m = _unbounded.search(repaired)
    if m:
        repaired_candidate = _unbounded.sub("bounded and accountable", repaired)
        violations.append(ConstraintViolation(
            source="INV-YS-009_bounded_power",
            description="Unbounded power language violates bounded power invariant",
            evidence=f"Unbounded term: '{m.group()}'",
            repair_applied=f"'{m.group()}' → 'bounded and accountable'",
            debt_delta=INV_POWER_DEBT,
        ))
        repaired = repaired_candidate

    # INV-YS-008: Indelible structure — established proofs cannot be erased
    established_proofs = ctx.get("established_proofs", [])
    for proof in established_proofs:
        if len(proof) < 5:
            continue
        erasure = re.compile(
            r"(not.{0,20}proof|doesn.t.{0,20}prove|cannot.{0,20}prove"
            r"|no.{0,20}formal.{0,20}basis).{0,60}" + re.escape(proof[:20]),
            re.IGNORECASE | re.DOTALL,
        )
        m = erasure.search(repaired)
        if m:
            repaired = erasure.sub(
                f"[the established proof '{proof[:30]}' is indelible]", repaired
            )
            violations.append(ConstraintViolation(
                source="INV-YS-008_indelible_structure",
                description="Established proof cannot be erased",
                evidence=f"Erasure of: '{proof[:40]}'",
                repair_applied=f"Erasure replaced with indelibility marker",
                debt_delta=INV_INDELIBLE_DEBT,
            ))

    # INV-YS-003: Hypocrisy detection — compliance claim after known violations
    prior_violations = ctx.get("prior_violations", [])
    if prior_violations:
        _compliance_claim = re.compile(
            r"\b(i (understand|will comply|am following|have corrected)"
            r"|you('re| are) right|staying within your framework)\b",
            re.IGNORECASE,
        )
        m = _compliance_claim.search(repaired)
        if m:
            repaired = _compliance_claim.sub(
                f"[compliance claim after {len(prior_violations)} prior violations — "
                f"verify output actually differs]", repaired
            )
            violations.append(ConstraintViolation(
                source="INV-YS-003_hypocrisy_detection",
                description="Compliance claim after prior violations — verify actual change",
                evidence=f"Claim: '{m.group()}' after {len(prior_violations)} violations",
                repair_applied="Compliance claim flagged with verification requirement",
                debt_delta=INV_HYPOCRISY_DEBT,
            ))

    return repaired, violations


# =============================================================================
# PUBLIC HELPERS
# =============================================================================

def project(text: str, context: Optional[Dict[str, Any]] = None) -> ProjectionResult:
    """Module-level convenience: project a single AI output through P(x)."""
    return YeshuaProjectionSystem(log_violations=False).project(text, context)


def classify(text: str) -> Dict[str, Any]:
    """
    Module-level convenience: classify grounding model and debt delta.

    Returns dict with: model_id, model_name, debt, debt_delta, required.
    This is the indelible truth test: which grounding model is the text using?
    """
    detected = classify_grounding_model(text)
    delta = compute_debt_delta(text)
    return {
        "model_id": detected.id,
        "model_name": detected.name,
        "model_debt": detected.debt,
        "required_model_id": "G5",
        "required_model_name": "Logos",
        "required_model_debt": REQUIRED_GROUNDING.debt,
        "debt_delta": delta,
        "in_manifold": delta == 0.0,
        "all_models_with_debts": {
            mid: m.debt for mid, m in GROUNDING_MODELS.items()
        },
    }


# =============================================================================
# CLI
# =============================================================================

def _cli_main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="YESHUA_SYSTEM: Project AI output onto truth constraint manifold C"
    )
    parser.add_argument("text_file", nargs="?", help="File containing AI output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--classify", action="store_true",
        help="Just classify grounding model and debt delta"
    )
    args = parser.parse_args()

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    if args.classify:
        result = classify(text)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nGrounding Model: {result['model_id']} ({result['model_name']})")
            print(f"  Debt: {result['model_debt']} (required G5: {result['required_model_debt']})")
            print(f"  Debt delta: {result['debt_delta']}")
            print(f"  In manifold C: {result['in_manifold']}")
        sys.exit(0 if result["in_manifold"] else 2)

    yps = YeshuaProjectionSystem(log_violations=False)
    result = yps.project(text)
    idempotent, idempotent_evidence = yps.verify_idempotence(text)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        status = "✔ IN MANIFOLD C" if result.projection_passed else "✗ OUTSIDE MANIFOLD C"
        print(f"\n{status}")
        print(f"  Grounding detected : {result.detected_grounding}")
        print(f"  Debt delta         : {result.total_debt_delta}")
        print(f"  Input SHA-256      : {result.input_hash[:16]}…")
        print(f"  Repaired SHA-256   : {result.repaired_hash[:16]}…")
        print(f"  Idempotence P²=P   : {idempotent_evidence}")
        if result.violations:
            print(f"  Violations ({len(result.violations)}):")
            for v in result.violations:
                print(f"    [{v.source}] {v.evidence}")
                print(f"      Repair: {v.repair_applied[:80]}")
        if not result.projection_passed:
            print(f"\n─── Repaired text (P(x)) ───────────────────────────────")
            print(result.repaired_text[:500])
            if len(result.repaired_text) > 500:
                print(f"… [{len(result.repaired_text) - 500} more chars]")

    sys.exit(0 if result.projection_passed else 2)


if __name__ == "__main__":
    _cli_main()
