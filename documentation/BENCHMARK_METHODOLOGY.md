---
tags: [documentation, benchmark-methodology]
register: documentation
---

# Benchmark Methodology

PR #83 adds a deterministic benchmark formalization layer that externalizes benchmark capability as proof-carrying artifacts.

## Module Mapping

| Module | Benchmark | Contribution |
|--------|-----------|--------------|
| `axioms/peano_extended.py` | Foundation | Extended arithmetic invariants with proof objects |
| `axioms/number_theory.py` | AIME / MATH | CRT, Bezout, totient, modular exponentiation |
| `axioms/combinatorics.py` | HMMT | Binomial, Catalan, pigeonhole, inclusion-exclusion |
| `axioms/game_theory.py` | GPQA-Diamond | Equilibrium, minimax, dominance, incentive compatibility |
| `axioms/epistemic_logic.py` | GPQA-Diamond / HLE | Kripke knowledge, common knowledge, Gettier, KK |
| `axioms/computability.py` | HLE | Halting, Rice, busy beaver, incompleteness |
| `axioms/pattern_recognition.py` | ARC-AGI-3 | Compositional rules, conditional transformations, verification |
| `benchmarks/ai_invariant_tests.py` | Aggregate | 50 proof-anchored invariant problems |
| `scripts/benchmark_pipeline.py` | Aggregate | Manifest generation, Merkle-root integrity, benchmark pipeline |

## Validation

- `python3 tests/test_peano_extended.py`
- `python3 tests/test_number_theory.py`
- `python3 tests/test_combinatorics.py`
- `python3 tests/test_game_theory.py`
- `python3 tests/test_epistemic_logic.py`
- `python3 tests/test_computability.py`
- `python3 tests/test_pattern_recognition.py`
- `python3 tests/test_ai_invariants.py`
- `python3 scripts/benchmark_pipeline.py`
