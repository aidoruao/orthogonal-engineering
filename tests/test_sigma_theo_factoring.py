from src.sal.adjoint_triple import AdjointTriple
from src.sal.sigma_theo_factoring import (
    SIGMA_FACTORING_MAP,
    factor_sigma_through_triple,
    verify_factoring_coherence,
)


def test_sigma_theo_factoring_all_operators():
    triple = AdjointTriple()
    for operator, expected in SIGMA_FACTORING_MAP.items():
        result = factor_sigma_through_triple(operator, triple)
        assert result.component == expected
        assert result.is_valid


def test_factoring_coherence():
    triple = AdjointTriple()
    coherence = verify_factoring_coherence(triple)
    assert coherence["all_operators_factored"] is True
    assert coherence["adjunction_valid"] is True
    assert coherence["coherent"] is True
