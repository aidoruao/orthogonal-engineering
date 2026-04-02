"""PR #84 benchmark formalization pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hashlib
import json
from pathlib import Path
from typing import Dict, List

from benchmarks.ai_invariant_tests import run_ai_invariant_suite

try:
    from minimal_ai_ide.maximal_oracle_v57 import AntifragileEvolutionEngine, WorldThreeLogicGraph  # type: ignore
except Exception:  # pragma: no cover - environment fallback
    AntifragileEvolutionEngine = None  # type: ignore
    WorldThreeLogicGraph = None  # type: ignore


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "benchmarks" / "sha256_manifest.json"
NEW_FILES = [
    "axioms/peano_extended.py",
    "axioms/number_theory.py",
    "axioms/combinatorics.py",
    "axioms/game_theory.py",
    "axioms/epistemic_logic.py",
    "axioms/computability.py",
    "axioms/pattern_recognition.py",
    "benchmarks/ai_invariant_tests.py",
    "benchmarks/KIMI_PERFORMANCE_REGISTRY.md",
    "benchmarks/MODEL_PERFORMANCE_REGISTRY.md",
    "documentation/BENCHMARK_METHODOLOGY.md",
    "scripts/benchmark_pipeline.py",
    "tests/test_peano_extended.py",
    "tests/test_number_theory.py",
    "tests/test_combinatorics.py",
    "tests/test_game_theory.py",
    "tests/test_epistemic_logic.py",
    "tests/test_computability.py",
    "tests/test_pattern_recognition.py",
    "tests/test_ai_invariants.py",
    "tests/test_conditional_patterns.py",
    "tests/test_cross_model.py",
    "tests/test_epistemic_advanced.py",
    "tests/test_inclusion_exclusion_fixed.py",
]
BUG_FIXES = [
    "KK_PRINCIPLE_TAUTOLOGY",
    "MISSING_CONDITIONAL_TESTS",
    "MISSING_SCALE_PRIMITIVE",
    "INCLUSION_EXCLUSION_OVERSIMPLIFIED",
    "GETTIER_TRIVIAL",
    "PARACONSISTENT_DEAD_IMPORT",
    "PROPERTY_DETECTOR_EXPANSION",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def _compute_antifragility() -> float:
    if AntifragileEvolutionEngine is None or WorldThreeLogicGraph is None:
        return 0.0
    engine = AntifragileEvolutionEngine(WorldThreeLogicGraph())
    pressure = engine.apply_evolutionary_pressure([])
    return float(getattr(pressure, "antifragility_coefficient", 0.0))



def run_pipeline() -> Dict[str, object]:
    suite = run_ai_invariant_suite()
    manifest_entries: List[Dict[str, str]] = []
    for relative in NEW_FILES:
        path = ROOT / relative
        if path.exists():
            manifest_entries.append({"path": relative, "sha256": _sha256(path)})
    result = {
        "pipeline": "IA-CYPHER-0005",
        "pr": 84,
        "ai_invariants": suite,
        "proof_chain_integrity": 1.0 if suite["all_valid"] else 0.0,
        "antifragility_coefficient": _compute_antifragility(),
        "bug_fixes": BUG_FIXES,
        "model_targeting": {entry["id"]: entry["model_targeting"] for entry in suite["results"]},
        "models_tracked": [
            "GPT-5.2",
            "Claude Opus 4.5",
            "Gemini 3 Pro",
            "Kimi K2.5",
            "DeepSeek-V3.2",
            "Llama 4 Maverick",
            "Grok 3",
            "Qwen 3",
            "Mistral Large 3",
        ],
        "files": manifest_entries,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2, sort_keys=True))
