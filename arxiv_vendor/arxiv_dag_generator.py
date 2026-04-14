#!/usr/bin/env python3
"""
arXiv DAG Generator — Build category hierarchy DAG from arxiv_seed.yaml.

Outputs a deterministic DAG representing arXiv categories as sub-universes,
with edges for hierarchical containment and cross-category morphisms.

Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def build_category_dag(seed: dict) -> dict:
    categories = seed.get("categories", [])
    nodes: Dict[str, dict] = {}
    edges: List[dict] = []

    root_id = "arxiv:root"
    nodes[root_id] = {
        "id": root_id,
        "type": "root",
        "label": seed["root"]["name"],
        "children": [],
    }

    for cat in categories:
        cat_id = cat["id"]
        node_id = f"arxiv:category:{cat_id}"
        nodes[node_id] = {
            "id": node_id,
            "type": "category",
            "label": cat_id,
            "name": cat["name"],
            "query": cat["query"],
            "description": cat.get("description", ""),
            "children": [],
        }
        edges.append({"source": root_id, "target": node_id, "type": "contains"})
        nodes[root_id]["children"].append(node_id)

        # Add implementation-status sub-nodes (lazy placeholders)
        for status in ["IMPLEMENTABLE", "ALREADY_IMPLEMENTED", "NOT_IMPLEMENTABLE", "INVERTIBLE", "SATURATED"]:
            status_id = f"arxiv:status:{cat_id}:{status}"
            nodes[status_id] = {
                "id": status_id,
                "type": "status_bucket",
                "label": status,
                "parent_category": cat_id,
                "paper_ids": [],
            }
            edges.append({"source": node_id, "target": status_id, "type": "classifies"})
            nodes[node_id]["children"].append(status_id)

    # Cross-category morphisms based on prefix overlap (e.g., cs.AI -> cs.LO)
    for i, cat_a in enumerate(categories):
        for cat_b in categories[i + 1 :]:
            prefix_a = cat_a["id"].split(".")[0]
            prefix_b = cat_b["id"].split(".")[0]
            if prefix_a == prefix_b:
                node_a = f"arxiv:category:{cat_a['id']}"
                node_b = f"arxiv:category:{cat_b['id']}"
                edges.append({"source": node_a, "target": node_b, "type": "sibling_domain"})

    dag = {
        "root": root_id,
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "source": seed["root"]["source"],
            "generated_at": seed["root"]["fetch_date"],
            "category_count": len(categories),
            "omega_invariant": seed["root"].get("omega_invariant", ""),
        },
    }

    # Compute DAG hash for verification
    dag_bytes = json.dumps(dag, sort_keys=True, separators=(",", ":")).encode("utf-8")
    dag["dag_hash"] = hashlib.sha256(dag_bytes).hexdigest()
    return dag


def main():
    parser = argparse.ArgumentParser(description="arXiv DAG Generator")
    parser.add_argument("--seed", default="arxiv_vendor/seed/arxiv_seed.yaml")
    parser.add_argument("--output", default="arxiv_vendor/dag/arxiv_category_dag.json")
    args = parser.parse_args()

    with open(args.seed, "r") as f:
        seed = yaml.safe_load(f)

    dag = build_category_dag(seed)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(dag, f, indent=2)
    print(f"DAG written to {output_path} ({len(dag['nodes'])} nodes, {len(dag['edges'])} edges)")


if __name__ == "__main__":
    main()
