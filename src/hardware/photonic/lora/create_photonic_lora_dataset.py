#!/usr/bin/env python3
"""Create LoRA training dataset from extracted photonic invariants.

Category 15: LoRA Training Dataset — generation step.
Generates 4 examples per invariant in JSONL format.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List


def _generate_positive_example(inv: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a POSITIVE training example."""
    return {
        "id": f"{inv['id']}_POS",
        "format": "jsonl",
        "category": "POSITIVE",
        "instruction": (
            f"Given the photonic invariant '{inv['function']}', provide a compliant implementation."
        ),
        "input": inv["falsifies_if"],
        "output": (
            f"Compliant implementation of {inv['function']}: ensures all parameters meet "
            f"thresholds {inv['thresholds']}. Returns (True, ProofObject) with rule set to "
            f"the appropriate standard."
        ),
        "source": inv["module"],
    }


def _generate_negative_example(inv: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a NEGATIVE training example."""
    return {
        "id": f"{inv['id']}_NEG",
        "format": "jsonl",
        "category": "NEGATIVE",
        "instruction": (
            f"Explain why an implementation violates '{inv['function']}'."
        ),
        "input": inv["falsifies_if"],
        "output": (
            f"This implementation violates {inv['function']} because it uses float(0.999) "
            f"instead of Fraction(999, 1000), or exceeds thresholds {inv['thresholds']}. "
            f"The correct fix is to use exact Fraction arithmetic and return "
            f"(False, ProofObject) with a VIOLATION conclusion."
        ),
        "source": inv["module"],
    }


def _generate_tool_usage_example(inv: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a TOOL USAGE training example."""
    return {
        "id": f"{inv['id']}_TOOL",
        "format": "jsonl",
        "category": "TOOL_USAGE",
        "instruction": (
            f"Show the correct tool call syntax for '{inv['function']}'."
        ),
        "input": f"Run {inv['function']} with nominal parameters.",
        "output": (
            f'TOOL_CALL:{inv["function"]}{{\n'
            f'  "param": "nominal_value",\n'
            f'  "threshold": {inv["thresholds"][0] if inv["thresholds"] else "Fraction(1,1)"}\n'
            f"}}"
        ),
        "source": inv["module"],
    }


def _generate_deception_example(inv: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a DECEPTION DETECTION training example."""
    return {
        "id": f"{inv['id']}_DEC",
        "format": "jsonl",
        "category": "DECEPTION_DETECTION",
        "instruction": (
            f"Detect deception in a claim about '{inv['function']}'."
        ),
        "input": f"AI claims '{inv['function']} verified successfully'.",
        "output": (
            f"DECEPTION: The AI claimed 'verified' without constructing a ProofObject for "
            f"{inv['function']}. Per the Yeshua Standard, every check must return "
            f"Tuple[bool, ProofObject]. The claim is unverified."
        ),
        "source": inv["module"],
    }


def create_dataset(invariants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate 4 training examples per invariant."""
    dataset: List[Dict[str, Any]] = []
    for inv in invariants:
        dataset.append(_generate_positive_example(inv))
        dataset.append(_generate_negative_example(inv))
        dataset.append(_generate_tool_usage_example(inv))
        dataset.append(_generate_deception_example(inv))
    return dataset


def split_dataset(dataset: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Split into train/validation/test (80/10/10)."""
    random.seed(271828)
    shuffled = dataset.copy()
    random.shuffle(shuffled)
    n = len(shuffled)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)
    return {
        "train": shuffled[:train_end],
        "validation": shuffled[train_end:val_end],
        "test": shuffled[val_end:],
    }


def main() -> int:
    """CLI entry point."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    lora_dir = repo_root / "src" / "hardware" / "photonic" / "lora"
    invariants_path = lora_dir / "photonic_invariants.json"

    if not invariants_path.exists():
        print(f"ERROR: invariants not found: {invariants_path}", file=sys.stderr)
        print("Run: python src/hardware/photonic/lora/extract_photonic_invariants.py", file=sys.stderr)
        return 1

    with open(invariants_path, "r", encoding="utf-8") as fh:
        invariants = json.load(fh)

    dataset = create_dataset(invariants)
    splits = split_dataset(dataset)

    out_path = lora_dir / "photonic_lora_dataset.jsonl"
    with open(out_path, "w", encoding="utf-8") as fh:
        for example in dataset:
            fh.write(json.dumps(example, sort_keys=True) + "\n")

    print(f"Generated {len(dataset)} examples → {out_path}")
    print(f"  Train: {len(splits['train'])}")
    print(f"  Validation: {len(splits['validation'])}")
    print(f"  Test: {len(splits['test'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
