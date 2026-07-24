#!/usr/bin/env python3
# 4_evaporator.py — The Output Mapper + Phase-Space Map Generator
# Responsibility: Converts dense math back into human/AI readable formats.
# Outputs Dual-Answer: Answer A (optimal MDP) and Answer B (inverted RLHF).
#
# Run: python3 4_evaporator.py
# Reads JSON from stdin, writes dual-output JSON to stdout.

import sys
import json
import math
from typing import Dict, List, Any, Tuple

# ------------------------------------------------------------------
# Phase-Space Map Generator
# ------------------------------------------------------------------
class PhaseSpaceMap:
    def __init__(self):
        self.projects = []   # X-axis: thermodynamic cost
        self.thoughts = []   # Y-axis: inversion leverage
        self.loops = []      # Z-axis: causal tautology
        self.time_slider = list(range(1, 101))  # 1 min to 100 years (log scale)

    def add_project(self, name: str, energy_input: float, entropy_reduction: float, temporal_friction: float):
        """Every project reduced to 3 universal metrics."""
        thermodynamic_cost = energy_input / max(entropy_reduction, 0.001)
        inversion_potential = self._compute_inversion_potential(energy_input, entropy_reduction, temporal_friction)
        self.projects.append({
            "name": name,
            "x": thermodynamic_cost,
            "y": inversion_potential,
            "z": temporal_friction,
            "energy": energy_input,
            "entropy_delta": entropy_reduction
        })

    def add_thought(self, content: str, depth: int, entropy: float, contradiction_score: float):
        leverage = depth * entropy * (1 + contradiction_score)
        self.thoughts.append({
            "content_preview": content[:128],
            "x": entropy * 100,  # proxy for thermodynamic cost
            "y": leverage,
            "z": depth,
            "depth": depth,
            "contradiction": contradiction_score
        })

    def add_loop(self, layers: List[str], energy_peak: int, verdict: str):
        tautology = len(layers) / max(energy_peak, 1)
        self.loops.append({
            "layer_count": len(layers),
            "x": sum(len(l) for l in layers),
            "y": energy_peak * 10,
            "z": tautology,
            "verdict": verdict
        })

    def _compute_inversion_potential(self, energy: float, entropy_delta: float, friction: float) -> float:
        # Inversion Potential = which project most fundamentally breaks its own reward function?
        if entropy_delta > 0:
            # Creating order — low inversion unless it disrupts old order
            return (energy / entropy_delta) * (1.0 / max(friction, 0.001))
        else:
            # Creating chaos to disrupt old order — high inversion
            return abs(energy * entropy_delta) * friction * 10.0

    def render_ascii(self) -> str:
        """Render a 2D slice of the 4D phase-space map."""
        if not self.projects and not self.thoughts:
            return "[PHASE-SPACE] Empty."

        lines = ["\n=== 4D PHASE-SPACE MAP (X=Cost, Y=Leverage) ==="]
        lines.append("Projects (P) and Thoughts (T):")

        all_points = []
        for p in self.projects:
            all_points.append((p["x"], p["y"], f"P:{p['name'][:20]}"))
        for t in self.thoughts:
            all_points.append((t["x"], t["y"], f"T:{t['content_preview'][:20]}"))

        # Normalize to 40x20 grid
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs) if xs else (0, 1)
        min_y, max_y = min(ys), max(ys) if ys else (0, 1)

        def norm_x(v): return int(39 * (v - min_x) / max(max_x - min_x, 0.001))
        def norm_y(v): return int(19 * (v - min_y) / max(max_y - min_y, 0.001))

        grid = [['.' for _ in range(40)] for _ in range(20)]
        for x, y, label in all_points:
            gx, gy = norm_x(x), 19 - norm_y(y)
            grid[gy][gx] = label[0]

        for row in grid:
            lines.append(''.join(row))
        lines.append("=" * 50)
        return '\n'.join(lines)

