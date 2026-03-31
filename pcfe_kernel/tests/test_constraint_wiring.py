"""
pcfe_kernel/tests/test_constraint_wiring.py

Tests for the wired Principle._check_constraint() (the stub fix from §3.2).
Verifies that constraint verification is actually performed via hash
correspondence rather than silently returning None.
"""

import hashlib

import pytest

from pcfe_kernel.principles import (
    Artifact,
    Principle,
    ALL_PRINCIPLES,
    ATOMICITY,
    DETERMINISM,
    FRACTAL_INTEGRITY,
    PEANO_ARITHMETIC,
    ANTI_NOMINALISM,
    verify_artifact,
)


# ---------------------------------------------------------------------------
# Artifact construction
# ---------------------------------------------------------------------------

class TestArtifactConstruction:
    def test_artifact_auto_hash(self):
        artifact = Artifact(content="hello", constraints=[])
        expected = hashlib.sha256(b"hello").hexdigest()
        assert artifact.hash == expected

    def test_artifact_explicit_hash(self):
        artifact = Artifact(content="hello", constraints=[], hash="custom_hash")
        assert artifact.hash == "custom_hash"

    def test_artifact_constraints_list(self):
        artifact = Artifact(content="x", constraints=["C1", "C2"])
        assert "C1" in artifact.constraints
        assert "C2" in artifact.constraints


# ---------------------------------------------------------------------------
# _check_constraint — the stub fix
# ---------------------------------------------------------------------------

class TestCheckConstraintWired:
    def test_check_constraint_returns_bool_not_none(self):
        p = Principle(name="P", description="d", constraints=["C1"])
        artifact = Artifact(content="x", constraints=["C1"])
        result = p._check_constraint("C1", artifact)
        assert result is not None, "_check_constraint must return bool, not None"
        assert isinstance(result, bool)

    def test_check_constraint_true_when_constraint_present(self):
        p = Principle(name="P", description="d", constraints=["C1"])
        artifact = Artifact(content="x", constraints=["C1", "C2"])
        assert p._check_constraint("C1", artifact) is True

    def test_check_constraint_false_when_constraint_absent(self):
        p = Principle(name="P", description="d", constraints=["C1"])
        artifact = Artifact(content="x", constraints=["C2"])
        assert p._check_constraint("C1", artifact) is False

    def test_check_constraint_false_when_artifact_has_no_hash(self):
        p = Principle(name="P", description="d", constraints=["C1"])

        class NoHash:
            constraints = ["C1"]

        assert p._check_constraint("C1", NoHash()) is False

    def test_check_constraint_false_when_artifact_has_no_constraints(self):
        p = Principle(name="P", description="d", constraints=["C1"])

        class NoConstraints:
            hash = "abc123"

        assert p._check_constraint("C1", NoConstraints()) is False

    def test_check_constraint_false_for_plain_dict(self):
        p = Principle(name="P", description="d", constraints=["C1"])
        assert p._check_constraint("C1", {"hash": "x", "constraints": ["C1"]}) is False


# ---------------------------------------------------------------------------
# Principle.verify()
# ---------------------------------------------------------------------------

class TestPrincipleVerify:
    def test_verify_true_when_all_constraints_satisfied(self):
        p = Principle(name="P", description="d", constraints=["C1", "C2"])
        artifact = Artifact(content="x", constraints=["C1", "C2", "C3"])
        assert p.verify(artifact) is True

    def test_verify_false_when_any_constraint_missing(self):
        p = Principle(name="P", description="d", constraints=["C1", "C2"])
        artifact = Artifact(content="x", constraints=["C1"])
        assert p.verify(artifact) is False

    def test_verify_true_for_no_constraints(self):
        p = Principle(name="P", description="d", constraints=[])
        artifact = Artifact(content="x", constraints=[])
        assert p.verify(artifact) is True


# ---------------------------------------------------------------------------
# Built-in principles
# ---------------------------------------------------------------------------

class TestBuiltinPrinciples:
    def test_five_builtin_principles_exist(self):
        assert len(ALL_PRINCIPLES) == 5

    def test_builtin_principle_names(self):
        names = {p.name for p in ALL_PRINCIPLES}
        expected = {"ATOMICITY", "DETERMINISM", "FRACTAL_INTEGRITY", "PEANO_ARITHMETIC", "ANTI_NOMINALISM"}
        assert names == expected

    def test_atomicity_has_constraints(self):
        assert len(ATOMICITY.constraints) > 0

    def test_determinism_has_constraints(self):
        assert len(DETERMINISM.constraints) > 0


# ---------------------------------------------------------------------------
# verify_artifact helper
# ---------------------------------------------------------------------------

class TestVerifyArtifact:
    def test_verify_artifact_passes_with_all_constraints(self):
        all_constraints = [c for p in ALL_PRINCIPLES for c in p.constraints]
        artifact = Artifact(content="full", constraints=all_constraints)
        assert verify_artifact(artifact) is True

    def test_verify_artifact_fails_with_missing_constraints(self):
        artifact = Artifact(content="empty", constraints=[])
        assert verify_artifact(artifact) is False

    def test_verify_artifact_custom_principles(self):
        p = Principle(name="CUSTOM", description="d", constraints=["MY_RULE"])
        artifact = Artifact(content="x", constraints=["MY_RULE"])
        assert verify_artifact(artifact, principles=[p]) is True

    def test_verify_artifact_no_principles_passes(self):
        artifact = Artifact(content="x", constraints=[])
        assert verify_artifact(artifact, principles=[]) is True
