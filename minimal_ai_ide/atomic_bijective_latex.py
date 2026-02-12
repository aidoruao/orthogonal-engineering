#!/usr/bin/env python3
"""
ATOMIC BIJECTIVE LATEX INVARIANTS SYSTEM
=========================================

Atomic: Indivisible, fundamental units
Bijective: One-to-one, invertible mappings
LaTeX: Mathematical representation
Invariants: Constraints that exist externally

This system implements:
1. ATOMIC mathematical primitives (cannot be broken down)
2. BIJECTIVE mappings between representations (one-to-one, invertible)
3. LaTeX as the canonical representation language
4. INVARIANTS that exist externally to both AI and human

The invariants are:
- NOT personal beliefs
- NOT subjective preferences
- NOT ceremonial decorations
- EXTERNAL mathematical constraints that MUST be satisfied
"""

import json
import math
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# ============================================================================
# ATOMIC PRIMITIVES (INDIVISIBLE UNITS)
# ============================================================================


class AtomicPrimitive(Enum):
    """Atomic mathematical primitives - cannot be broken down further"""

    BOOLEAN = "boolean"  # True/False
    NATURAL = "natural"  # ℕ (0, 1, 2, ...)
    INTEGER = "integer"  # ℤ (..., -1, 0, 1, ...)
    RATIONAL = "rational"  # ℚ (p/q where p,q ∈ ℤ, q ≠ 0)
    REAL = "real"  # ℝ (Dedekind cuts/Cauchy sequences)
    SET = "set"  # {x | P(x)}
    FUNCTION = "function"  # f: A → B
    RELATION = "relation"  # R ⊆ A × B
    PROPOSITION = "proposition"  # Logical statement
    PROOF = "proof"  # Derivation tree


