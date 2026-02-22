"""falsification package — Popperian Enforcement Layer"""
from falsification.hypothesis import Hypothesis, FalsificationResult, register_hypothesis, HYPOTHESIS_REGISTRY
from falsification.counterexample_engine import CounterexampleFound, run_falsification, run_all_hypotheses
