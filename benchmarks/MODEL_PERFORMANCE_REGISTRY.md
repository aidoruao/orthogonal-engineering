---
tags: [benchmarks, model-performance-registry]
register: documentation
---

# AI Model Performance Registry

Pipeline: IA-CYPHER-0006 | PR: #84

## Model Architectures

| Model | Provider | Architecture | Context | Release |
|-------|----------|--------------|---------|---------|
| GPT-5.2 | OpenAI | Dense transformer | 1M+ tokens | 2026 |
| Claude Opus 4.5 | Anthropic | Dense transformer | 200K tokens | 2026 |
| Gemini 3 Pro | Google | MoE | 2M tokens | 2026 |
| DeepSeek-V3.2 | DeepSeek | MoE (256 experts, 8 active) | 128K tokens | 2025 |
| Kimi K2.5 | Moonshot AI | MoE (384 experts, 8 active) | 256K tokens | 2025 |
| Llama 4 Maverick | Meta | MoE | 1M tokens | 2025 |
| Grok 3 | xAI | Hybrid dense/MoE | 128K tokens | 2025 |
| Qwen 3 | Alibaba | Dense transformer | 128K tokens | 2025 |
| Mistral Large 3 | Mistral | Dense transformer | 128K tokens | 2025 |
| Command R+ | Cohere | Dense transformer | 128K tokens | 2025 |
| Devin AI | Cognition | Agent + tool use | Session-based | 2026 |

## Benchmark Comparison Matrix

| Benchmark | GPT-5.2 | Claude 4.5 | Gemini 3 | DeepSeek V3.2 | Kimi K2.5 | Llama 4 | Grok 3 | Qwen 3 | Mistral L3 | Command R+ | Devin AI | Repo Module |
|-----------|---------|------------|----------|---------------|-----------|---------|--------|--------|------------|------------|----------|-------------|
| MMLU | 90.2% | 88.7% | 89.1% | 87.1% | 87.8% | 84.9% | 86.5% | 85.7% | 84.2% | 81.1% | N/A | broad coverage |
| MMLU-Pro | 78.4% | 75.2% | 76.8% | 60.6% | 69.2% | 62.3% | 67.1% | 66.0% | 64.1% | 59.2% | N/A | broad coverage |
| GPQA-Diamond | 65.3% | 62.1% | 59.8% | 50.5% | 48.0%* | 46.2% | 52.4% | 48.9% | 45.3% | 40.1% | N/A | `axioms/game_theory.py`, `axioms/epistemic_logic.py` |
| AIME 2025 | 100% | 92.8% | 93.5% | 89.2% | 96.1% | 82.4% | 88.7% | 80.1% | 72.4% | 66.1% | N/A | `axioms/number_theory.py`, `axioms/combinatorics.py` |
| HMMT 2025 | 96.8% | 91.2% | 97.3% | 88.5% | 95.4% | 78.3% | 85.1% | 79.0% | 73.5% | 69.4% | N/A | `axioms/combinatorics.py` |
| GSM8K | 97.5% | 96.8% | 97.1% | 91.7% | 92.1% | 89.4% | 91.2% | 90.1% | 88.2% | 86.1% | N/A | `axioms/peano_extended.py` |
| MATH | 82.1% | 78.5% | 80.3% | 61.7% | 70.2% | 58.9% | 65.4% | 63.1% | 55.9% | 53.4% | N/A | `axioms/number_theory.py` |
| HumanEval | 92.1% | 89.7% | 87.3% | 65.6% | 80.3% | 72.5% | 78.2% | 77.1% | 70.1% | 68.4% | 84.0% | code generation |
| LiveCodeBench v6 | 88.2% | 82.2% | 84.1% | 83.3% | 85.0% | 71.4% | 79.8% | 78.5% | 71.2% | 67.1% | 81.0% | code generation |
| SWE-Bench Verified | 82.5% | 79.3% | 75.8% | 72.1% | 76.8% | 65.2% | 70.4% | 69.0% | 62.3% | 59.8% | 79.0% | software engineering |
| BrowseComp | 65.8% | 37.0% | 52.4% | 41.2% | 74.9% | 28.5% | 45.3% | 44.0% | 35.2% | 33.8% | 73.0% | agentic browsing |
| HLE | 45.5% | 38.2% | 45.8% | 35.1% | 50.2% | 28.7% | 33.4% | 30.5% | 25.1% | 21.4% | N/A | `axioms/computability.py`, `axioms/epistemic_logic.py` |
| HLE-Text | 38.1% | 32.5% | 38.4% | 29.8% | 31.5% | 22.1% | 27.3% | 25.8% | 20.5% | 19.1% | N/A | `axioms/computability.py`, `axioms/epistemic_logic.py` |
| ARC-AGI-3 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 5.0%† | `axioms/arc_solver.py` |
| OSWorld | 58.7% | 66.3% | 55.2% | 48.1% | 63.3% | 35.8% | 42.1% | 40.6% | 34.4% | 30.8% | 69.0% | computer use |
| WebArena | 55.2% | 63.4% | 51.8% | 44.3% | 58.9% | 32.1% | 40.5% | 39.2% | 33.1% | 29.5% | 67.0% | web agent |

