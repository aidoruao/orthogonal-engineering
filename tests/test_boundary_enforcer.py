"""
Tests for boundary_enforcer — YESHUA STANDARD domain-actualization constraints.

Covers:
  - external_claim tagging and propagation
  - validate_input_schema / validate_output_schema contract failures
  - deterministic halting in a representative onboarding workflow

Author: Orthogonal Engineering
Version: 1.0.0
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.boundary_enforcer import (
    ContractViolationError,
    ExternalClaimError,
    assert_not_external_claim,
    is_external_claim,
    tag_external_claim,
    validate_input_schema,
    validate_output_schema,
)
from oe_ifm.halt_condition import BoundedCounter, HaltConditionError


# ---------------------------------------------------------------------------
# external_claim tagging
# ---------------------------------------------------------------------------


def test_tag_external_claim_sets_flag():
    """`tag_external_claim` returns a dict with external_claim=True."""
    result = tag_external_claim("some output")
    assert result["external_claim"] is True
    assert result["value"] == "some output"


def test_tag_external_claim_includes_source():
    """`tag_external_claim` includes the optional source field."""
    result = tag_external_claim(42, source="external-llm")
    assert result["source"] == "external-llm"
    assert result["external_claim"] is True


def test_tag_external_claim_without_source():
    """`tag_external_claim` without source omits the source key."""
    result = tag_external_claim("data")
    assert "source" not in result


def test_is_external_claim_true():
    """`is_external_claim` returns True for tagged objects."""
    tagged = tag_external_claim({"proof": "nope"})
    assert is_external_claim(tagged) is True


def test_is_external_claim_false_for_plain_dict():
    """`is_external_claim` returns False for plain dicts."""
    # TODO: Expand test_is_external_claim_false_for_plain_dict() - stub detected by Yeshua Agent
    assert is_external_claim({"key": "value"}) is False


def test_is_external_claim_false_for_non_dict():
    """`is_external_claim` returns False for non-dict types."""
    assert is_external_claim("raw string") is False
    assert is_external_claim(None) is False
    assert is_external_claim(123) is False


def test_assert_not_external_claim_passes_for_plain():
    """`assert_not_external_claim` does not raise for non-tagged objects."""
    # TODO: Expand test_assert_not_external_claim_passes_for_plain() - stub detected by Yeshua Agent
    assert_not_external_claim({"proof": "valid"})  # should not raise


def test_assert_not_external_claim_raises_for_tagged():
    """`assert_not_external_claim` raises ExternalClaimError for tagged objects."""
    tagged = tag_external_claim("untrusted output")
    with pytest.raises(ExternalClaimError):
        assert_not_external_claim(tagged)


def test_assert_not_external_claim_includes_context():
    """`assert_not_external_claim` error message includes context string."""
    tagged = tag_external_claim("bad")
    with pytest.raises(ExternalClaimError, match="my-context"):
        assert_not_external_claim(tagged, context="my-context")


def test_external_claim_not_usable_as_proof():
    """External claims must not silently pass through proof-consumption sites."""
    external = tag_external_claim({"result": "fabricated"})
    # Simulated proof-consumption site
    def consume_proof(obj):
        assert_not_external_claim(obj, context="consume_proof")
        return obj["result"]

    with pytest.raises(ExternalClaimError):
        consume_proof(external)


# ---------------------------------------------------------------------------
# validate_input_schema
# ---------------------------------------------------------------------------


def test_validate_input_schema_passes_valid_kwargs():
    """validate_input_schema allows valid keyword arguments."""
    schema = {"type": "dict", "required": ["name"], "properties": {"name": {"type": "str"}}}

    @validate_input_schema(schema)
    def greet(*, name):
        return f"Hello, {name}"

    assert greet(name="Alice") == "Hello, Alice"


def test_validate_input_schema_raises_on_missing_required_key():
    """validate_input_schema raises ContractViolationError for missing required kwarg."""
    schema = {"type": "dict", "required": ["name"]}

    @validate_input_schema(schema)
    def greet(*, name=None):
        return "Hello"

    with pytest.raises(ContractViolationError) as exc_info:
        greet()  # name not provided in kwargs

    assert exc_info.value.direction == "input"
    assert "name" in str(exc_info.value)


def test_validate_input_schema_raises_on_wrong_type():
    """validate_input_schema raises ContractViolationError for wrong kwarg type."""
    schema = {
        "type": "dict",
        "properties": {"count": {"type": "int"}},
    }

    @validate_input_schema(schema)
    def process(*, count):
        return count

    with pytest.raises(ContractViolationError) as exc_info:
        process(count="not-an-int")

    assert exc_info.value.direction == "input"


def test_validate_input_schema_aborts_before_execution():
    """validate_input_schema must abort before the function body runs."""
    executed = []

    schema = {"type": "dict", "required": ["x"]}

    @validate_input_schema(schema)
    def side_effect(*, x=None):
        executed.append(True)
        return x

    with pytest.raises(ContractViolationError):
        side_effect()  # x not provided

    assert executed == [], "Function body must not execute on contract failure"


def test_validate_input_schema_violation_record():
    """ContractViolationError.record is a deterministic violation dict."""
    schema = {"type": "dict", "required": ["field"]}

    @validate_input_schema(schema)
    def fn(*, field=None):
        pass

    with pytest.raises(ContractViolationError) as exc_info:
        fn()

    record = exc_info.value.record
    assert record["violation"] == "contract"
    assert record["direction"] == "input"
    assert "timestamp_utc" in record
    assert isinstance(record["errors"], list) and len(record["errors"]) > 0


# ---------------------------------------------------------------------------
# validate_output_schema
# ---------------------------------------------------------------------------


def test_validate_output_schema_passes_valid_output():
    """validate_output_schema allows valid return values."""
    schema = {"type": "dict", "required": ["status"]}

    @validate_output_schema(schema)
    def run():
        return {"status": "ok"}

    assert run()["status"] == "ok"


def test_validate_output_schema_raises_on_wrong_return_type():
    """validate_output_schema raises ContractViolationError for wrong return type."""
    schema = {"type": "dict"}

    @validate_output_schema(schema)
    def run():
        return "not-a-dict"

    with pytest.raises(ContractViolationError) as exc_info:
        run()

    assert exc_info.value.direction == "output"


def test_validate_output_schema_raises_on_missing_required_key():
    """validate_output_schema raises ContractViolationError for missing key in output."""
    schema = {"type": "dict", "required": ["status", "result"]}

    @validate_output_schema(schema)
    def run():
        return {"status": "ok"}  # missing "result"

    with pytest.raises(ContractViolationError) as exc_info:
        run()

    assert "result" in str(exc_info.value)


def test_validate_output_schema_violation_record():
    """ContractViolationError from output schema has correct record fields."""
    schema = {"type": "int"}

    @validate_output_schema(schema)
    def compute():
        return "string-not-int"

    with pytest.raises(ContractViolationError) as exc_info:
        compute()

    record = exc_info.value.record
    assert record["violation"] == "contract"
    assert record["direction"] == "output"
    assert "compute" in record["function"]


# ---------------------------------------------------------------------------
# Deterministic halting — representative onboarding workflow
# ---------------------------------------------------------------------------


def test_bounded_onboarding_workflow_halts_deterministically():
    """
    A simulated onboarding audit loop terminates deterministically using
    BoundedCounter when the artifact count exceeds the configured ceiling.
    """
    counter = BoundedCounter(max_steps=5)

    # Simulate an audit loop over 10 "artifacts"
    artifacts = list(range(10))

    with pytest.raises(HaltConditionError) as exc_info:
        for artifact in artifacts:
            counter.step()

    assert exc_info.value.limit_type == "steps"
    assert exc_info.value.current > exc_info.value.maximum


def test_bounded_onboarding_workflow_succeeds_within_limit():
    """
    A simulated onboarding audit loop completes successfully when the artifact
    count is within the configured ceiling.
    """
    counter = BoundedCounter(max_steps=20)
    results = []

    for artifact in range(10):
        counter.step()
        results.append(artifact)

    assert len(results) == 10
    assert counter.steps == 10


def test_stage_2_validate_structure_is_bounded(tmp_path):
    """
    CheckOnboardingPipeline.stage_2_validate_structure uses a BoundedCounter
    and raises HaltConditionError when the artifact count exceeds the ceiling.
    """
    import importlib
    import unittest.mock as mock

    from toolkit.oe.onboarding_check import (
        CheckOnboardingPipeline,
        CandidateArtifact,
        ArtifactType,
        _MAX_AUDIT_ARTIFACTS,
    )

    pipeline = CheckOnboardingPipeline(str(tmp_path))

    # Build a list slightly over the limit by patching the constant
    small_limit = 3
    artifacts = [
        CandidateArtifact(
            path=f"file_{i}.md",
            artifact_type=ArtifactType.ONBOARDING_FILE,
            size_bytes=100,
        )
        for i in range(small_limit + 1)
    ]

    # Patch the module-level constant and BoundedCounter max_steps
    with mock.patch(
        "toolkit.oe.onboarding_check._MAX_AUDIT_ARTIFACTS", small_limit
    ):
        with pytest.raises(HaltConditionError):
            pipeline.stage_2_validate_structure(artifacts)
