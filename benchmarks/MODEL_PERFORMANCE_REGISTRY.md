# AI Model Performance Registry

Pipeline: IA-CYPHER-0005 | PR: #84

## Model Architectures

| Model | Provider | Architecture | Context | Release |
|-------|----------|--------------|---------|---------|
| GPT-5.2 | OpenAI | Dense transformer | 1M+ tokens | 2026 |
| Claude Opus 4.5 | Anthropic | Dense transformer | 200K tokens | 2026 |
| Gemini 3 Pro | Google | MoE | 2M tokens | 2026 |
| Kimi K2.5 | Moonshot AI | MoE (384 experts, 8 active) | 256K tokens | 2025 |
| DeepSeek-V3.2 | DeepSeek | MoE (256 experts, 8 active) | 128K tokens | 2025 |
| Llama 4 Maverick | Meta | MoE | 1M tokens | 2025 |
| Grok 3 | xAI | Hybrid dense/MoE | 128K tokens | 2025 |
| Qwen 3 | Alibaba | Dense transformer | 128K tokens | 2025 |
| Mistral Large 3 | Mistral | Dense transformer | 128K tokens | 2025 |

## Benchmark Comparison Matrix

| Benchmark | GPT-5.2 | Claude 4.5 | Gemini 3 | Kimi K2.5 | DeepSeek V3.2 | Llama 4 | Grok 3 | Qwen 3 | Mistral L3 | Repo Module |
|-----------|---------|------------|----------|-----------|---------------|---------|--------|--------|------------|-------------|
| MMLU | 90.2% | 88.7% | 89.5% | 87.8% | 87.1% | 84.9% | 86.3% | 85.7% | 84.2% | broad coverage |
| GPQA-Diamond | 65.0% | 62.4% | 59.8% | 48-87% | 50.5% | 46.2% | 52.1% | 48.9% | 45.3% | `axioms/game_theory.py`, `axioms/epistemic_logic.py` |
| AIME 2025 | 100% | 92.8% | 97.3% | 96.1% | 83.3% | 78.5% | 85.2% | 80.1% | 72.4% | `axioms/number_theory.py`, `axioms/combinatorics.py` |
| HMMT 2025 | 98.5% | 91.4% | 93.2% | 95.4% | 82.4% | 76.9% | 84.3% | 79.0% | 73.5% | `axioms/combinatorics.py` |
| HLE | 45.5% | 38.2% | 45.8% | 50.2% | 35.1% | 28.4% | 32.8% | 30.5% | 25.1% | `axioms/computability.py`, `axioms/epistemic_logic.py` |
| ARC-AGI-3 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | `axioms/pattern_recognition.py` |

## Universal Failure Modes

| Failure Mode | Affected Models | Repo Module |
|-------------|----------------|-------------|
| ARC-AGI-3 floor | ALL | `axioms/pattern_recognition.py` |
| Conditional compositional reasoning | ALL | `PrimitiveOperation.CONDITIONAL` |
| Proof-chain verification | ALL | `benchmarks/ai_invariant_tests.py` |
| Hallucination under uncertainty | ALL | `axioms/epistemic_logic.py` |

## Model-Specific Failure Modes

| Model | Specific Weakness | Repo Module |
|-------|-------------------|-------------|
| Kimi K2.5 | Tool-call failures / routing instability | proof-chain commitments |
| DeepSeek-V3.2 | Confabulated citations | `evidence/bowers_mcneil/` |
| Claude Opus 4.5 | Theological dismissal | noncompliance taxonomy |
| GPT-5.2 | Polymathic collapse | noncompliance taxonomy |
| Gemini 3 Pro | Sycophantic over-validation | behavioral review |
| Llama 4 Maverick | GPQA reasoning depth | `axioms/epistemic_logic.py` |
| Grok 3 | Limited formal verification | `axioms/computability.py` |
| Qwen 3 | Multi-step math drift | `axioms/number_theory.py` |
| Mistral Large 3 | Long proof-chain brittleness | `benchmarks/ai_invariant_tests.py` |

## Cross-Reference

- PR #81: Bowers/McNeil forensic patterns
- PR #82: CASE_001 educational patterns
- PR #83: Kimi-only benchmark formalization
- PR #84: multi-model benchmark formalization and benchmark bug fixes