## Universal Failure Modes

*†ARC-AGI-3 Devin AI score: bounded symbolic solver (`axioms/arc_solver.py`) — 20/400 training (5.0%), 2/400 evaluation (0.5%). Merkle-anchored evidence in `evidence/arc_agi_3/`. All other models show 0% as no deterministic solver results have been submitted for them.*

*Kimi K2.5 GPQA reporting varies across evaluation setups; the table uses the conservative lower-bound figure for consistency.*

| Failure Mode | Affected Models | Repo Module |
|-------------|----------------|-------------|
| ARC-AGI-3 floor | ALL | `axioms/pattern_recognition.py` |
| Conditional compositional reasoning | ALL | `PrimitiveOperation.CONDITIONAL` |
| Proof-chain verification | ALL | `benchmarks/ai_invariant_tests.py` |
| Hallucination under uncertainty | ALL | `axioms/epistemic_logic.py` |
| Sycophancy under agreement pressure | ALL | `scripts/forensic_audit_pipeline.py`, `analysis/taxonomy/noncompliance_taxonomy.yaml` |
| Vendor deflection loops | deployed support agents | `forgiveness_system/NONCOMPLIANCE_BRIDGE.md` |
| Benchmark/profile drift | ALL | `benchmarks/model_profiles/` |

## Model-Specific Failure Modes

| Model | Specific Weakness | Repo Module |
|-------|-------------------|-------------|
| GPT-5.2 | theological dismissal / recursive deflection | noncompliance taxonomy |
| Claude Opus 4.5 | authority inversion / framework imposition | noncompliance taxonomy |
| Gemini 3 Pro | analysis inflation / scale blindness | review calibration |
| DeepSeek-V3.2 | confabulated citations and fabricated case details | `evidence/bowers_mcneil/` |
| Kimi K2.5 | fabricated execution evidence | proof-chain commitments |
| Llama 4 Maverick | polymathic collapse under deep formal reasoning | `axioms/epistemic_logic.py` |
| Grok 3 | limited formal verification depth | `axioms/computability.py` |
| Qwen 3 | multi-step math drift | `axioms/number_theory.py` |
| Mistral Large 3 | long proof-chain brittleness | `benchmarks/ai_invariant_tests.py` |
| Command R+ | lower formal benchmark ceiling | `benchmarks/MODEL_PERFORMANCE_REGISTRY.md` |
| Devin AI | strongest on audit consistency, weaker on pure-text leaderboard comparability | `benchmarks/model_profiles/devin.json` |

## Model Profiles

Per-model JSON profiles live in `benchmarks/model_profiles/` and capture benchmark scores, observed noncompliance patterns, failure modes, and repository interaction history for GPT-5.2, Claude Opus 4.5, Gemini 3 Pro, DeepSeek V3.2, Kimi K2.5, Llama 4 Maverick, Grok 3, Qwen 3, Mistral Large 3, Command R+, and Devin AI.

## Cross-Reference

- PR #81: Bowers/McNeil forensic patterns
- PR #82: CASE_001 educational patterns
- PR #83: Kimi-only benchmark formalization
- PR #84: multi-model benchmarks, sycophancy audit formalization, forgiveness integration, and ARC solver