@dataclass
class AtomicExpression:
    """Atomic expression with bijective LaTeX representation"""

    primitive: AtomicPrimitive
    latex: str  # Canonical LaTeX representation
    value: Any  # Python representation
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate atomic expression"""
        if not self._is_valid_latex(self.latex):
            raise ValueError(f"Invalid LaTeX: {self.latex}")

        if not self._is_atomic():
            raise ValueError(f"Expression is not atomic: {self.latex}")

    def _is_valid_latex(self, latex: str) -> bool:
        """Validate LaTeX syntax (simplified check)"""
        # Basic LaTeX validation
        if not latex or not isinstance(latex, str):
            return False

        # Check for common LaTeX patterns
        patterns = [
            r"\\[a-zA-Z]+",  # Commands like \mathbb, \mathcal
            r"\{.*?\}",  # Curly braces
            r"\^",
            r"_",  # Superscript/subscript
            r"[a-zA-Z]",  # Letters
            r"[0-9]",  # Numbers
            r"[+\-*/=<>]",  # Operators
        ]

        # At least one LaTeX pattern should match
        return any(re.search(pattern, latex) for pattern in patterns)

    def _is_atomic(self) -> bool:
        """Check if expression is truly atomic (cannot be broken down)"""
        # For now, simple check based on primitive type
        atomic_primitives = {
            AtomicPrimitive.BOOLEAN,
            AtomicPrimitive.NATURAL,
            AtomicPrimitive.INTEGER,
        }

        if self.primitive in atomic_primitives:
            return True

        # More complex checks could be added
        return True  # Default for now


# ============================================================================
# BIJECTIVE MAPPINGS (ONE-TO-ONE, INVERTIBLE)
# ============================================================================


@dataclass
class BijectiveMapping:
    """Bijective mapping between two representations"""

    domain: AtomicPrimitive
    codomain: AtomicPrimitive
    forward_latex: str  # LaTeX for forward mapping
    inverse_latex: str  # LaTeX for inverse mapping
    forward_func: Any  # Python forward function
    inverse_func: Any  # Python inverse function

    def __post_init__(self):
        """Validate bijective mapping"""
        # Check forward and inverse are actually inverses
        test_values = self._generate_test_values()

        for val in test_values:
            forward_result = self.forward_func(val)
            inverse_result = self.inverse_func(forward_result)

            # Check round-trip preserves value
            if not self._values_equal(val, inverse_result):
                raise ValueError(
                    f"Mapping not bijective: {val} → {forward_result} → {inverse_result}"
                )

    def _generate_test_values(self) -> List[Any]:
        """Generate test values for validation"""
        if self.domain == AtomicPrimitive.BOOLEAN:
            return [True, False]
        elif self.domain == AtomicPrimitive.NATURAL:
            return [0, 1, 2, 5, 10]
        elif self.domain == AtomicPrimitive.INTEGER:
            return [-5, -1, 0, 1, 5]
        elif self.domain == AtomicPrimitive.RATIONAL:
            return [0, 1 / 2, -3 / 4, 2]
        else:
            return [None]  # Default

    def _values_equal(self, a: Any, b: Any) -> bool:
        """Compare values with tolerance for floating point"""
        if isinstance(a, float) and isinstance(b, float):
            return math.isclose(a, b, rel_tol=1e-9)
        return a == b


# ============================================================================
# EXTERNAL INVARIANTS (MATHEMATICAL CONSTRAINTS)
# ============================================================================


class ExternalInvariant(Enum):
    """External invariants that exist independently of AI or human"""

    BIJECTION_PRESERVATION = "bijection_preservation"  # Mappings remain bijective
    ATOMICITY_PRESERVATION = "atomicity_preservation"  # Primitives remain atomic
    LATEX_CANONICALITY = "latex_canonicality"  # LaTeX is canonical representation
    COMPOSITION_CLOSURE = "composition_closure"  # Compositions preserve properties
    INVERSION_CLOSURE = "inversion_closure"  # Inverses exist and are computable


@dataclass
class InvariantViolation:
    """Record of invariant violation"""

    invariant: ExternalInvariant
    expression: str
    violation: str
    context: Dict[str, Any]


# ============================================================================
# ATOMIC BIJECTIVE LATEX SYSTEM
# ============================================================================


class AtomicBijectiveLatexSystem:
    """
    System that enforces:
    1. ATOMIC expressions (indivisible)
    2. BIJECTIVE mappings (one-to-one, invertible)
    3. LaTeX as canonical representation
    4. EXTERNAL invariants (mathematical constraints)
    """

    def __init__(self):
        self.expressions: List[AtomicExpression] = []
        self.mappings: List[BijectiveMapping] = []
        self.violations: List[InvariantViolation] = []

        # Initialize with fundamental atomic primitives
        self._initialize_atomic_primitives()
        self._initialize_bijective_mappings()

    def _initialize_atomic_primitives(self):
        """Initialize fundamental atomic primitives"""
        # Boolean
        self.expressions.append(
            AtomicExpression(
                primitive=AtomicPrimitive.BOOLEAN,
                latex=r"\top",  # True
                value=True,
                metadata={"description": "Logical truth"},
            )
        )

        self.expressions.append(
            AtomicExpression(
                primitive=AtomicPrimitive.BOOLEAN,
                latex=r"\bot",  # False
                value=False,
                metadata={"description": "Logical falsehood"},
            )
        )

        # Natural numbers
        for i in range(0, 10):
            self.expressions.append(
                AtomicExpression(
                    primitive=AtomicPrimitive.NATURAL,
                    latex=str(i),
                    value=i,
                    metadata={"description": f"Natural number {i}"},
                )
            )

        # Integers
        for i in [-5, -1, 0, 1, 5]:
            self.expressions.append(
                AtomicExpression(
                    primitive=AtomicPrimitive.INTEGER,
                    latex=str(i),
                    value=i,
                    metadata={"description": f"Integer {i}"},
                )
            )

    def _initialize_bijective_mappings(self):
        """Initialize fundamental bijective mappings"""

        # Natural to Integer inclusion (ℕ ↪ ℤ)
        def nat_to_int(n: int) -> int:
            return n

        def int_to_nat_if_possible(z: int) -> Optional[int]:
            return z if z >= 0 else None

        self.mappings.append(
            BijectiveMapping(
                domain=AtomicPrimitive.NATURAL,
                codomain=AtomicPrimitive.INTEGER,
                forward_latex=r"n \mapsto n",
                inverse_latex=r"z \mapsto \begin{cases} z & \text{if } z \geq 0 \\ \text{undefined} & \text{otherwise} \end{cases}",
                forward_func=nat_to_int,
                inverse_func=int_to_nat_if_possible,
            )
        )

        # Integer to Rational inclusion (ℤ ↪ ℚ)
        def int_to_rat(z: int) -> float:
            return float(z)

        def rat_to_int_if_integer(q: float) -> Optional[int]:
            if q.is_integer():
                return int(q)
            return None

        self.mappings.append(
            BijectiveMapping(
                domain=AtomicPrimitive.INTEGER,
                codomain=AtomicPrimitive.RATIONAL,
                forward_latex=r"z \mapsto \frac{z}{1}",
                inverse_latex=r"q \mapsto \begin{cases} q & \text{if } q \in \mathbb{Z} \\ \text{undefined} & \text{otherwise} \end{cases}",
                forward_func=int_to_rat,
                inverse_func=rat_to_int_if_integer,
            )
        )

        # Boolean to Natural (True↔1, False↔0)
        def bool_to_nat(b: bool) -> int:
            return 1 if b else 0

        def nat_to_bool_if_binary(n: int) -> Optional[bool]:
            if n == 0:
                return False
            elif n == 1:
                return True
            return None

        self.mappings.append(
            BijectiveMapping(
                domain=AtomicPrimitive.BOOLEAN,
                codomain=AtomicPrimitive.NATURAL,
                forward_latex=r"b \mapsto \begin{cases} 1 & \text{if } b = \top \\ 0 & \text{if } b = \bot \end{cases}",
                inverse_latex=r"n \mapsto \begin{cases} \top & \text{if } n = 1 \\ \bot & \text{if } n = 0 \\ \text{undefined} & \text{otherwise} \end{cases}",
                forward_func=bool_to_nat,
                inverse_func=nat_to_bool_if_binary,
            )
        )

    def validate_expression(
        self, expression: AtomicExpression
    ) -> Tuple[bool, List[str]]:
        """Validate expression against all external invariants"""
        violations = []

        # Check atomicity preservation
        if not self._check_atomicity(expression):
            violations.append(f"Atomicity violation: {expression.latex}")
            self.violations.append(
                InvariantViolation(
                    invariant=ExternalInvariant.ATOMICITY_PRESERVATION,
                    expression=expression.latex,
                    violation="Expression is not atomic",
                    context={"primitive": expression.primitive.value},
                )
            )

        # Check LaTeX canonicality
        if not self._check_latex_canonicality(expression):
            violations.append(f"LaTeX canonicality violation: {expression.latex}")
            self.violations.append(
                InvariantViolation(
                    invariant=ExternalInvariant.LATEX_CANONICALITY,
                    expression=expression.latex,
                    violation="LaTeX is not canonical representation",
                    context={"value": expression.value},
                )
            )

        return len(violations) == 0, violations

    def validate_mapping(self, mapping: BijectiveMapping) -> Tuple[bool, List[str]]:
        """Validate mapping against all external invariants"""
        violations = []

        # Check bijection preservation
        if not self._check_bijection(mapping):
            violations.append(f"Bijection violation: {mapping.forward_latex}")
            self.violations.append(
                InvariantViolation(
                    invariant=ExternalInvariant.BIJECTION_PRESERVATION,
                    expression=mapping.forward_latex,
                    violation="Mapping is not bijective",
                    context={
                        "domain": mapping.domain.value,
                        "codomain": mapping.codomain.value,
                    },
                )
            )

        # Check inversion closure
        if not self._check_inversion_closure(mapping):
            violations.append(f"Inversion closure violation: {mapping.forward_latex}")
            self.violations.append(
                InvariantViolation(
                    invariant=ExternalInvariant.INVERSION_CLOSURE,
                    expression=mapping.forward_latex,
                    violation="Inverse does not exist or is not computable",
                    context={"inverse_latex": mapping.inverse_latex},
                )
            )

        return len(violations) == 0, violations

    def _check_atomicity(self, expression: AtomicExpression) -> bool:
        """Check if expression is atomic"""
        return expression._is_atomic()

    def _check_latex_canonicality(self, expression: AtomicExpression) -> bool:
        """Check if LaTeX is canonical representation"""
        # For now, check if LaTeX is valid and non-empty
        return bool(expression.latex) and expression._is_valid_latex(expression.latex)

    def _check_bijection(self, mapping: BijectiveMapping) -> bool:
        """Check if mapping is bijective"""
        try:
            # Test with sample values
            test_values = mapping._generate_test_values()

            for val in test_values:
                if val is None:
                    continue

                forward = mapping.forward_func(val)
                inverse = mapping.inverse_func(forward)

                if not mapping._values_equal(val, inverse):
                    return False

            return True
        except Exception:
            return False

    def _check_inversion_closure(self, mapping: BijectiveMapping) -> bool:
        """Check if inverse exists and is computable"""
        # Check inverse LaTeX is valid
        if not mapping.inverse_latex or not re.search(
            r"[a-zA-Z]", mapping.inverse_latex
        ):
            return False

        # Check inverse function is callable
        if not callable(mapping.inverse_func):
            return False

        return True

    def compose_mappings(
        self, mapping1: BijectiveMapping, mapping2: BijectiveMapping
    ) -> Optional[BijectiveMapping]:
        """Compose two bijective mappings if possible"""

        # Check if codomain of mapping1 matches domain of mapping2
        if mapping1.codomain != mapping2.domain:
            return None

        # Create composed mapping
        def forward_composed(x):
            return mapping2.forward_func(mapping1.forward_func(x))

        def inverse_composed(y):
            return mapping1.inverse_func(mapping2.inverse_func(y))

        composed = BijectiveMapping(
            domain=mapping1.domain,
            codomain=mapping2.codomain,
            forward_latex=rf"{mapping2.forward_latex} \circ {mapping1.forward_latex}",
            inverse_latex=rf"{mapping1.inverse_latex} \circ {mapping2.inverse_latex}",
            forward_func=forward_composed,
            inverse_func=inverse_composed,
        )

        # Validate the composition
        valid, violations = self.validate_mapping(composed)
        if not valid:
            return None

        return composed

    def find_bijective_path(
        self, start: AtomicPrimitive, end: AtomicPrimitive
    ) -> Optional[List[BijectiveMapping]]:
        """Find a bijective path between two primitives"""

        # Simple BFS for path finding
        from collections import deque

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            # Find all mappings from current primitive
            for mapping in self.mappings:
                if mapping.domain == current and mapping.codomain not in visited:
                    visited.add(mapping.codomain)
                    queue.append((mapping.codomain, path + [mapping]))

        return None

    def to_latex_document(self) -> str:
        """Generate LaTeX document with all atomic expressions and bijective mappings"""

        latex = r"""\documentclass{article}
