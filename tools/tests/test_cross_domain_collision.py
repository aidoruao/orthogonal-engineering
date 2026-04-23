"""Test suite for cross-domain invariant collision detector.

Phase 6 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fractions import Fraction

from tools.cross_domain_invariant_collision import (
    InvariantMetadata,
    InvariantCollision,
    scan_domain_invariants,
    detect_collisions,
    demonstrate_propagation,
    _extract_patterns,
)


class TestCrossDomainCollision:
    def test_extract_patterns(self):
        assert "greater_than" in _extract_patterns("x > 0")
        assert "less_than" in _extract_patterns("x < 1")
        assert "not_equal" in _extract_patterns("x != 0")
        assert "bounded_interval" in _extract_patterns("outside [0, 1]")
        assert "monotonicity" in _extract_patterns("not monotonic")

    def test_detect_standard_collision(self):
        invs = [
            InvariantMetadata("d_a", "check_x", "Bayes 1763", "x > 0"),
            InvariantMetadata("d_b", "check_y", "Bayes 1763", "y < 1"),
        ]
        collisions = detect_collisions(invs)
        assert len(collisions) == 1
        c = collisions[0]
        assert c.shared_root == "Bayes 1763"
        assert c.collision_type == "standard"
        assert c.propagation_risk == Fraction(3, 4)

    def test_detect_pattern_collision(self):
        invs = [
            InvariantMetadata("d_a", "check_x", "A 1900", "x > 0"),
            InvariantMetadata("d_b", "check_y", "B 1950", "y > 1"),
        ]
        collisions = detect_collisions(invs)
        assert len(collisions) == 1
        c = collisions[0]
        assert c.collision_type == "pattern"
        assert c.shared_root == "greater_than"

    def test_no_same_domain_collision(self):
        invs = [
            InvariantMetadata("d_a", "check_x", "S", "x > 0"),
            InvariantMetadata("d_a", "check_y", "S", "y > 1"),
        ]
        collisions = detect_collisions(invs)
        assert len(collisions) == 0

    def test_demonstrate_propagation(self):
        c = InvariantCollision(
            domain_a="d_a", check_a="check_x",
            domain_b="d_b", check_b="check_y",
            shared_root="Bayes 1763",
            collision_type="standard",
            propagation_risk=Fraction(3, 4),
        )
        proof = demonstrate_propagation(c)
        assert "d_a/check_x" in proof.conclusion
        assert "d_b/check_y" in proof.conclusion
        assert "Bayes 1763" in proof.conclusion

    def test_scan_real_domains(self):
        from tools.cross_domain_invariant_collision import scan_all_domains
        invariants = scan_all_domains()
        assert len(invariants) > 0
        domains = {inv.domain for inv in invariants}
        assert len(domains) > 0
        collisions = detect_collisions(invariants)
        # Collisions may exist; just verify the function runs
        assert isinstance(collisions, list)
