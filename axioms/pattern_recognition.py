"""ARC-style pattern recognition helpers with proof objects for PR #84."""

from __future__ import annotations

import zlib
from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from axioms.logic import ProofObject, merkle_root_over_proofs

try:
    from minimal_ai_ide.maximal_oracle_v57 import KolmogorovComplexityEstimator  # type: ignore
except Exception:  # pragma: no cover - environment fallback
    class KolmogorovComplexityEstimator:  # type: ignore
        def estimate(self, content: str) -> int:
            return len(zlib.compress(content.encode("utf-8")))


class PrimitiveOperation(Enum):
    IDENTITY = "identity"
    ROTATE_90 = "rotate_90"
    ROTATE_180 = "rotate_180"
    ROTATE_270 = "rotate_270"
    REFLECT_H = "reflect_horizontal"
    REFLECT_V = "reflect_vertical"
    TRANSLATE = "translate"
    RECOLOR = "recolor"
    EXTRACT_OBJECT = "extract_object"
    DETECT_BOUNDARY = "detect_boundary"
    COUNT = "count"
    CONDITIONAL = "conditional"
    SCALE = "scale"
    FILL = "fill"
    CROP = "crop"


@dataclass
class Grid:
    cells: List[List[int]]
    rows: int = field(init=False)
    cols: int = field(init=False)

    def __post_init__(self) -> None:
        self.rows = len(self.cells)
        self.cols = len(self.cells[0]) if self.cells else 0

    def copy(self) -> "Grid":
        return Grid([row[:] for row in self.cells])

    def __eq__(self, other):
        return isinstance(other, Grid) and self.cells == other.cells

    def get_color_histogram(self) -> Dict[int, int]:
        counts: Counter[int] = Counter()
        for row in self.cells:
            counts.update(row)
        return dict(counts)

    def get_contiguous_regions(self) -> List[List[Tuple[int, int]]]:
        seen = set()
        regions: List[List[Tuple[int, int]]] = []
        for r in range(self.rows):
            for c in range(self.cols):
                color = self.cells[r][c]
                if color == 0 or (r, c) in seen:
                    continue
                region: List[Tuple[int, int]] = []
                queue = deque([(r, c)])
                seen.add((r, c))
                while queue:
                    cr, cc = queue.popleft()
                    region.append((cr, cc))
                    for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in seen and self.cells[nr][nc] == color:
                            seen.add((nr, nc))
                            queue.append((nr, nc))
                regions.append(region)
        return regions

    def get_boundary(self, region: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        boundary: List[Tuple[int, int]] = []
        region_set = set(region)
        for r, c in region:
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if not (0 <= nr < self.rows and 0 <= nc < self.cols) or (nr, nc) not in region_set:
                    boundary.append((r, c))
                    break
        return boundary


@dataclass
class CompositionalRule:
    operations: List[Tuple[PrimitiveOperation, Dict]]
    condition: Optional[Callable[[Grid], bool]] = None
    complexity: int = field(init=False)

    def __post_init__(self) -> None:
        estimator = KolmogorovComplexityEstimator()
        op_string = str([(op.value, params) for op, params in self.operations])
        self.complexity = estimator.estimate(op_string)



def _rotate_90(cells: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*cells[::-1])]



def _recolor_mapping(inp: Grid, out: Grid) -> Optional[Dict[int, int]]:
    if inp.rows != out.rows or inp.cols != out.cols:
        return None
    mapping: Dict[int, int] = {}
    for r in range(inp.rows):
        for c in range(inp.cols):
            src = inp.cells[r][c]
            dst = out.cells[r][c]
            if src in mapping and mapping[src] != dst:
                return None
            mapping[src] = dst
    return mapping


def _dominant_color(grid: Grid) -> int:
    histogram = grid.get_color_histogram()
    return max(histogram, key=histogram.get) if histogram else 0


def _property_detectors() -> List[Callable[[Grid], int]]:
    return [
        lambda grid: grid.rows,
        lambda grid: grid.cols,
        lambda grid: grid.rows * grid.cols,
        lambda grid: int(grid.rows == grid.cols),
        lambda grid: sum(1 for row in grid.cells for cell in row if cell != 0),
        lambda grid: len(grid.get_contiguous_regions()),
        lambda grid: len(grid.get_color_histogram()),
        _dominant_color,
    ]


def _crop_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if out.rows == 0 or out.cols == 0 or out.rows > inp.rows or out.cols > inp.cols:
        return None
    for top in range(inp.rows - out.rows + 1):
        for left in range(inp.cols - out.cols + 1):
            cropped = [row[left:left + out.cols] for row in inp.cells[top:top + out.rows]]
            if cropped == out.cells:
                return {"top": top, "left": left, "height": out.rows, "width": out.cols}
    return None


def _prefix_rules() -> List[CompositionalRule]:
    return [
        CompositionalRule([(PrimitiveOperation.IDENTITY, {})]),
        CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
        CompositionalRule([(PrimitiveOperation.ROTATE_180, {})]),
        CompositionalRule([(PrimitiveOperation.ROTATE_270, {})]),
        CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
        CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
        CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
        CompositionalRule([(PrimitiveOperation.EXTRACT_OBJECT, {})]),
        CompositionalRule([(PrimitiveOperation.COUNT, {})]),
    ]


