#!/usr/bin/env python3
"""
Photonic Chip Fractal Dataset Generator
========================================

Generates a deterministic, content-addressed DAG from the Photonic Chip Universe seed.

Authority: seed/photonic_chip_universe.yaml
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class PhotonicNode:
    """Represents a single node in the Photonic Chip DAG."""

    def __init__(
        self,
        node_id: str,
        parent_node: Optional[str],
        level: str,
        index: int,
        name: str,
        seed_ref: str,
    ) -> None:
        self.node_id = node_id
        self.parent_node = parent_node
        self.level = level
        self.index = index
        self.name = name
        self.seed_ref = seed_ref
        self.children: List[str] = []
        self.content_hash: Optional[str] = None
        self.safety_constraints: Optional[Dict[str, Any]] = None
        self.metadata: Dict[str, Any] = {}

    def set_safety_constraints(self, constraints: Dict[str, Any]) -> None:
        """Set safety constraints from universe."""
        self.safety_constraints = constraints

    def compute_content_hash(self) -> str:
        """Compute canonical content hash for this node."""
        content = {
            "node_id": self.node_id,
            "parent_node": self.parent_node,
            "level": self.level,
            "index": self.index,
            "name": self.name,
            "children": sorted(self.children),
            "seed_ref": self.seed_ref,
            "safety_constraints": self.safety_constraints,
            "metadata": self.metadata,
        }
        payload = json.dumps(content, sort_keys=True, separators=(",", ":"))
        self.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "node_id": self.node_id,
            "parent_node": self.parent_node,
            "level": self.level,
            "index": self.index,
            "name": self.name,
            "seed_ref": self.seed_ref,
            "children": self.children,
            "content_hash": self.content_hash,
            "safety_constraints": self.safety_constraints,
            "metadata": self.metadata,
        }


def _hash_id(seed: str, parent: Optional[str], level: str, index: int) -> str:
    """Deterministic node ID from seed + parent + level + index."""
    payload = json.dumps(
        {"seed": seed, "parent": parent, "level": level, "index": index},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def generate_universe(seed_path: str | Path) -> List[PhotonicNode]:
    """Expand photonic_chip_universe.yaml into a deterministic DAG.

    Returns a flat list of PhotonicNode objects.
    """
    seed_path = Path(seed_path)
    with open(seed_path, "r", encoding="utf-8") as fh:
        seed = yaml.safe_load(fh)

    universe = seed["universe"]
    subsystems = universe.get("subsystems", {})
    test_cases_per_param = universe.get("test_cases_per_parameter", 4)
    safety = universe.get("safety", {})
    seed_value = str(universe.get("seed_value", "271828"))

    nodes: List[PhotonicNode] = []
    node_index = 0

    # Root node
    root_id = _hash_id(seed_value, None, "universe", node_index)
    root = PhotonicNode(
        node_id=root_id,
        parent_node=None,
        level="universe",
        index=node_index,
        name=universe["id"],
        seed_ref=str(seed_path),
    )
    root.set_safety_constraints(safety)
    nodes.append(root)
    node_index += 1

    for subsys_name, subsys_data in subsystems.items():
        subsys_id = _hash_id(seed_value, root_id, "subsystem", node_index)
        subsys_node = PhotonicNode(
            node_id=subsys_id,
            parent_node=root_id,
            level="subsystem",
            index=node_index,
            name=subsys_name,
            seed_ref=str(seed_path),
        )
        subsys_node.set_safety_constraints(safety)
        nodes.append(subsys_node)
        root.children.append(subsys_id)
        node_index += 1

        for comp_name in subsys_data.get("components", []):
            comp_id = _hash_id(seed_value, subsys_id, "component", node_index)
            comp_node = PhotonicNode(
                node_id=comp_id,
                parent_node=subsys_id,
                level="component",
                index=node_index,
                name=comp_name,
                seed_ref=str(seed_path),
            )
            comp_node.set_safety_constraints(safety)
            nodes.append(comp_node)
            subsys_node.children.append(comp_id)
            node_index += 1

            # Parameters (2 per component for deterministic expansion)
            for param_idx in range(2):
                param_name = f"{comp_name}_param_{param_idx + 1}"
                param_id = _hash_id(seed_value, comp_id, "parameter", node_index)
                param_node = PhotonicNode(
                    node_id=param_id,
                    parent_node=comp_id,
                    level="parameter",
                    index=node_index,
                    name=param_name,
                    seed_ref=str(seed_path),
                )
                param_node.set_safety_constraints(safety)
                nodes.append(param_node)
                comp_node.children.append(param_id)
                node_index += 1

                # Test cases
                for tc_idx in range(test_cases_per_param):
                    tc_name = f"{param_name}_tc_{tc_idx + 1}"
                    tc_id = _hash_id(seed_value, param_id, "test_case", node_index)
                    tc_node = PhotonicNode(
                        node_id=tc_id,
                        parent_node=param_id,
                        level="test_case",
                        index=node_index,
                        name=tc_name,
                        seed_ref=str(seed_path),
                    )
                    tc_node.metadata["expected_result"] = "pass" if tc_idx < 2 else "fail"
                    tc_node.set_safety_constraints(safety)
                    nodes.append(tc_node)
                    param_node.children.append(tc_id)
                    node_index += 1

    # Compute content hashes
    for node in nodes:
        node.compute_content_hash()

    return nodes


def write_manifest(nodes: List[PhotonicNode], output_path: str | Path) -> Path:
    """Write manifest JSONL and return the path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        for node in nodes:
            fh.write(json.dumps(node.to_dict(), sort_keys=True) + "\n")
    return output_path


def main() -> int:
    """CLI entry point."""
    repo_root = Path(__file__).resolve().parent.parent
    seed_path = repo_root / "seed" / "photonic_chip_universe.yaml"
    output_path = repo_root / "out" / "photonic_chip_manifest.jsonl"

    if not seed_path.exists():
        print(f"ERROR: seed not found: {seed_path}", file=sys.stderr)
        return 1

    nodes = generate_universe(seed_path)
    manifest_path = write_manifest(nodes, output_path)
    print(f"Generated {len(nodes)} nodes → {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
