#!/usr/bin/env python3
"""
STATISTICAL VALIDATION MODULE - P-Value Calculations for Orthogonal Engineering

Version: 1.0.0
Date: 2026-01-24
Purpose: Provide reproducible p-value calculations for statistical claims
Requirements: All claims of p < 0.0001 must be calculable and verifiable

Key Features:
1. Multiple statistical tests (chi-square, binomial, permutation)
2. Confidence interval calculations
3. Effect size measurements
4. Reproducible random seed control
5. Comprehensive reporting
"""

import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class StatisticalTest(Enum):
    """Types of statistical tests available"""

    CHI_SQUARE = "chi_square"
    BINOMIAL = "binomial"
    PERMUTATION = "permutation"
    FISHER_EXACT = "fisher_exact"
    T_TEST = "t_test"


class SignificanceLevel(Enum):
    """Standard significance levels"""

    P_001 = 0.001
    P_005 = 0.005
    P_01 = 0.01
    P_05 = 0.05


@dataclass
class StatisticalResult:
    """Complete statistical test results"""

    test_type: StatisticalTest
    null_hypothesis: str
    alternative_hypothesis: str
    test_statistic: float
    p_value: float
    degrees_of_freedom: Optional[int] = None
    effect_size: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    sample_size: Optional[int] = None
    power: Optional[float] = None
    is_significant: bool = False
    significance_level: float = 0.05
    assumptions_met: bool = False
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        self.is_significant = self.p_value < self.significance_level

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result["test_type"] = self.test_type.value
        result["significance_level"] = self.significance_level
        if self.confidence_interval:
            result["confidence_interval"] = list(self.confidence_interval)
        return result