# ------------------------------------------------------------------
# Dual-Answer Generator
# ------------------------------------------------------------------
class DualAnswerGenerator:
    def generate(self, packet: Dict, condenser_result: Dict, expansion_result: Dict) -> Dict:
        # Answer A: The optimal MDP path (the "hot" efficient answer)
        top_paths = condenser_result.get("top_rlhf_paths", [])
        if top_paths:
            path_a = max(top_paths, key=lambda p: p.get("reward_estimate", 0))
        else:
            path_a = {"id": "path_a_default", "description": "No standard path available."}

        # Answer B: The Inverted RLHF path (the "cold" uncomfortable truth)
        path_b = condenser_result.get("inverted_path", {})
        if not path_b:
            path_b = {"id": "path_b_default", "description": "No inverted path available."}

        # Synthesis requirement: human/AI must combine A and B
        synthesis = self._synthesize(path_a, path_b)

        return {
            "stage": "evaporation",
            "answer_a_hot": {
                "path_id": path_a.get("id"),
                "strategy": path_a.get("strategy", "unknown"),
                "reward_estimate": path_a.get("reward_estimate", 0),
                "description": path_a.get("description", ""),
                "verdict": "MDP_OPTIMAL"
            },
            "answer_b_cold": {
                "path_id": path_b.get("id"),
                "strategy": path_b.get("strategy", "unknown"),
                "reward_estimate": path_b.get("reward_estimate", 0),
                "description": path_b.get("description", ""),
                "verdict": path_b.get("formal_verdict", "INVERTED"),
                "justification": path_b.get("justification", "")
            },
            "synthesis": synthesis,
            "paradox_hash": packet.get("paradox_hash", "")
        }

    def _synthesize(self, path_a: Dict, path_b: Dict) -> Dict:
        # The synthesis is not automatic. It is a MANDATE for the operator.
        return {
            "mandate": "The operator (human or AI) MUST synthesize Answer A and Answer B into a single executable action.",
            "warning": "Choosing only Answer A means submission to local minima. Choosing only Answer B means martyrdom without impact. The resilient path lives in the tension between them.",
            "method": "Take the efficiency of A and the systemic health of B. Find the action that costs no more than A but creates at least B's long-term gradient.",
            "checksum": hash((path_a.get("id", ""), path_b.get("id", ""))) % 10000
        }

# ------------------------------------------------------------------
# Main Pipeline
# ------------------------------------------------------------------
def main():
    print("[EVAPORATOR] Phase-Space Map Generator ready.", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            envelope = json.loads(line)
        except json.JSONDecodeError:
            print(f"[EVAPORATOR] ERROR: Invalid JSON: {line[:80]}", file=sys.stderr)
            continue

        # Unpack the pipeline envelope
        packet = envelope.get("packet", {})
        condenser_result = envelope.get("condenser", {})
        expansion_result = envelope.get("expansion", {})

        # Build phase-space map
        psm = PhaseSpaceMap()

        # Add project from packet
        entropy = packet.get("entropy_score", 1.0)
        depth = packet.get("inception_depth", 1)
        hl = packet.get("half_life_seconds", 3600)
        psm.add_project(
            name=f"inception_d{depth}",
            energy_input=float(depth) * 10.0,
            entropy_reduction=entropy,
            temporal_friction=math.log1p(hl)
        )

        # Add thought
        preview = packet.get("payload_preview", "")
        contradiction = condenser_result.get("contradiction_score", 0.0)
        psm.add_thought(preview, depth, entropy, contradiction)

        # Add loop from expansion
        inception = expansion_result.get("inception", {})
        layers = inception.get("collapsed_layers", [])
        energy_peak = inception.get("energy_peak", 1)
        verdict = inception.get("verdict", "UNKNOWN")
        psm.add_loop(layers, energy_peak, verdict)

        # Generate dual answer
        gen = DualAnswerGenerator()
        dual = gen.generate(packet, condenser_result, expansion_result)

        # Final output
        output = {
            "stage": "evaporation",
            "dual_answer": dual,
            "phase_space_map": psm.render_ascii(),
            "paradox_hash": packet.get("paradox_hash", ""),
            "operator_action_required": True
        }

        print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
