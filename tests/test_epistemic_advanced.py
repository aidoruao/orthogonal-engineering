#!/usr/bin/env python3
"""Tests for PR #84 advanced epistemic logic helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.epistemic_logic import (
    KripkeModel,
    ParaconsistentTruthValue,
    construct_gettier_counterexample,
    evaluate_distributed_knowledge,
    evaluate_jtb,
    evaluate_knowledge,
    evaluate_paraconsistent,
    public_announcement,
    test_kk_principle,
)
from axioms.logic import ProofObject


def test_epistemic_advanced_suite():
    failing_kk_model = KripkeModel(
        worlds={"w1", "w2", "w3"},
        accessibility={"alice": {("w1", "w2"), ("w2", "w2"), ("w2", "w3"), ("w3", "w3")}},
        valuation={"w1": {"p": True}, "w2": {"p": True}, "w3": {"p": False}},
    )
    assert test_kk_principle(failing_kk_model, "alice", "p")[0] is False

    gettier_model, gettier_proof = construct_gettier_counterexample()
    assert gettier_proof.is_valid()
    assert gettier_model.worlds == {"w1", "w2"}
    justification = ProofObject("Justification", ["misleading evidence still forms a valid derivation"], "belief justified")
    assert evaluate_jtb(gettier_model, "smith", "ford_or_barcelona", "w1", justification)[0] is True
    assert evaluate_knowledge(gettier_model, "smith", "ford_or_barcelona", "w1")[0] is False

    both_model = KripkeModel({"w"}, {"alice": {("w", "w")}}, {"w": {"q": True, "not:q": True}})
    true_model = KripkeModel({"w"}, {"alice": {("w", "w")}}, {"w": {"q": True, "not:q": False}})
    false_model = KripkeModel({"w"}, {"alice": {("w", "w")}}, {"w": {"q": False, "not:q": True}})
    neither_model = KripkeModel({"w"}, {"alice": {("w", "w")}}, {"w": {"q": False, "not:q": False}})
    assert evaluate_paraconsistent(both_model, "alice", "q", "w")[0] == ParaconsistentTruthValue.BOTH
    assert evaluate_paraconsistent(true_model, "alice", "q", "w")[0] == ParaconsistentTruthValue.TRUE
    assert evaluate_paraconsistent(false_model, "alice", "q", "w")[0] == ParaconsistentTruthValue.FALSE
    assert evaluate_paraconsistent(neither_model, "alice", "q", "w")[0] == ParaconsistentTruthValue.NEITHER

    distributed_model = KripkeModel(
        worlds={"w1", "w2", "w3"},
        accessibility={
            "alice": {("w1", "w1"), ("w1", "w2")},
            "bob": {("w1", "w1"), ("w1", "w3")},
        },
        valuation={
            "w1": {"p": True, "announce": True},
            "w2": {"p": False, "announce": True},
            "w3": {"p": False, "announce": False},
        },
    )
    assert evaluate_knowledge(distributed_model, "alice", "p", "w1")[0] is False
    assert evaluate_knowledge(distributed_model, "bob", "p", "w1")[0] is False
    assert evaluate_distributed_knowledge(distributed_model, ["alice", "bob"], "p", "w1")[0] is True

    announced_model, proof = public_announcement(distributed_model, "announce")
    assert proof.is_valid()
    assert announced_model.worlds == {"w1", "w2"}


def main():
    test_epistemic_advanced_suite()
    print("PASS test_epistemic_advanced_suite")


if __name__ == "__main__":
    main()
