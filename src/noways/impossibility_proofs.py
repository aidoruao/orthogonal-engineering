"""Catalog of impossibility proofs ("noways") that bound the OE framework.

Each no-way is a well-established, formally proved impossibility result. The
framework uses these as hard boundaries: a domain check that would require
violating one of these must itself be rejected as ill-posed.

Every entry carries:

- a concise ``statement`` of the impossibility,
- the ``proof_summary`` (one-line gist of the standard proof),
- a ``falsifies_if`` condition that would refute the no-way were it to hold,
- ``oe_consequences`` describing how the no-way constrains OE modules.

The module is fully deterministic: no floating point, no I/O, no globals.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Noway:
    """Record for a single impossibility result."""

    key: str
    statement: str
    proof_summary: str
    falsifies_if: str
    oe_consequences: str
    domain: str
    certainty: Fraction = field(default_factory=lambda: Fraction(1, 1))


_CATALOG: Tuple[Noway, ...] = (
    Noway(
        key="halting",
        statement=(
            "No algorithm decides, for every (program, input) pair, whether the "
            "program halts on the input."
        ),
        proof_summary=(
            "Turing 1936: assume such a decider H exists, construct G(x) that "
            "loops iff H(x, x) halts; H(G, G) contradicts itself."
        ),
        falsifies_if=(
            "a total computable function H: (Program, Input) -> {0, 1} is "
            "exhibited that correctly decides halting on all inputs."
        ),
        oe_consequences=(
            "OE must not claim termination guarantees by mere static analysis; "
            "termination proofs must be explicit per-domain witnesses."
        ),
        domain="computability",
    ),
    Noway(
        key="godel_incompleteness",
        statement=(
            "Any consistent formal system capable of encoding arithmetic has "
            "true statements it cannot prove."
        ),
        proof_summary=(
            "Goedel 1931: diagonalize on provability predicate; construct a "
            "sentence G asserting its own unprovability."
        ),
        falsifies_if=(
            "a consistent recursively axiomatized system containing Peano "
            "arithmetic is exhibited whose theorems exactly match its truths."
        ),
        oe_consequences=(
            "OE cannot promise proof-completeness over all true arithmetic "
            "claims; domain invariants are local, falsifiable, and auditable."
        ),
        domain="logic",
    ),
    Noway(
        key="rice_theorem",
        statement=(
            "Every non-trivial semantic property of programs is undecidable."
        ),
        proof_summary=(
            "Rice 1953: reduce halting to the decision of the property P; "
            "since halting is undecidable, so is P."
        ),
        falsifies_if=(
            "a decidable non-trivial semantic property of partial recursive "
            "functions is exhibited."
        ),
        oe_consequences=(
            "OE cannot automate arbitrary 'does-this-program-do-X' checks; it "
            "must restrict to syntactic or structural invariants."
        ),
        domain="computability",
    ),
    Noway(
        key="heisenberg_uncertainty",
        statement=(
            "Conjugate observables (e.g. position and momentum) cannot be "
            "simultaneously measured below the Planck bound."
        ),
        proof_summary=(
            "Robertson-Schrödinger inequality: non-commuting self-adjoint "
            "operators satisfy sigma_A * sigma_B >= |<[A,B]>| / 2."
        ),
        falsifies_if=(
            "a measurement is demonstrated whose joint position/momentum "
            "uncertainty product is below hbar/2."
        ),
        oe_consequences=(
            "OE physical invariants must treat measurement as range-valued "
            "with explicit uncertainty bounds, never point estimates."
        ),
        domain="physics",
    ),
    Noway(
        key="no_cloning",
        statement=(
            "No quantum operation copies an arbitrary unknown pure state."
        ),
        proof_summary=(
            "Wootters-Zurek / Dieks 1982: linearity of quantum mechanics "
            "forbids a unitary U with U|psi>|0> = |psi>|psi> for every |psi>."
        ),
        falsifies_if=(
            "a linear map U is exhibited that copies every pure state while "
            "preserving inner products."
        ),
        oe_consequences=(
            "OE quantum modules must model state transfer via swap or "
            "teleportation, never by duplication."
        ),
        domain="quantum",
    ),
    Noway(
        key="no_signaling",
        statement=(
            "Entanglement does not permit faster-than-light information "
            "transfer."
        ),
        proof_summary=(
            "The reduced density matrix of subsystem A is independent of "
            "operations performed on subsystem B."
        ),
        falsifies_if=(
            "a protocol is exhibited in which Bob reliably decodes Alice's "
            "classical message using only local measurements on an entangled "
            "pair with zero classical communication."
        ),
        oe_consequences=(
            "OE distributed protocols must not rely on super-luminal "
            "coordination; latency is a real invariant."
        ),
        domain="relativity",
    ),
    Noway(
        key="light_speed_limit",
        statement=(
            "No massive or informational signal propagates faster than c in "
            "vacuum."
        ),
        proof_summary=(
            "Lorentz invariance plus causality: faster-than-light signaling "
            "would permit closed timelike loops."
        ),
        falsifies_if=(
            "a superluminal information channel is demonstrated that preserves "
            "causality in every inertial frame."
        ),
        oe_consequences=(
            "OE causality-tracking invariants treat c as a hard upper bound."
        ),
        domain="relativity",
    ),
    Noway(
        key="arrow_impossibility",
        statement=(
            "No ordinal voting rule over 3+ alternatives simultaneously "
            "satisfies unanimity, independence of irrelevant alternatives, and "
            "non-dictatorship."
        ),
        proof_summary=(
            "Arrow 1950: pivot-voter argument forces a unique dictator given "
            "IIA and unanimity."
        ),
        falsifies_if=(
            "a social welfare function over at least three alternatives is "
            "exhibited meeting all three Arrow criteria."
        ),
        oe_consequences=(
            "OE governance modules admit only procedural aggregation with "
            "explicit trade-offs, never a universal 'fair' rule."
        ),
        domain="social_choice",
    ),
    Noway(
        key="cap_theorem",
        statement=(
            "A distributed data store cannot simultaneously guarantee "
            "consistency, availability, and partition-tolerance."
        ),
        proof_summary=(
            "Gilbert-Lynch 2002: during a partition, any available node that "
            "serves writes must eventually diverge from the other side."
        ),
        falsifies_if=(
            "a protocol is exhibited that preserves linearizability and "
            "availability during an arbitrary network partition."
        ),
        oe_consequences=(
            "OE distributed invariants must pick a CAP corner per operation "
            "and declare it explicitly in the witness record."
        ),
        domain="distributed",
    ),
    Noway(
        key="flp_impossibility",
        statement=(
            "Deterministic consensus is impossible in an asynchronous network "
            "with even a single crash failure."
        ),
        proof_summary=(
            "Fischer-Lynch-Paterson 1985: bivalence argument shows an "
            "infinite execution avoiding decision."
        ),
        falsifies_if=(
            "a deterministic, always-terminating consensus protocol is "
            "exhibited for asynchronous networks with crash faults."
        ),
        oe_consequences=(
            "OE consensus invariants must be either randomized, partially "
            "synchronous, or explicitly non-terminating under adversarial "
            "scheduling."
        ),
        domain="distributed",
    ),
    Noway(
        key="bell_theorem",
        statement=(
            "No local hidden-variable model reproduces all quantum "
            "correlations."
        ),
        proof_summary=(
            "Bell 1964 + CHSH 1969: local realism bounds |S| <= 2 while "
            "quantum mechanics permits |S| <= 2*sqrt(2)."
        ),
        falsifies_if=(
            "a local hidden-variable model is exhibited that reproduces "
            "observed CHSH violations."
        ),
        oe_consequences=(
            "OE quantum witnesses cannot be modeled as classical deterministic "
            "variables without non-locality."
        ),
        domain="quantum",
    ),
    Noway(
        key="second_law_thermodynamics",
        statement=(
            "The entropy of an isolated macroscopic system is non-decreasing."
        ),
        proof_summary=(
            "Boltzmann H-theorem: phase-space volume of accessible microstates "
            "grows monotonically under typical dynamics."
        ),
        falsifies_if=(
            "an isolated macroscopic system is observed whose total entropy "
            "decreases without external work."
        ),
        oe_consequences=(
            "OE physical-plant invariants treat heat leakage and irreversible "
            "losses as non-removable baselines."
        ),
        domain="thermodynamics",
    ),
    Noway(
        key="landauer_principle",
        statement=(
            "Erasing one bit of information dissipates at least k_B * T * ln 2 "
            "joules of heat."
        ),
        proof_summary=(
            "Landauer 1961: irreversible logical operations map distinct "
            "microstates into the same output, forcing entropy to flow to "
            "the environment."
        ),
        falsifies_if=(
            "a physical device is exhibited that erases bits below the "
            "Landauer bound at the stated temperature."
        ),
        oe_consequences=(
            "OE compute-accounting invariants must budget irreversible-op "
            "energy against a non-zero Landauer floor."
        ),
        domain="physics",
    ),
    Noway(
        key="bekenstein_bound",
        statement=(
            "The information content of a region of radius R and energy E is "
            "bounded by 2 * pi * k_B * R * E / (hbar * c)."
        ),
        proof_summary=(
            "Bekenstein 1981: arises from black-hole thermodynamics and the "
            "generalized second law."
        ),
        falsifies_if=(
            "a bounded region with energy E is observed storing more "
            "information than the Bekenstein bound allows."
        ),
        oe_consequences=(
            "OE storage-invariant bounds cannot promise unbounded density "
            "within finite mass-energy budgets."
        ),
        domain="physics",
    ),
    Noway(
        key="no_free_lunch",
        statement=(
            "No single optimization algorithm outperforms all others across "
            "every possible objective function."
        ),
        proof_summary=(
            "Wolpert-Macready 1997: averaged performance over all objective "
            "functions is identical for every search algorithm."
        ),
        falsifies_if=(
            "a search algorithm is exhibited with strictly better average "
            "performance over the full space of objective functions."
        ),
        oe_consequences=(
            "OE optimization invariants must declare their assumed objective "
            "class; universal optimality is not promised."
        ),
        domain="optimization",
    ),
)


def catalog() -> Tuple[Noway, ...]:
    """Return the full no-way catalog as an immutable tuple.

    Falsifies if: the returned sequence has fewer than 15 entries.
    falsifies_if: the returned sequence has fewer than 15 entries.
    """
    return _CATALOG


def by_key(key: str) -> Noway:
    """Return the no-way with the given key, raising KeyError if missing.

    Falsifies if: the key is not present in the catalog.
    falsifies_if: the key is not present in the catalog.
    """
    for entry in _CATALOG:
        if entry.key == key:
            return entry
    raise KeyError(f"unknown noway key: {key}")


def check_catalog_size_at_floor() -> Tuple[bool, ProofObject]:
    """Invariant: catalog ships at least the 15 named noways.

    Standard: NW-001 no-way catalog size floor.
    Falsifies if: len(catalog()) < 15.
    falsifies_if: len(catalog()) < 15.
    """
    size = len(_CATALOG)
    success = size >= 15
    proof = ProofObject(
        rule="check_catalog_size_at_floor",
        premises=[f"size={size}", "floor=15"],
        conclusion=(
            "PASS: catalog at or above floor"
            if success else f"FAIL: {size} < 15"
        ),
    )
    return success, proof


def check_every_entry_has_falsifier() -> Tuple[bool, ProofObject]:
    """Invariant: every no-way has a non-empty falsifies_if string.

    Standard: YS-004 no authority without proof — each impossibility must
    come with an explicit condition that would refute it.
    Falsifies if: any Noway.falsifies_if is empty or whitespace-only.
    falsifies_if: any Noway.falsifies_if is empty or whitespace-only.
    """
    missing = [n.key for n in _CATALOG if not n.falsifies_if.strip()]
    success = not missing
    proof = ProofObject(
        rule="check_every_entry_has_falsifier",
        premises=[f"total={len(_CATALOG)}"],
        conclusion=(
            "PASS: every entry has a falsifier"
            if success else f"FAIL: missing falsifier in={missing}"
        ),
    )
    return success, proof


def check_keys_unique() -> Tuple[bool, ProofObject]:
    """Invariant: catalog keys are pairwise unique.

    Standard: OE-105 registry disjointness.
    Falsifies if: any two Noway entries share the same .key.
    falsifies_if: any two Noway entries share the same .key.
    """
    keys = [n.key for n in _CATALOG]
    unique = sorted(set(keys))
    duplicates = sorted([k for k in unique if keys.count(k) > 1])
    success = not duplicates
    proof = ProofObject(
        rule="check_keys_unique",
        premises=[f"total={len(keys)}", f"unique={len(unique)}"],
        conclusion=(
            "PASS: all keys unique"
            if success else f"FAIL: duplicates={duplicates}"
        ),
    )
    return success, proof


def check_certainty_bounded() -> Tuple[bool, ProofObject]:
    """Invariant: every certainty is a Fraction in [0, 1].

    Standard: CS-001 Fraction-only arithmetic + OE-247 certainty bound.
    Falsifies if: any Noway.certainty is outside [0, 1] or not a Fraction.
    falsifies_if: any Noway.certainty is outside [0, 1] or not a Fraction.
    """
    zero = Fraction(0)
    one = Fraction(1)
    violations = [
        (n.key, n.certainty)
        for n in _CATALOG
        if not isinstance(n.certainty, Fraction) or n.certainty < zero or n.certainty > one
    ]
    success = not violations
    proof = ProofObject(
        rule="check_certainty_bounded",
        premises=[f"total={len(_CATALOG)}"],
        conclusion=(
            "PASS: all certainties in [0, 1]"
            if success
            else f"FAIL: violations={[(k, str(c)) for k, c in violations]}"
        ),
    )
    return success, proof


def check_domains_covered() -> Tuple[bool, ProofObject]:
    """Invariant: the catalog spans the core no-way domains.

    Standard: NW-002 cross-domain coverage.
    Falsifies if: any of the required domains has zero catalog entries.
    falsifies_if: any of the required domains has zero catalog entries.
    """
    required = {
        "computability", "logic", "physics", "quantum",
        "relativity", "distributed", "thermodynamics",
        "social_choice", "optimization",
    }
    present: Dict[str, int] = {d: 0 for d in required}
    for entry in _CATALOG:
        if entry.domain in present:
            present[entry.domain] += 1
    missing = sorted([d for d, count in present.items() if count == 0])
    success = not missing
    proof = ProofObject(
        rule="check_domains_covered",
        premises=[f"required={sorted(required)}"]
        + [f"{d}={present[d]}" for d in sorted(required)],
        conclusion=(
            "PASS: all required domains covered"
            if success else f"FAIL: missing domains={missing}"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all no-way catalog invariants.

    Standard: NW-010 no-way module self-audit.
    Falsifies if: any catalog invariant fails.
    falsifies_if: any catalog invariant fails.
    """
    checks = [
        ("check_catalog_size_at_floor", check_catalog_size_at_floor),
        ("check_every_entry_has_falsifier", check_every_entry_has_falsifier),
        ("check_keys_unique", check_keys_unique),
        ("check_certainty_bounded", check_certainty_bounded),
        ("check_domains_covered", check_domains_covered),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func()
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