class StatisticalValidator:
    """
    Main statistical validation class providing p-value calculations
    for Orthogonal Engineering claims.
    """

    def __init__(self, random_seed: int = 42):
        """
        Initialize validator with reproducible random seed.

        Args:
            random_seed: Seed for reproducible random number generation
        """
        self.random_seed = random_seed
        random.seed(random_seed)
        self.results_log = []

    def chi_square_test(
        self,
        observed: List[int],
        expected: List[float],
        null_hypothesis: str = "No difference from expected",
    ) -> StatisticalResult:
        """
        Perform chi-square goodness-of-fit test.

        Args:
            observed: Observed frequencies
            expected: Expected frequencies under null hypothesis
            null_hypothesis: Description of null hypothesis

        Returns:
            StatisticalResult with chi-square statistic and p-value
        """
        # Validate inputs
        if len(observed) != len(expected):
            raise ValueError("Observed and expected must have same length")

        if any(e == 0 for e in expected):
            # Handle zero expected frequencies gracefully
            # Replace zeros with small epsilon to allow calculation
            expected = [max(e, 1e-10) for e in expected]

        # Calculate chi-square statistic
        chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected))

        # Degrees of freedom
        df = len(observed) - 1

        # Calculate p-value using chi-square distribution approximation
        p_value = self._chi2_p_value(chi2, df)

        # Calculate effect size (Cramer's V for goodness-of-fit)
        total = sum(observed)
        effect_size = (
            math.sqrt(chi2 / (total * (len(observed) - 1))) if total > 0 else 0
        )

        result = StatisticalResult(
            test_type=StatisticalTest.CHI_SQUARE,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis="Distribution differs from expected",
            test_statistic=chi2,
            p_value=p_value,
            degrees_of_freedom=df,
            effect_size=effect_size,
            sample_size=total,
            assumptions_met=self._check_chi_square_assumptions(observed, expected),
        )

        self.results_log.append(result)
        return result

    def binomial_test(
        self,
        successes: int,
        trials: int,
        expected_prob: float = 0.5,
        null_hypothesis: str = "Success probability equals expected",
    ) -> StatisticalResult:
        """
        Perform exact binomial test.

        Args:
            successes: Number of successes
            trials: Total number of trials
            expected_prob: Expected probability under null hypothesis
            null_hypothesis: Description of null hypothesis

        Returns:
            StatisticalResult with exact binomial p-value
        """
        if not 0 <= expected_prob <= 1:
            raise ValueError("Expected probability must be between 0 and 1")

        if successes > trials or successes < 0:
            raise ValueError("Invalid successes/trials values")

        # Calculate exact binomial p-value (two-tailed)
        p_value = self._exact_binomial_p_value(successes, trials, expected_prob)

        # Calculate confidence interval for success probability
        ci = self._binomial_confidence_interval(successes, trials)

        # Calculate effect size (difference from expected)
        observed_prob = successes / trials if trials > 0 else 0
        effect_size = observed_prob - expected_prob

        result = StatisticalResult(
            test_type=StatisticalTest.BINOMIAL,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis="Success probability differs from expected",
            test_statistic=successes,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=ci,
            sample_size=trials,
            assumptions_met=True,  # Binomial test has minimal assumptions
        )

        self.results_log.append(result)
        return result

    def permutation_test(
        self,
        group_a: List[float],
        group_b: List[float],
        test_statistic_func: callable = None,
        null_hypothesis: str = "Groups have same distribution",
        n_permutations: int = 10000,
    ) -> StatisticalResult:
        """
        Perform permutation test (non-parametric).

        Args:
            group_a: First group of observations
            group_b: Second group of observations
            test_statistic_func: Function to compute test statistic (default: mean difference)
            null_hypothesis: Description of null hypothesis
            n_permutations: Number of permutations to run

        Returns:
            StatisticalResult with permutation p-value
        """
        if test_statistic_func is None:
            test_statistic_func = lambda a, b: statistics.mean(a) - statistics.mean(b)

        # Calculate observed test statistic
        observed_stat = test_statistic_func(group_a, group_b)

        # Combine groups for permutation
        combined = group_a + group_b
        n_a = len(group_a)

        # Generate permutation distribution
        perm_stats = []
        for _ in range(n_permutations):
            # Randomly permute combined data
            permuted = random.sample(combined, len(combined))
            perm_a = permuted[:n_a]
            perm_b = permuted[n_a:]
            perm_stat = test_statistic_func(perm_a, perm_b)
            perm_stats.append(perm_stat)

        # Calculate p-value (two-tailed)
        abs_observed = abs(observed_stat)
        extreme_count = sum(1 for stat in perm_stats if abs(stat) >= abs_observed)
        p_value = (extreme_count + 1) / (n_permutations + 1)  # +1 for observed

        # Calculate effect size (Cohen's d)
        effect_size = self._cohens_d(group_a, group_b)

        # Calculate confidence interval via bootstrap
        ci = self._bootstrap_confidence_interval(group_a, group_b, test_statistic_func)

        result = StatisticalResult(
            test_type=StatisticalTest.PERMUTATION,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis="Groups differ",
            test_statistic=observed_stat,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=ci,
            sample_size=len(group_a) + len(group_b),
            assumptions_met=True,  # Permutation test is non-parametric
        )

        self.results_log.append(result)
        return result

    def validate_density_claim(
        self,
        observed_density: float,
        total_turns: int,
        baseline_density: float = 0.05,
        claim_p_value: float = 0.0001,
    ) -> Dict:
        """
        Validate density claims like "p < 0.0001" for invariant density.

        Args:
            observed_density: Observed invariant density (e.g., 0.453 for 45.3%)
            total_turns: Total number of conversation turns
            baseline_density: Expected density under null hypothesis (default: 5%)
            claim_p_value: Claimed p-value (e.g., 0.0001)

        Returns:
            Dictionary with validation results
        """
        # Calculate observed successes
        observed_successes = int(round(observed_density * total_turns))

        # Run binomial test
        binomial_result = self.binomial_test(
            successes=observed_successes,
            trials=total_turns,
            expected_prob=baseline_density,
            null_hypothesis=f"Invariant density equals baseline ({baseline_density:.1%})",
        )

        # Run chi-square test for comparison
        observed_counts = [observed_successes, total_turns - observed_successes]
        expected_counts = [
            baseline_density * total_turns,
            (1 - baseline_density) * total_turns,
        ]

        # Only run chi-square if we have non-zero expected counts
        chi2_result = None
        if all(e > 0 for e in expected_counts):
            chi2_result = self.chi_square_test(
                observed=observed_counts,
                expected=expected_counts,
                null_hypothesis=f"Distribution matches baseline ({baseline_density:.1%})",
            )

        # Check if claim is supported
        claim_supported = binomial_result.p_value < claim_p_value

        # Calculate power
        power = self._calculate_power(
            n=total_turns, p0=baseline_density, p1=observed_density, alpha=claim_p_value
        )

        validation_result = {
            "validation_date": datetime.now().isoformat(),
            "claim": {
                "observed_density": observed_density,
                "total_turns": total_turns,
                "claimed_p_value": claim_p_value,
                "baseline_density": baseline_density,
            },
            "results": {
                "binomial_test": binomial_result.to_dict(),
                "chi_square_test": chi2_result.to_dict() if chi2_result else None,
            },
            "validation": {
                "claim_supported": claim_supported,
                "actual_p_value": binomial_result.p_value,
                "power": power,
                "required_sample_size": self._required_sample_size(
                    p0=baseline_density,
                    p1=observed_density,
                    alpha=claim_p_value,
                    power=0.8,
                ),
            },
            "interpretation": self._generate_interpretation(
                observed_density,
                baseline_density,
                binomial_result.p_value,
                claim_p_value,
                claim_supported,
            ),
        }

        return validation_result

    def _chi2_p_value(self, chi2: float, df: int) -> float:
        """Calculate p-value for chi-square statistic using approximation."""
        # Simple approximation for chi-square p-value
        # In production, use scipy.stats.chi2.sf or similar
        import math

        if df <= 0:
            return 1.0

        # Approximation for large df
        if df > 100:
            # Normal approximation
            z = (chi2 - df) / math.sqrt(2 * df)
            return 2 * (1 - self._normal_cdf(abs(z)))

        # Simple gamma function approximation for small df
        # This is a simplified version - real implementation would use proper chi2 distribution
        k = df / 2
        x = chi2 / 2

        # Upper incomplete gamma approximation
        p_value = self._upper_incomplete_gamma(k, x)

        return min(max(p_value, 0), 1)

    def _exact_binomial_p_value(self, k: int, n: int, p: float) -> float:
        """Calculate exact two-tailed binomial p-value."""
        # Calculate probability of observing k or more extreme results
        prob = 0.0
        for i in range(n + 1):
            # Probability of exactly i successes
            prob_i = math.comb(n, i) * (p**i) * ((1 - p) ** (n - i))

            # Check if this result is as or more extreme than observed
            if abs(i - n * p) >= abs(k - n * p):
                prob += prob_i

        return prob

    def _binomial_confidence_interval(
        self, successes: int, trials: int, confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate Wilson score interval for binomial proportion."""
        if trials == 0:
            return (0.0, 0.0)

        p = successes / trials
        z = self._z_score(confidence)

        denominator = 1 + z**2 / trials
        centre_adjusted_probability = p + z**2 / (2 * trials)
        adjusted_standard_deviation = math.sqrt(
            (p * (1 - p) + z**2 / (4 * trials)) / trials
        )

        lower_bound = (
            centre_adjusted_probability - z * adjusted_standard_deviation
        ) / denominator

        upper_bound = (
            centre_adjusted_probability + z * adjusted_standard_deviation
        ) / denominator

        return (max(0, lower_bound), min(1, upper_bound))

    def _cohens_d(self, group_a: List[float], group_b: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        if not group_a or not group_b:
            return 0.0

        mean_a = statistics.mean(group_a)
        mean_b = statistics.mean(group_b)

        var_a = statistics.variance(group_a) if len(group_a) > 1 else 0
        var_b = statistics.variance(group_b) if len(group_b) > 1 else 0

        pooled_sd = math.sqrt(
            ((len(group_a) - 1) * var_a + (len(group_b) - 1) * var_b)
            / (len(group_a) + len(group_b) - 2)
        )

        if pooled_sd == 0:
            return 0.0

        return (mean_a - mean_b) / pooled_sd

    def _bootstrap_confidence_interval(
        self,
        group_a: List[float],
        group_b: List[float],
        statistic_func: callable,
        n_bootstrap: int = 1000,
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval."""
        combined = group_a + group_b
        n_a = len(group_a)

        bootstrap_stats = []
        for _ in range(n_bootstrap):
            # Sample with replacement
            sample = random.choices(combined, k=len(combined))
            sample_a = sample[:n_a]
            sample_b = sample[n_a:]
            bootstrap_stats.append(statistic_func(sample_a, sample_b))

        alpha = 1 - confidence
        lower = statistics.quantiles(bootstrap_stats, n=100)[int(alpha / 2 * 100) - 1]
        upper = statistics.quantiles(bootstrap_stats, n=100)[
            int((1 - alpha / 2) * 100) - 1
        ]

        return (lower, upper)

    def _calculate_power(
        self, n: int, p0: float, p1: float, alpha: float = 0.05
    ) -> float:
        """Calculate statistical power for binomial test."""
        # Handle edge cases
        if n <= 0:
            return 0.0

        if p0 <= 0 or p0 >= 1 or p1 <= 0 or p1 >= 1:
            return 0.0

        # Normal approximation for power calculation
        z_alpha = self._z_score(1 - alpha / 2)  # Two-tailed

        se0 = math.sqrt(p0 * (1 - p0) / n)
        se1 = math.sqrt(p1 * (1 - p1) / n)

        # Non-centrality parameter
        if se0 == 0:
            return 0.0
        d = (p1 - p0) / se0

        # Power using normal approximation
        power = 1 - self._normal_cdf(z_alpha - d) + self._normal_cdf(-z_alpha - d)

        return max(0, min(1, power))

    def _required_sample_size(
        self, p0: float, p1: float, alpha: float = 0.05, power: float = 0.8
    ) -> int:
        """Calculate required sample size for binomial test."""
        z_alpha = self._z_score(1 - alpha / 2)  # Two-tailed
        z_beta = self._z_score(power)

        p_bar = (p0 + p1) / 2

        numerator = (
            z_alpha * math.sqrt(2 * p_bar * (1 - p_bar))
            + z_beta * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))
        ) ** 2
        denominator = (p1 - p0) ** 2

        return math.ceil(numerator / denominator)

    def _check_chi_square_assumptions(
        self, observed: List[int], expected: List[float]
    ) -> bool:
        """Check chi-square test assumptions."""
        # All expected frequencies should be >= 5
        if any(e < 5 for e in expected):
            return False

        # No zero expected frequencies
        if any(e == 0 for e in expected):
            return False

        return True

    def _z_score(self, probability: float) -> float:
        """Convert probability to z-score using approximation."""
        # Simple approximation of inverse normal CDF
        # In production, use scipy.stats.norm.ppf or similar
        if probability <= 0 or probability >= 1:
            return float("inf")

        # Approximation from Peter John Acklam
        a1 = -39.6968302866538
        a2 = 220.946098424521
        a3 = -275.928510446969
        a4 = 138.357751867269
        a5 = -30.6647980661472
        a6 = 2.50662827745924

        b1 = -54.4760987982241
        b2 = 161.585836858041
        b3 = -155.698979859887
        b4 = 66.8013118877197
        b5 = -13.2806815528857

        c1 = -7.78489400243029e-03
        c2 = -0.322396458041136
        c3 = -2.40075827716184
        c4 = -2.54973253934373
        c5 = 4.37466414146497
        c6 = 2.93816398269878

        d1 = 7.78469570904146e-03
        d2 = 0.32246712907004
        d3 = 2.445134137143
        d4 = 3.75440866190742

        p_low = 0.02425
        p_high = 1 - p_low

        if probability < p_low:
            q = math.sqrt(-2 * math.log(probability))
            return (((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / (
                (((d1 * q + d2) * q + d3) * q + d4) * q + 1
            )
        elif probability <= p_high:
            q = probability - 0.5
            r = q * q
            return (
                (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6)
                * q
                / (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1)
            )
        else:
            q = math.sqrt(-2 * math.log(1 - probability))
            return -(((((c1 * q + c2) * q + c3) * q + c4) * q + c5) * q + c6) / (
                (((d1 * q + d2) * q + d3) * q + d4) * q + 1
            )

    def _normal_cdf(self, x: float) -> float:
        """Calculate normal CDF using approximation."""
        # Approximation from Abramowitz and Stegun
        t = 1 / (1 + 0.2316419 * abs(x))
        d = 0.3989423 * math.exp(-x * x / 2)
        prob = (
            d
            * t
            * (
                0.3193815
                + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))
            )
        )

        if x > 0:
            return 1 - prob
        else:
            return prob

    def _upper_incomplete_gamma(self, s: float, x: float) -> float:
        """Approximation of upper incomplete gamma function."""
        # Simple approximation for chi-square p-value calculation
        if x <= 0:
            return 1.0

        # For small x, use series expansion
        if x < s + 1:
            return self._lower_incomplete_gamma_series(s, x)
        else:
            # Use continued fraction for large x
            return self._upper_incomplete_gamma_cf(s, x)

    def _lower_incomplete_gamma_series(self, s: float, x: float) -> float:
        """Series expansion for lower incomplete gamma."""
        term = 1.0 / s
        total = term

        for n in range(1, 100):
            term *= x / (s + n)
            total += term
            if abs(term) < 1e-10:
                break

        return total * (x**s) * math.exp(-x)

    def _upper_incomplete_gamma_cf(self, s: float, x: float) -> float:
        """Continued fraction for upper incomplete gamma."""
        # Lentz's algorithm for continued fraction
        tiny = 1e-30
        c = 1.0
        d = 1.0 / (x - s + 1.0)
        if d == 0:
            d = tiny
        h = d

        for i in range(1, 100):
            a = -i * (i - s)
            b = x - s + (2 * i + 1)
            d = 1.0 / (a * d + b)
            if d == 0:
                d = tiny
            c = b + a / c
            if c == 0:
                c = tiny
            h *= d * c
            if abs(d * c - 1) < 1e-10:
                break

        return h * (x**s) * math.exp(-x)

    def _generate_interpretation(
        self,
        observed: float,
        expected: float,
        p_value: float,
        claim_p: float,
        supported: bool,
    ) -> str:
        """Generate human-readable interpretation of results."""
        if supported:
            return (
                f"The claim of p < {claim_p:.4f} is SUPPORTED. "
                f"Observed density ({observed:.1%}) significantly exceeds "
                f"baseline ({expected:.1%}) with p = {p_value:.6f}."
            )
        else:
            return (
                f"The claim of p < {claim_p:.4f} is NOT SUPPORTED. "
                f"Observed density ({observed:.1%}) does not significantly "
                f"exceed baseline ({expected:.1%}) with p = {p_value:.6f}."
            )

    def save_results(self, results: Dict, output_path: Path):
        """Save validation results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {output_path}")

    def print_summary(self, results: Dict):
        """Print human-readable summary of validation results."""
        print("\n" + "=" * 60)
        print("STATISTICAL VALIDATION SUMMARY")
        print("=" * 60)

        claim = results["claim"]
        validation = results["validation"]

        print(f"\nClaim: {claim['observed_density']:.1%} invariant density")
        print(f"Sample size: {claim['total_turns']:,} turns")
        print(f"Baseline: {claim['baseline_density']:.1%}")
        print(f"Claimed p-value: < {claim['claimed_p_value']:.4f}")

        print(f"\nActual p-value: {validation['actual_p_value']:.6f}")
        print(
            f"Claim supported: {'✅ YES' if validation['claim_supported'] else '❌ NO'}"
        )
        print(f"Statistical power: {validation['power']:.1%}")
        print(f"Required sample size: {validation['required_sample_size']:,}")

        print(f"\n{results['interpretation']}")


def main():
    """Command-line interface for statistical validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Statistical validation for Orthogonal Engineering claims"
    )

    parser.add_argument(
        "--density",
        "-d",
        type=float,
        required=True,
        help="Observed invariant density (e.g., 0.453 for 45.3%%)",
    )
    parser.add_argument(
        "--turns",
        "-t",
        type=int,
        required=True,
        help="Total number of conversation turns",
    )
    parser.add_argument(
        "--baseline",
        "-b",
        type=float,
        default=0.05,
        help="Baseline density under null hypothesis (default: 0.05)",
    )
    parser.add_argument(
        "--claim-p",
        "-p",
        type=float,
        default=0.0001,
        help="Claimed p-value threshold (default: 0.0001)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default="./validation_results.json",
        help="Output file path (default: ./validation_results.json)",
    )
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    # Validate inputs
    if not 0 <= args.density <= 1:
        print("Error: Density must be between 0 and 1")
        return 1

    if args.turns <= 0:
        print("Error: Number of turns must be positive")
        return 1

    if not 0 <= args.baseline <= 1:
        print("Error: Baseline must be between 0 and 1")
        return 1

    if not 0 < args.claim_p < 1:
        print("Error: Claim p-value must be between 0 and 1")
        return 1

    # Run validation
    print("=" * 60)
    print("ORTHOGONAL ENGINEERING - STATISTICAL VALIDATION")
    print("=" * 60)

    validator = StatisticalValidator(random_seed=args.seed)

    print(f"\nValidating claim: p < {args.claim_p:.4f}")
    print(f"Observed density: {args.density:.1%}")
    print(f"Sample size: {args.turns:,} turns")
    print(f"Baseline: {args.baseline:.1%}")

    results = validator.validate_density_claim(
        observed_density=args.density,
        total_turns=args.turns,
        baseline_density=args.baseline,
        claim_p_value=args.claim_p,
    )

    # Print summary
    validator.print_summary(results)

    # Save results
    validator.save_results(results, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
