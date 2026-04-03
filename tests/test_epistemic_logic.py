#!/usr/bin/env python3
# @falsification_id: F_EPIST_001
"""Tests for PR #83 epistemic-logic layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.epistemic_logic import agm_revision, KripkeModel, construct_gettier_counterexample, evaluate_common_knowledge, evaluate_distributed_knowledge, evaluate_jtb, evaluate_knowledge, public_announcement, test_kk_principle
from axioms.logic import ProofObject


def test_epistemic_logic_suite():
    model = KripkeModel(
        worlds={"w1", "w2"},
        accessibility={"alice": {("w1", "w1"), ("w1", "w2"), ("w2", "w2")}, "bob": {("w1", "w1"), ("w2", "w2")}},
        valuation={"w1": {"p": True, "believes:alice:p": True}, "w2": {"p": True, "believes:alice:p": True}},
    )
    just = ProofObject("Justification", ["sensor trace"], "belief justified")
    assert evaluate_knowledge(model, "alice", "p", "w1")[0]
    assert evaluate_common_knowledge(model, ["alice", "bob"], "p", "w1")[0]
    assert evaluate_jtb(model, "alice", "p", "w1", just)[0]
    assert construct_gettier_counterexample()[1].is_valid()
    assert test_kk_principle(model, "alice", "p")[0]
    richer = KripkeModel(
        worlds={"w1", "w2", "w3"},
        accessibility={"alice": {("w1", "w1"), ("w1", "w2")}, "bob": {("w1", "w1"), ("w1", "w3")}},
        valuation={"w1": {"p": True, "announce": True}, "w2": {"p": False, "announce": True}, "w3": {"p": False, "announce": False}},
    )
    assert evaluate_distributed_knowledge(richer, ["alice", "bob"], "p", "w1")[0]
    assert public_announcement(richer, "announce")[0].worlds == {"w1", "w2"}
    assert agm_revision({"p", "q"}, "not:p")[0] == {"q", "not:p"}


def main():
    test_epistemic_logic_suite()
    print("PASS test_epistemic_logic_suite")


if __name__ == "__main__":
    main()