def _freeze(value):
    if isinstance(value, dict):
        return tuple(sorted((key, _freeze(inner)) for key, inner in value.items()))
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _rule_key(rule: CompositionalRule) -> Tuple[Tuple[str, object], ...]:
    return tuple((operation.value, _freeze(params)) for operation, params in rule.operations)


def _grid_key(grid: Grid) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in grid.cells)


def _candidate_rules_with_depth(
    inp: Grid,
    out: Grid,
    max_depth: int,
    memo: Optional[Dict[Tuple[Tuple[Tuple[int, ...], ...], Tuple[Tuple[int, ...], ...], int], List[CompositionalRule]]] = None,
) -> List[CompositionalRule]:
    if memo is None:
        memo = {}
    memo_key = (_grid_key(inp), _grid_key(out), max_depth)
    if memo_key in memo:
        return memo[memo_key]

    candidates = list(_candidate_rules_for_pair(inp, out))
    if max_depth <= 1:
        memo[memo_key] = candidates
        return candidates

    seen = {_rule_key(rule) for rule in candidates}
    for prefix in _prefix_rules():
        intermediate = apply_rule(prefix, inp)
        for suffix in _candidate_rules_with_depth(intermediate, out, max_depth - 1, memo):
            operations = prefix.operations + suffix.operations
            key = tuple((operation.value, _freeze(params)) for operation, params in operations)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(CompositionalRule(operations))
    memo[memo_key] = candidates
    return candidates



def apply_rule(rule: CompositionalRule, grid: Grid) -> Grid:
    current = grid.copy()
    for operation, params in rule.operations:
        if operation == PrimitiveOperation.IDENTITY:
            current = current.copy()
        elif operation == PrimitiveOperation.ROTATE_90:
            current = Grid(_rotate_90(current.cells))
        elif operation == PrimitiveOperation.ROTATE_180:
            current = Grid(_rotate_90(_rotate_90(current.cells)))
        elif operation == PrimitiveOperation.ROTATE_270:
            current = Grid(_rotate_90(_rotate_90(_rotate_90(current.cells))))
        elif operation == PrimitiveOperation.REFLECT_H:
            current = Grid(current.cells[::-1])
        elif operation == PrimitiveOperation.REFLECT_V:
            current = Grid([row[::-1] for row in current.cells])
        elif operation == PrimitiveOperation.RECOLOR:
            mapping = params.get("mapping", {})
            current = Grid([[mapping.get(cell, cell) for cell in row] for row in current.cells])
        elif operation == PrimitiveOperation.TRANSLATE:
            dx = params.get("dx", 0)
            dy = params.get("dy", 0)
            fill = params.get("fill", 0)
            translated = [[fill for _ in range(current.cols)] for _ in range(current.rows)]
            for r in range(current.rows):
                for c in range(current.cols):
                    nr, nc = r + dy, c + dx
                    if 0 <= nr < current.rows and 0 <= nc < current.cols:
                        translated[nr][nc] = current.cells[r][c]
            current = Grid(translated)
        elif operation == PrimitiveOperation.CROP:
            top = params.get("top", 0)
            left = params.get("left", 0)
            height = params.get("height", current.rows)
            width = params.get("width", current.cols)
            current = Grid([row[left:left + width] for row in current.cells[top:top + height]])
        elif operation == PrimitiveOperation.FILL:
            source = params.get("source")
            target = params.get("target", source)
            current = Grid([[target if cell == source else cell for cell in row] for row in current.cells])
        elif operation == PrimitiveOperation.EXTRACT_OBJECT:
            regions = current.get_contiguous_regions()
            largest = max(regions, key=len, default=[])
            if not largest:
                current = Grid([[0]])
            else:
                rows = [r for r, _ in largest]
                cols = [c for _, c in largest]
                top, bottom = min(rows), max(rows)
                left, right = min(cols), max(cols)
                extracted = [row[left:right + 1] for row in current.cells[top:bottom + 1]]
                current = Grid(extracted)
        elif operation == PrimitiveOperation.DETECT_BOUNDARY:
            output = [[0 for _ in range(current.cols)] for _ in range(current.rows)]
            for region in current.get_contiguous_regions():
                for r, c in current.get_boundary(region):
                    output[r][c] = current.cells[r][c]
            current = Grid(output)
        elif operation == PrimitiveOperation.COUNT:
            nonzero = sum(1 for row in current.cells for cell in row if cell != 0)
            current = Grid([[nonzero]])
        elif operation == PrimitiveOperation.SCALE:
            factor = int(params.get("factor", 2))
            if factor <= 0:
                raise ValueError("scale factor must be positive")
            scaled: List[List[int]] = []
            for row in current.cells:
                expanded = []
                for cell in row:
                    expanded.extend([cell] * factor)
                for _ in range(factor):
                    scaled.append(expanded[:])
            current = Grid(scaled)
        elif operation == PrimitiveOperation.CONDITIONAL:
            prop = params["property"]
            value_rules = params["value_rules"]
            default_rule = params.get("default_rule")
            key = prop(current)
            selected = value_rules.get(key, default_rule)
            if selected is None:
                return current
            current = apply_rule(selected, current)
    return current



