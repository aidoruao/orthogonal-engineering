"""tools/unify_lora_datasets.py -- Merge all LoRA datasets into unified training corpus.

Part 5A of Forensic Offensive Campaign.

Merges datasets from lora_dataset/, lora_dataset_augmented.jsonl,
and photonic campaign data -> target 1500+ examples.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

DATASET_PATHS = [
    REPO_ROOT / "lora_dataset",
    REPO_ROOT / "lora_dataset_augmented.jsonl",
]
OUTPUT_PATH = REPO_ROOT / "lora_dataset_unified.jsonl"
TARGET_EXAMPLES = 1500


def _load_examples(path: Path) -> List[dict]:
    """Load examples from a dataset path.

    falsifies_if: returns non-empty list when path contains no valid examples.
    """
    examples: List[dict] = []
    if path.is_dir():
        for child in path.iterdir():
            if child.suffix == ".jsonl":
                try:
                    with child.open(encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                examples.append(json.loads(line))
                except (OSError, json.JSONDecodeError):
                    continue
    elif path.is_file() and path.suffix == ".jsonl":
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        examples.append(json.loads(line))
        except (OSError, json.JSONDecodeError):
            pass
    return examples


def unify_datasets() -> Tuple[bool, ProofObject]:
    """Merge all LoRA datasets into a single unified corpus.

    Standard: LORA-001 dataset unification.
    Falsifies if: unified corpus has fewer than TARGET_EXAMPLES.
    falsifies_if: unified corpus has fewer than TARGET_EXAMPLES.
    """
    all_examples: List[dict] = []
    for path in DATASET_PATHS:
        if path.exists():
            all_examples.extend(_load_examples(path))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    count = len(all_examples)
    success = count >= TARGET_EXAMPLES
    proof = ProofObject(
        rule="lora_dataset_unification",
        premises=[f"examples={count}", f"target={TARGET_EXAMPLES}"],
        conclusion=(
            f"PASS: Unified {count} examples into {OUTPUT_PATH}"
            if success else f"FAIL: Only {count} examples, target is {TARGET_EXAMPLES}"
        ),
    )
    return success, proof


if __name__ == "__main__":
    ok, proof = unify_datasets()
    print(proof.conclusion)
    sys.exit(0 if ok else 1)
