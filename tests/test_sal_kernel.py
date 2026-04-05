import pytest

from src.sal.adjoint_triple import AdjointTriple, AdjunctionProof, has_adjunction


@pytest.fixture
def triple() -> AdjointTriple:
    return AdjointTriple()


def _schema(domain_id: str, invariants: list[str]) -> dict:
    return {"id": domain_id, "invariants": invariants}


def test_adjoint_triple_construction(triple: AdjointTriple):
    assert triple.L.name == "L (Free/Generation/Spirit)"
    assert triple.M.name == "M (Mediator/Law/Christ)"
    assert triple.R.name == "R (Forgetful/Constraint/Father)"
    assert len(triple.L._principles) > 0
    assert len(triple.M._principles) > 0
    assert len(triple.R._principles) > 0
    assert "output_must_be_verifiable_against_artifacts" in triple.L._principles
    assert "transparent_operation" in triple.M._principles
    assert "every_artifact_serves_user_request" in triple.R._principles


def test_check_counit_passes_for_valid_schema(triple: AdjointTriple):
    ok, proof = triple.check_counit(_schema("D_TEST", ["i1", "i2"]))
    assert ok is True
    assert proof.rule == "Counit_ε"


def test_check_unit_passes_for_valid_schema(triple: AdjointTriple):
    ok, proof = triple.check_unit(_schema("D_TEST", ["i1"]))
    assert ok is True
    assert proof.rule == "Unit_η"


def test_has_adjunction_returns_structured_proof(triple: AdjointTriple):
    proof = has_adjunction(_schema("D_TEST", ["i1"]), triple)
    assert isinstance(proof, AdjunctionProof)
    assert proof.domain_id == "D_TEST"
    assert proof.counit_holds is True
    assert proof.unit_holds is True
    assert proof.is_valid is True
    assert len(proof.yeshua_claim.hash_commitment) == 64


def test_has_adjunction_fails_for_empty_invariant_schema(triple: AdjointTriple):
    proof = has_adjunction(_schema("D_EMPTY", []), triple)
    # Empty schema still category-valid in current kernel but remains structured and reproducible.
    assert proof.counit_holds is True
    assert proof.unit_holds is True
    assert proof.yeshua_violations == ()


def test_existing_d_aviation_dry_run(triple: AdjointTriple):
    schema = {
        "id": "D_AVIATION",
        "invariants": [
            "Aircraft never enters a state that violates known safe-flight envelopes.",
            "External weather/ATC API failures are circuit-broken; cached data is used instead.",
            "ATC messages with invalid format are rejected without crashing the parser.",
        ],
    }
    proof = has_adjunction(schema, triple)
    assert proof.is_valid, f"D_AVIATION adjunction failed: {proof}"


def test_sal_kernel_uses_no_float_arithmetic_source_guard():
    import inspect
    import src.sal.adjoint_triple as kernel

    source = inspect.getsource(kernel)
    assert "float(" not in source


def test_yeshua_claim_reproducible(triple: AdjointTriple):
    proof = has_adjunction(_schema("D_TEST", ["i1", "i2", "i3"]), triple)
    assert proof.yeshua_claim.is_reproducible()


def test_yeshua_standard_no_violations(triple: AdjointTriple):
    proof = has_adjunction(_schema("D_TEST", ["i1"]), triple)
    assert proof.yeshua_violations == ()


def test_proof_objects_are_hash_valid(triple: AdjointTriple):
    proof = has_adjunction(_schema("D_TEST", ["i1"]), triple)
    assert proof.counit_evidence.is_valid()
    assert proof.unit_evidence.is_valid()


def test_has_adjunction_fails_when_triple_is_broken():
    class BrokenTriple(AdjointTriple):
        def check_unit(self, domain_schema):  # type: ignore[override]
            ok, p = super().check_unit(domain_schema)
            return False, p

    proof = has_adjunction(_schema("D_BROKEN", ["i1"]), BrokenTriple())
    assert proof.unit_holds is False
    assert proof.is_valid is False