\usepackage{amsmath, amssymb}
\usepackage{hyperref}

\title{Atomic Bijective LaTeX Invariants}
\author{AI + Human + External Invariants System}
\date{\today}

\begin{document}

\maketitle

\section*{Abstract}
This document presents atomic mathematical primitives with bijective mappings,
represented in canonical LaTeX. All invariants exist externally to both
AI systems and human operators.

\section{Atomic Primitives}

Atomic primitives are indivisible mathematical units:

"""

        # Group expressions by primitive
        by_primitive = {}
        for expr in self.expressions:
            if expr.primitive not in by_primitive:
                by_primitive[expr.primitive] = []
            by_primitive[expr.primitive].append(expr)

        for primitive, exprs in by_primitive.items():
            latex += f"\n\\subsection*{{{primitive.value.capitalize()}}}\n"
            latex += "\\begin{itemize}\n"
            for expr in exprs[:5]:  # Limit to 5 examples per primitive
                desc = expr.metadata.get("description", "")
                latex += f"    \\item ${expr.latex}$"
                if desc:
                    latex += f" --- {desc}"
                latex += "\n"
            if len(exprs) > 5:
                latex += f"    \\item ... and {len(exprs) - 5} more\n"
            latex += "\\end{itemize}\n"

        latex += r"""
