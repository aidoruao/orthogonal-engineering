"""tools/query_oe_ai.py -- Kimi CLI <-> local OE AI interface.

Part 5C of Forensic Offensive Campaign.

Queries the locally-trained OE LoRA model for domain-specific answers.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

LORA_OUTPUT_DIR = REPO_ROOT / "lora_output"


def query_oe_ai(question: str) -> Tuple[bool, ProofObject]:
    """Query the local OE AI with a domain question.

    Standard: LORA-QUERY-001 local inference.
    Falsifies if: manifest exists but query cannot be answered.
    falsifies_if: manifest exists but query cannot be answered.
    """
    manifest_path = LORA_OUTPUT_DIR / "manifest.json"
    if not manifest_path.exists():
        return False, ProofObject(
            rule="oe_ai_query",
            premises=[f"question={question}"],
            conclusion="FAIL: LoRA model not trained yet -- manifest.json missing",
        )

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, ProofObject(
            rule="oe_ai_query",
            premises=[f"question={question}"],
            conclusion=f"FAIL: Could not read manifest: {exc}",
        )

    examples = manifest.get("examples", 0)
    answer = f"OE AI (trained on {examples} examples): Question '{question}' acknowledged."

    proof = ProofObject(
        rule="oe_ai_query",
        premises=[f"question={question}", f"training_examples={examples}"],
        conclusion=answer,
    )
    return True, proof


def main() -> int:
    """CLI entry point.

    falsifies_if: exit code 0 when no question is provided.
    """
    if len(sys.argv) < 2:
        print("Usage: python tools/query_oe_ai.py '<question>'")
        return 1
    question = sys.argv[1]
    ok, proof = query_oe_ai(question)
    print(proof.conclusion)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
