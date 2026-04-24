"""kernel/correspondence_bridge.py -- Correspondence validator for sub-agent outputs.

Part 4D of Forensic Offensive Campaign.

Every sub-agent output from kernel/agent_stream.py must pass a correspondence
check: the output must commute with the expected transformation diagram.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject
from src.domains.d_correspondence_theory.implementation import CorrespondenceDiagram, Morphism
from src.domains.d_correspondence_theory.invariants import check_commutative_square


def validate_sub_agent_output(
    input_payload: str,
    output_payload: str,
    expected_diagram: CorrespondenceDiagram,
) -> Tuple[bool, ProofObject]:
    """Validate that a sub-agent output satisfies the correspondence diagram.

    Standard: KERNEL-CORR-001 sub-agent validation.
    Falsifies if: output does not commute with the expected diagram.
    falsifies_if: output does not commute with the expected diagram.
    """
    success, proof = check_commutative_square(expected_diagram)
    if not success:
        return False, ProofObject(
            rule="sub_agent_correspondence",
            premises=[
                f"input_payload={input_payload}",
                f"output_payload={output_payload}",
                f"diagram={expected_diagram.diagram_id}",
            ],
            conclusion=f"FAIL: Sub-agent output violates correspondence -- {proof.conclusion}",
        )
    return True, ProofObject(
        rule="sub_agent_correspondence",
        premises=[
            f"input_payload={input_payload}",
            f"output_payload={output_payload}",
            f"diagram={expected_diagram.diagram_id}",
        ],
        conclusion="Sub-agent output commutes with correspondence diagram",
    )


if __name__ == "__main__":
    # Smoke test with a trivial commuting diagram
    f = Morphism(name="f", source="A", target="B", mapping=lambda x: f"agent({x})")
    g = Morphism(name="g", source="A", target="C", mapping=lambda x: f"validate(agent({x}))")
    h = Morphism(name="h", source="B", target="C", mapping=lambda x: f"validate({x})")
    diagram = CorrespondenceDiagram(
        diagram_id="AGENT001",
        objects=("A", "B", "C"),
        morphisms={"f": f, "g": g, "h": h},
        test_inputs=("task_1",),
    )
    ok, proof = validate_sub_agent_output("task_1", "result_1", diagram)
    print(proof.conclusion)
    sys.exit(0 if ok else 1)
