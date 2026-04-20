"""Pattern: Equity Threshold

Implements the requirement that resource distribution variance stays
within bounds. No group can monopolize resources.

Mathematical: variance(allocations) <= threshold
              Gini coefficient <= threshold

Used by: D_SCHOOL_FUNDING, D_NEIGHBORHOOD_EQUITY, D_SCHOOL_EQUITY,
D_TRANSIT, D_UTILITY_REGULATION

All arithmetic is performed over ``fractions.Fraction``; no ``float`` is
ever introduced. Callers that need a decimal rendering can use
:func:`src.orthogonal_engineering.fraction_display.format_decimal`.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List


@dataclass
class Allocation:
    """A resource allocation."""
    recipient_id: str
    amount: Fraction
    population: int = 1  # For per-capita calculations

    @property
    def per_capita(self) -> Fraction:
        """Calculate per-capita amount."""
        if self.population == 0:
            return Fraction(0)
        return self.amount / self.population


class EquityThreshold:
    """Enforces equity thresholds on resource allocations.

    Resource distribution must stay within bounded variance. No recipient
    can receive a disproportionate share.

    Attributes:
        variance_threshold: Maximum allowed coefficient-of-variation-squared.
        gini_threshold: Maximum allowed Gini coefficient.
    """

    def __init__(
        self,
        variance_threshold: Fraction = Fraction(15, 100),  # 0.15
        gini_threshold: Fraction = Fraction(4, 10),        # 0.40
    ) -> None:
        self.variance_threshold = variance_threshold
        self.gini_threshold = gini_threshold
        self.violations: List[Dict[str, Any]] = []

    def calculate_variance(self, allocations: List[Allocation]) -> Fraction:
        """Return the coefficient-of-variation squared of per-capita allocations.

        Defined as ``variance / mean^2`` with the sample variance
        (denominator ``n-1``). Returns ``Fraction(0)`` for fewer than two
        allocations or a zero mean.

        Falsifies if: for any list of allocations, the returned value is not
        equal to the exact rational ``variance / mean^2``.
        falsifies_if: returned value disagrees with the exact rational
        coefficient-of-variation squared.
        """
        values: List[Fraction] = [a.per_capita for a in allocations]
        n = len(values)
        if n < 2:
            return Fraction(0)
        total = sum(values, Fraction(0))
        mean = total / n
        if mean == 0:
            return Fraction(0)
        squared_dev_sum = sum(((v - mean) * (v - mean) for v in values), Fraction(0))
        variance = squared_dev_sum / (n - 1)
        return variance / (mean * mean)

    def calculate_gini(self, allocations: List[Allocation]) -> Fraction:
        """Return the Gini coefficient of per-capita allocations.

        Uses the standard sorted-rank formula
        ``(2 * sum(i * x_i)) / (n * sum(x)) - (n + 1) / n`` with all
        arithmetic kept in ``Fraction``.

        Falsifies if: the returned Fraction does not equal the closed-form
        Gini value for the provided allocations, or returns a negative
        value for strictly non-negative inputs.
        falsifies_if: returned value disagrees with the closed-form Gini on
        the provided inputs.
        """
        values: List[Fraction] = sorted(a.per_capita for a in allocations)
        n = len(values)
        if n < 2:
            return Fraction(0)
        total = sum(values, Fraction(0))
        if total == 0:
            return Fraction(0)
        weighted = sum(
            (Fraction(i + 1) * v for i, v in enumerate(values)),
            Fraction(0),
        )
        return (2 * weighted) / (n * total) - Fraction(n + 1, n)

    def check_equity(self, allocations: List[Allocation]) -> Dict[str, Any]:
        """Check if allocations meet equity thresholds.

        Falsifies if: the returned dict reports ``equitable=True`` while
        either the variance or Gini strictly exceeds its threshold, or
        ``equitable=False`` while both are within bounds.
        falsifies_if: ``equitable`` disagrees with the threshold check on
        ``variance`` and ``gini``.
        """
        variance = self.calculate_variance(allocations)
        gini = self.calculate_gini(allocations)

        violations: List[Dict[str, Any]] = []

        if variance > self.variance_threshold:
            violations.append({
                "type": "variance_exceeded",
                "value": variance,
                "threshold": self.variance_threshold,
            })

        if gini > self.gini_threshold:
            violations.append({
                "type": "gini_exceeded",
                "value": gini,
                "threshold": self.gini_threshold,
            })

        if violations:
            self.violations.extend(violations)

        return {
            "equitable": len(violations) == 0,
            "variance": variance,
            "gini": gini,
            "violations": violations,
        }

    def get_equity_violations(self) -> List[Dict[str, Any]]:
        """Get all equity violations detected."""
        return self.violations
