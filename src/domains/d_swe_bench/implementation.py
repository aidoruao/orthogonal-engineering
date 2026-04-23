"""D_SWE_BENCH implementation — SWE-bench Excedent

Layer: 3 (Regulatory/Research)
CardinalStrength: PREDICATIVE

Software engineering benchmark evaluation, patch correctness, minimality.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SWEBenchInstance:
    """Single SWE-bench instance evaluation."""
    repo_id: str
    issue_id: str
    patch_correctness: Fraction        # 0 or 1
    test_pass_rate: Fraction           # tests passing after patch
    files_modified: int
    lines_changed: int
    resolution_type: str               # "bug_fix" | "feature" | "refactor"


@dataclass(frozen=True)
class SWEBenchScore:
    """Aggregate SWE-bench score for a model."""
    model_id: str
    split: str                         # "verified" | "lite" | "pro"
    instances_resolved: int
    instances_total: int
    resolve_rate: Fraction
    false_positive_rate: Fraction
    avg_patch_size: Fraction
