from src.sal.cross_repo_adjunction import verify_cross_repo_adjunction


def test_cross_repo_adjunction_returns_structured_proof():
    result = verify_cross_repo_adjunction()
    proof = result["proof"]
    assert proof.domain_id == "CROSS_REPO"
    assert proof.counit_evidence.is_valid()
    assert proof.unit_evidence.is_valid()


def test_anti_nominalism_via_adjunction():
    result = verify_cross_repo_adjunction()
    missing = result["anti_nominalism_violations"]
    assert isinstance(missing, list)
    assert all(":" in item for item in missing)