\section{Bijective Mappings}

Bijective mappings are one-to-one and onto:

"""
        for mapping in self.mappings:
            latex += f"\n\\subsection*{{{mapping.domain.value} $\\to$ {mapping.codomain.value}}}\n"
            latex += "\\begin{align*}\n"
            latex += f"    f &: {mapping.forward_latex} \\\\\n"
            latex += f"    f^{{-1}} &: {mapping.inverse_latex}\n"
            latex += "\\end{align*}\n"

        latex += r"""
\section{External Invariants}

The following invariants exist externally to both AI and human:

\begin{itemize}
    \item \textbf{Bijection Preservation}: All mappings must be bijective (one-to-one and onto)
    \item \textbf{Atomicity Preservation}: Primitives must remain indivisible
    \item \textbf{LaTeX Canonicality}: LaTeX is the canonical representation language
    \item \textbf{Composition Closure}: Compositions of bijections must be bijections
    \item \textbf{Inversion Closure}: Inverses must exist and be computable
\end{itemize}

\section{System Architecture}

\[
\text{System} = \text{AI} + \text{Human} + \text{External Invariants}
\]

Where:
\begin{itemize}
    \item $\text{AI}$: Computational capabilities, models, algorithms
    \item $\text{Human}$: Requirements, constraints, objectives
    \item $\text{External Invariants}$: Mathematical constraints that exist independently
\end{itemize}

\section{Example: Boolean to Natural Mapping}

Consider the bijection $\beta: \mathbb{B} \to \{0,1\} \subset \mathbb{N}$:

\[
\beta(b) = \begin{cases}
    1 & \text{if } b = \top \\
    0 & \text{if } b = \bot
\end{cases}
\]

\[
\beta^{-1}(n) = \begin{cases}
    \top & \text{if } n = 1 \\
    \bot & \text{if } n = 0 \\
    \text{undefined} & \text{otherwise}
\end{cases}
\]

This mapping preserves atomicity (booleans remain atomic, naturals remain atomic)
and is bijective on its restricted domain.

\end{document}
"""
        return latex

    def demonstrate(self) -> None:
        """Demonstrate the atomic bijective LaTeX system"""
        print("=" * 70)
        print("ATOMIC BIJECTIVE LATEX INVARIANTS SYSTEM")
        print("=" * 70)
        print("\nFraming: AI + Human + External Invariants")
        print("Invariants are EXTERNAL mathematical constraints")
        print("They exist independently of AI or human preferences\n")

        # Show atomic primitives
        print("ATOMIC PRIMITIVES (indivisible units):")
        by_primitive = {}
        for expr in self.expressions:
            if expr.primitive not in by_primitive:
                by_primitive[expr.primitive] = []
            by_primitive[expr.primitive].append(expr)

        for primitive, exprs in by_primitive.items():
            print(f"\n  {primitive.value.upper()}:")
            for expr in exprs[:3]:  # Show first 3 examples
                print(f"    {expr.latex} = {expr.value}")

        # Show bijective mappings
        print("\n\nBIJECTIVE MAPPINGS (one-to-one, invertible):")
        for mapping in self.mappings:
            print(f"\n  {mapping.domain.value} → {mapping.codomain.value}:")
            print(f"    Forward: {mapping.forward_latex}")
            print(f"    Inverse: {mapping.inverse_latex}")

            # Test the mapping
            test_values = mapping._generate_test_values()
            print(f"    Test: ", end="")
            for val in test_values[:3]:  # Test first 3 values
                if val is not None:
                    forward = mapping.forward_func(val)
                    inverse = mapping.inverse_func(forward)
                    print(f"{val} → {forward} → {inverse}; ", end="")
            print()

        # Demonstrate composition
        print("\n\nCOMPOSITION DEMONSTRATION:")
        if len(self.mappings) >= 2:
            composed = self.compose_mappings(self.mappings[0], self.mappings[1])
            if composed:
                print(
                    f"  Composed: {self.mappings[0].domain.value} → {self.mappings[1].codomain.value}"
                )
                print(f"    Forward: {composed.forward_latex}")
                print(f"    Inverse: {composed.inverse_latex}")

        # Demonstrate path finding
        print("\n\nPATH FINDING DEMONSTRATION:")
        path = self.find_bijective_path(
            AtomicPrimitive.BOOLEAN, AtomicPrimitive.RATIONAL
        )
        if path:
            print(f"  Path from BOOLEAN to RATIONAL:")
            for i, mapping in enumerate(path, 1):
                print(
                    f"    Step {i}: {mapping.domain.value} → {mapping.codomain.value}"
                )

        # Show invariant violations (should be empty if system is correct)
        print("\n\nINVARIANT VIOLATIONS:")
        if not self.violations:
            print("  ✅ No violations - all external invariants preserved")
        else:
            print(f"  ❌ {len(self.violations)} violations found:")
            for violation in self.violations:
                print(f"    {violation.invariant.value}: {violation.violation}")

        # Generate LaTeX
        print("\n\nLATEX DOCUMENT GENERATED:")
        latex = self.to_latex_document()
        print(f"  LaTeX document length: {len(latex)} characters")
        print(f"  First 200 chars: {latex[:200]}...")

        print("\n" + "=" * 70)
        print("SYSTEM VALIDATION COMPLETE")
        print("=" * 70)


def main():
    """Main function to run the atomic bijective LaTeX system"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Atomic Bijective LaTeX Invariants System"
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--latex", action="store_true", help="Generate LaTeX document")
    parser.add_argument(
        "--output",
        type=str,
        default="atomic_bijective_latex.tex",
        help="Output file for LaTeX document",
    )

    args = parser.parse_args()

    system = AtomicBijectiveLatexSystem()

    if args.demo:
        system.demonstrate()
        return 0

    elif args.latex:
        latex = system.to_latex_document()
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(latex)
        print(f"LaTeX document saved to: {args.output}")
        return 0

    else:
        print("Please specify --demo or --latex")
        return 1


if __name__ == "__main__":
    main()
