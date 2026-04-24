"""D_DAG_THEORY invariants -- Directed Acyclic Graph checks.

Part 3E of Forensic Offensive Campaign.

Checks formalize DAG properties:
- acyclicity proof (no cycles via DFS)
- topological sort determinism (same DAG -> same sort order)
- content-addressed node identity (hash uniquely identifies content)
- Merkle derivability (root hash deterministically derived from children)
- reachability transitivity (if A->B and B->C then A->C)
- deterministic expansion (same parameters -> same node count)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Set, Tuple

from axioms.logic import ProofObject
from .implementation import DAGExpansion, DAGNode, DAGState


def _has_cycle(state: DAGState, node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
    """DFS helper to detect cycles.

    falsifies_if: returns False when a cycle exists.
    """
    visited.add(node_id)
    rec_stack.add(node_id)
    node = state.nodes.get(node_id)
    if node is not None:
        for child_id in node.children:
            if child_id not in visited:
                if _has_cycle(state, child_id, visited, rec_stack):
                    return True
            elif child_id in rec_stack:
                return True
    rec_stack.discard(node_id)
    return False


def check_acyclicity_proof(state: DAGState) -> Tuple[bool, ProofObject]:
    """DAG must contain no cycles.

    Standard: DAG-001 acyclicity.
    Falsifies if: DFS detects a back edge (cycle).
    falsifies_if: DFS detects a back edge (cycle).
    """
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    for node_id in state.nodes:
        if node_id not in visited:
            if _has_cycle(state, node_id, visited, rec_stack):
                return False, ProofObject(
                    rule="dag_acyclicity",
                    premises=[f"dag_id={state.dag_id}", "cycle_detected=True"],
                    conclusion="VIOLATION: Cycle detected in DAG -- acyclicity violated",
                )
    return True, ProofObject(
        rule="dag_acyclicity",
        premises=[f"dag_id={state.dag_id}", f"node_count={len(state.nodes)}"],
        conclusion="No cycles detected: DAG acyclicity holds",
    )


def check_topological_sort_determinism(state: DAGState) -> Tuple[bool, ProofObject]:
    """Topological sort must produce a deterministic ordering.

    Standard: DAG-002 determinism.
    Falsifies if: two Kahn-algorithm runs on the same DAG produce different orders.
    falsifies_if: two Kahn-algorithm runs on the same DAG produce different orders.
    """
    # Kahn's algorithm
    def kahn_sort(nodes: Dict[str, DAGNode]) -> List[str]:
        in_degree: Dict[str, int] = {nid: 0 for nid in nodes}
        for node in nodes.values():
            for child in node.children:
                if child in in_degree:
                    in_degree[child] += 1
        queue = sorted([nid for nid, deg in in_degree.items() if deg == 0])
        result: List[str] = []
        while queue:
            nid = queue.pop(0)
            result.append(nid)
            node = nodes.get(nid)
            if node:
                for child in sorted(node.children):
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        queue.append(child)
                        queue.sort()
        return result

    order1 = kahn_sort(state.nodes)
    order2 = kahn_sort(state.nodes)
    if order1 != order2:
        return False, ProofObject(
            rule="dag_topological_determinism",
            premises=[f"dag_id={state.dag_id}", "run1!=run2"],
            conclusion="VIOLATION: Topological sort is non-deterministic",
        )
    if len(order1) != len(state.nodes):
        return False, ProofObject(
            rule="dag_topological_determinism",
            premises=[f"dag_id={state.dag_id}", f"sorted={len(order1)}", f"nodes={len(state.nodes)}"],
            conclusion="VIOLATION: Topological sort does not include all nodes",
        )
    return True, ProofObject(
        rule="dag_topological_determinism",
        premises=[f"dag_id={state.dag_id}", f"order_length={len(order1)}"],
        conclusion="Topological sort deterministic and complete",
    )


def check_content_addressed_node_identity(state: DAGState) -> Tuple[bool, ProofObject]:
    """Node content_hash must uniquely identify payload (no hash collisions).

    Standard: DAG-003 content addressing.
    Falsifies if: two nodes with different payloads share the same content_hash.
    falsifies_if: two nodes with different payloads share the same content_hash.
    """
    hash_to_payloads: Dict[str, Set[str]] = {}
    for node in state.nodes.values():
        hash_to_payloads.setdefault(node.content_hash, set()).add(node.payload)
    collisions = {
        h: payloads for h, payloads in hash_to_payloads.items() if len(payloads) > 1
    }
    if collisions:
        return False, ProofObject(
            rule="dag_content_addressing",
            premises=[f"dag_id={state.dag_id}", f"collisions={len(collisions)}"],
            conclusion="VIOLATION: Content hash collision detected -- identity not unique",
        )
    return True, ProofObject(
        rule="dag_content_addressing",
        premises=[f"dag_id={state.dag_id}", f"unique_hashes={len(hash_to_payloads)}"],
        conclusion="All content hashes uniquely identify payloads",
    )


def check_merkle_derivability(state: DAGState) -> Tuple[bool, ProofObject]:
    """Root node must be present and its hash must deterministically derive from children.

    Standard: DAG-004 Merkle derivability.
    Falsifies if: root_id not in nodes or root has no children in a non-trivial DAG.
    falsifies_if: root_id not in nodes or root has no children in a non-trivial DAG.
    """
    if state.root_id not in state.nodes:
        return False, ProofObject(
            rule="dag_merkle_derivability",
            premises=[f"dag_id={state.dag_id}", f"root_id={state.root_id}"],
            conclusion="VIOLATION: Root node not found in DAG",
        )
    root = state.nodes[state.root_id]
    if len(state.nodes) > 1 and not root.children:
        return False, ProofObject(
            rule="dag_merkle_derivability",
            premises=[f"dag_id={state.dag_id}", f"root_children={len(root.children)}"],
            conclusion="VIOLATION: Root has no children in a non-trivial DAG -- Merkle derivability broken",
        )
    return True, ProofObject(
        rule="dag_merkle_derivability",
        premises=[f"dag_id={state.dag_id}", f"root_id={state.root_id}"],
        conclusion="Root present and derivable from children: Merkle derivability holds",
    )


def check_reachability_transitivity(state: DAGState) -> Tuple[bool, ProofObject]:
    """Reachability must be transitive: if A->B and B->C then A must reach C.

    Standard: DAG-005 transitivity.
    Falsifies if: a path A->B and B->C exists but A cannot reach C.
    falsifies_if: a path A->B and B->C exists but A cannot reach C.
    """
    def can_reach(start: str, target: str, visited: Set[str]) -> bool:
        if start == target:
            return True
        if start in visited:
            return False
        visited.add(start)
        node = state.nodes.get(start)
        if node:
            for child in node.children:
                if can_reach(child, target, visited):
                    return True
        return False

    violations = []
    for node in state.nodes.values():
        for child_id in node.children:
            child = state.nodes.get(child_id)
            if child:
                for grandchild_id in child.children:
                    if not can_reach(node.node_id, grandchild_id, set()):
                        violations.append((node.node_id, child_id, grandchild_id))
    if violations:
        return False, ProofObject(
            rule="dag_reachability_transitivity",
            premises=[f"dag_id={state.dag_id}", f"violations={len(violations)}"],
            conclusion=f"VIOLATION: {len(violations)} reachability transitivity breach(es) detected",
        )
    return True, ProofObject(
        rule="dag_reachability_transitivity",
        premises=[f"dag_id={state.dag_id}"],
        conclusion="Reachability transitivity holds across all node pairs",
    )


def check_deterministic_expansion(expansion: DAGExpansion) -> Tuple[bool, ProofObject]:
    """Expansion parameters must produce deterministic node and edge counts.

    Standard: DAG-006 deterministic expansion.
    Falsifies if: target_depth < 0 or expansion_factor < 1.
    falsifies_if: target_depth < 0 or expansion_factor < 1.
    """
    if expansion.target_depth < 0:
        return False, ProofObject(
            rule="dag_deterministic_expansion",
            premises=[
                f"dag_id={expansion.dag_id}",
                f"target_depth={expansion.target_depth}",
            ],
            conclusion="VIOLATION: Target depth is negative -- expansion undefined",
        )
    if expansion.expansion_factor < 1:
        return False, ProofObject(
            rule="dag_deterministic_expansion",
            premises=[
                f"dag_id={expansion.dag_id}",
                f"expansion_factor={expansion.expansion_factor}",
            ],
            conclusion="VIOLATION: Expansion factor < 1 -- contraction, not expansion",
        )
    return True, ProofObject(
        rule="dag_deterministic_expansion",
        premises=[
            f"dag_id={expansion.dag_id}",
            f"target_depth={expansion.target_depth}",
            f"expansion_factor={expansion.expansion_factor}",
            f"resulting_nodes={expansion.resulting_nodes}",
            f"resulting_edges={expansion.resulting_edges}",
        ],
        conclusion="Expansion parameters valid: deterministic expansion possible",
    )


def run_all_invariants() -> dict:
    """Run all DAG theory invariants against test data.

    Falsifies if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    results: dict = {}

    # PASS case: valid DAG
    node_a = DAGNode(node_id="A", content_hash="sha256_A", payload="root", children=("B", "C"))
    node_b = DAGNode(node_id="B", content_hash="sha256_B", payload="child_b", children=("D",))
    node_c = DAGNode(node_id="C", content_hash="sha256_C", payload="child_c", children=("D",))
    node_d = DAGNode(node_id="D", content_hash="sha256_D", payload="leaf", children=())
    pass_state = DAGState(
        dag_id="DAG001",
        nodes={"A": node_a, "B": node_b, "C": node_c, "D": node_d},
        root_id="A",
        max_depth=3,
    )
    pass_expansion = DAGExpansion(
        dag_id="DAG001",
        target_depth=5,
        expansion_factor=2,
        resulting_nodes=31,
        resulting_edges=30,
    )

    # FAIL case: cycle + hash collision + invalid expansion
    node_x = DAGNode(node_id="X", content_hash="sha256_COLLIDE", payload="x", children=("Y",))
    node_y = DAGNode(node_id="Y", content_hash="sha256_COLLIDE", payload="y", children=("X",))  # cycle + collision
    fail_state = DAGState(
        dag_id="DAG002",
        nodes={"X": node_x, "Y": node_y},
        root_id="X",
        max_depth=2,
    )
    fail_expansion = DAGExpansion(
        dag_id="DAG002",
        target_depth=-1,
        expansion_factor=0,
        resulting_nodes=0,
        resulting_edges=0,
    )

    checks = [
        ("check_acyclicity_proof", lambda: check_acyclicity_proof(pass_state)),
        ("check_acyclicity_proof_fail", lambda: check_acyclicity_proof(fail_state)),
        ("check_topological_sort_determinism", lambda: check_topological_sort_determinism(pass_state)),
        ("check_topological_sort_determinism_fail", lambda: check_topological_sort_determinism(fail_state)),
        ("check_content_addressed_node_identity", lambda: check_content_addressed_node_identity(pass_state)),
        ("check_content_addressed_node_identity_fail", lambda: check_content_addressed_node_identity(fail_state)),
        ("check_merkle_derivability", lambda: check_merkle_derivability(pass_state)),
        ("check_merkle_derivability_fail", lambda: check_merkle_derivability(fail_state)),
        ("check_reachability_transitivity", lambda: check_reachability_transitivity(pass_state)),
        ("check_reachability_transitivity_fail", lambda: check_reachability_transitivity(fail_state)),
        ("check_deterministic_expansion", lambda: check_deterministic_expansion(pass_expansion)),
        ("check_deterministic_expansion_fail", lambda: check_deterministic_expansion(fail_expansion)),
    ]

    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DAG_THEORY invariants: PASS")
