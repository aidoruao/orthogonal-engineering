# Kimi K2.5 Performance Registry

Pipeline: IA-CYPHER-0004 | PR: #83

## Architecture

| Spec | Value |
|------|-------|
| Parameters | 1T total, 32B active/token |
| Architecture | MoE, 384 experts, 8 active/token |
| Context | 256K tokens |

## Benchmark Scores (self-reported)

| Benchmark | Score | Repo Module That Addresses Gap |
|-----------|-------|-------------------------------|
| MMLU | 87.79% | Benchmark suite already proof-centers reasoning |
| GPQA-Diamond | 48-87% | `axioms/game_theory.py`, `axioms/epistemic_logic.py` |
| AIME 2025 | 96.1% | `axioms/number_theory.py`, `axioms/combinatorics.py` |
| HMMT 2025 | 95.4% | `axioms/combinatorics.py` |
| GSM8K | 92.12% | Peano-grounded arithmetic substrate |
| MATH | 70.22% | `axioms/peano_extended.py`, `axioms/number_theory.py` |
| HumanEval | 80.33% | Existing repo engineering stack |
| SWE-Bench | 76.8% | Existing repo engineering stack |
| HLE | 50.2% | `axioms/computability.py`, `axioms/epistemic_logic.py` |
| ARC-AGI-3 | 0% | `axioms/pattern_recognition.py` |

## Failure Mode → Module Mapping

| Failure Mode | Rate/Description | Addressing Module |
|-------------|------------------|-------------------|
| Tool call failures | Externalized proof chains required | `benchmarks/ai_invariant_tests.py` |
| MoE inconsistency | Routing variability | Merkle-rooted proof commitments |
| Self-misidentification | Externalized capability tracking | This registry + invariant suite |
| ARC-AGI-3 | 0% frontier-model floor | `axioms/pattern_recognition.py` |
| GPQA reasoning depth | Variable abstract reasoning | `axioms/game_theory.py`, `axioms/epistemic_logic.py` |
| HLE without tools | Lower theorem depth | `axioms/computability.py` |

## Cross-Reference

- PR #81: Bowers/McNeil forensic patterns S-09→S-20
- PR #82: CASE_001 educational patterns S-26→S-29
- PR #83: benchmark formalization targeting Kimi failure modes
