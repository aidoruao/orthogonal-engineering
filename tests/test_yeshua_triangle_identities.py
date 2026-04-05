from axioms.yeshua_axioms import YESHUA_AXIOMS
from src.sal.adjoint_triple import AdjointTriple
from src.sal.yeshua_as_triangle_identities import (
    AXIOM_TO_SAL_TARGET,
    map_axiom_to_triangle_identity,
    verify_all_axioms_map,
)


def test_yeshua_axioms_map_to_identities():
    triple = AdjointTriple()
    for n in YESHUA_AXIOMS:
        mapping = map_axiom_to_triangle_identity(n, triple)
        assert mapping.target == AXIOM_TO_SAL_TARGET[n]
        assert mapping.is_valid


def test_verify_all_axioms_map():
    triple = AdjointTriple()
    result = verify_all_axioms_map(triple)
    assert result["count"] == 8
    assert result["all_valid"] is True