def _candidate_rules_for_pair(inp: Grid, out: Grid) -> List[CompositionalRule]:
    candidates: List[CompositionalRule] = []
    for operation in (
        PrimitiveOperation.IDENTITY,
        PrimitiveOperation.ROTATE_90,
        PrimitiveOperation.ROTATE_180,
        PrimitiveOperation.ROTATE_270,
        PrimitiveOperation.REFLECT_H,
        PrimitiveOperation.REFLECT_V,
        PrimitiveOperation.DETECT_BOUNDARY,
        PrimitiveOperation.EXTRACT_OBJECT,
        PrimitiveOperation.COUNT,
    ):
        rule = CompositionalRule([(operation, {})])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    mapping = _recolor_mapping(inp, out)
    if mapping is not None:
        rule = CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": mapping})])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    crop_params = _crop_params(inp, out)
    if crop_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.CROP, crop_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    return candidates



def requires_conditional(pairs: List[Tuple[Grid, Grid]]) -> bool:
    if len(pairs) < 2:
        return False
    operation_signatures = []
    for inp, out in pairs:
        candidates = _candidate_rules_for_pair(inp, out)
        operation_signatures.append(tuple(rule.operations[0][0] for rule in candidates[:2]))
    first = operation_signatures[0]
    return any(signature != first for signature in operation_signatures[1:])



def infer_conditional_rule(pairs: List[Tuple[Grid, Grid]], properties: List[Callable[[Grid], int]]) -> Optional[CompositionalRule]:
    for prop in properties:
        grouped: Dict[int, List[Tuple[Grid, Grid]]] = {}
        for inp, out in pairs:
            grouped.setdefault(prop(inp), []).append((inp, out))
        value_rules: Dict[int, CompositionalRule] = {}
        valid = True
        for value, group in grouped.items():
            rule, _ = detect_compositional_rule(group, max_composition_depth=1)
            if rule is None:
                valid = False
                break
            value_rules[value] = rule
        if valid and len(value_rules) > 1:
            return CompositionalRule([(PrimitiveOperation.CONDITIONAL, {"property": prop, "value_rules": value_rules})])
    return None



def detect_compositional_rule(input_output_pairs: List[Tuple[Grid, Grid]], max_composition_depth: int = 3) -> Tuple[Optional[CompositionalRule], ProofObject]:
    candidates: List[CompositionalRule] = []
    if not input_output_pairs:
        proof = ProofObject("PatternRuleDetection", ["No examples provided"], "No rule inferred")
        return None, proof
    first_candidates = _candidate_rules_with_depth(*input_output_pairs[0], max_depth=max_composition_depth)
    for candidate in first_candidates:
        if all(apply_rule(candidate, inp) == out for inp, out in input_output_pairs):
            candidates.append(candidate)
    conditional = None
    if not candidates and requires_conditional(input_output_pairs):
        conditional = infer_conditional_rule(input_output_pairs, _property_detectors())
        if conditional is not None and all(apply_rule(conditional, inp) == out for inp, out in input_output_pairs):
            candidates.append(conditional)
    if not candidates:
        proof = ProofObject(
            "PatternRuleDetection",
            [f"pairs={len(input_output_pairs)}", f"requires_conditional={requires_conditional(input_output_pairs)}"],
            "No compositional rule inferred",
        )
        return None, proof
    rule = min(candidates, key=lambda candidate: candidate.complexity)
    proof = ProofObject(
        "PatternRuleDetection",
        [f"candidate_count={len(candidates)}", f"selected_complexity={rule.complexity}"],
        f"Inferred rule with operations {[op.value for op, _ in rule.operations]}",
    )
    return rule, proof



def verify_rule(rule: CompositionalRule, test_pairs: List[Tuple[Grid, Grid]]) -> Tuple[bool, ProofObject]:
    results = []
    for inp, expected in test_pairs:
        actual = apply_rule(rule, inp)
        results.append(actual == expected)
    all_correct = all(results)
    proof = ProofObject(
        rule="pattern_recognition_verification",
        premises=[f"Rule complexity: {rule.complexity}", f"Test pairs: {len(test_pairs)}", f"Results: {results}"],
        conclusion=f"Rule {'verified' if all_correct else 'falsified'} on {len(test_pairs)} test pairs",
    )
    return all_correct, proof



def verify_pattern_recognition_with_evidence(rule: CompositionalRule, test_pairs: List[Tuple[Grid, Grid]]) -> Dict[str, object]:
    ok, proof = verify_rule(rule, test_pairs)
    return {
        "verified": ok,
        "proof_hash": proof.proof_hash,
        "merkle_root": merkle_root_over_proofs([proof]),
    }
