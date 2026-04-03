"""ARC-style pattern recognition helpers with proof objects for PR #84."""

from __future__ import annotations

import hashlib
import json
import zlib
from collections import Counter, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from axioms.logic import ProofObject, merkle_root_over_proofs
from axioms.number_theory import gcd_extended, is_prime, mod_peano
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from forgiveness_system.forgiveness_system import ForgivenessSystem

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
    TILE = "tile"
    CROP = "crop"
    DECOMPOSE_OBJECTS = "decompose_objects"
    COMPOSE_OBJECTS = "compose_objects"


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

    def hash(self) -> str:
        payload = json.dumps(self.cells, separators=(",", ":"), sort_keys=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

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

    def has_horizontal_symmetry(self) -> bool:
        return self.cells == self.cells[::-1]

    def has_vertical_symmetry(self) -> bool:
        return all(row == row[::-1] for row in self.cells)

    def has_rotational_symmetry(self, order: int) -> bool:
        """Return whether the grid is invariant under 180° (order=2) or 90° (order=4) rotation."""
        if order == 2:
            return Grid(_rotate_90(_rotate_90(self.cells))) == self
        if order == 4:
            return Grid(_rotate_90(self.cells)) == self
        raise ValueError("order must be 2 or 4")


@dataclass
class CompositionalRule:
    operations: List[Tuple[PrimitiveOperation, Dict]]
    condition: Optional[Callable[[Grid], bool]] = None
    complexity: int = field(init=False)

    def __post_init__(self) -> None:
        estimator = KolmogorovComplexityEstimator()
        op_string = str([(op.value, params) for op, params in self.operations])
        self.complexity = estimator.estimate(op_string)


@dataclass(frozen=True)
class ObjectComponent:
    top: int
    left: int
    color: int
    grid: Grid


GridKey = Tuple[Tuple[int, ...], ...]
MemoKey = Tuple[GridKey, GridKey, int]
PATTERN_FORGIVENESS_BASE_PATH = Path("/tmp/orthogonal_pattern_recognition_forgiveness")



def _rotate_90(cells: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*cells[::-1])]


def _count_nonzero_cells(grid: Grid) -> int:
    count = 0
    for row in grid.cells:
        for cell in row:
            if cell != 0:
                count += 1
    return count


def _extract_region_grid(grid: Grid, region: List[Tuple[int, int]]) -> ObjectComponent:
    rows = [r for r, _ in region]
    cols = [c for _, c in region]
    top, bottom = min(rows), max(rows)
    left, right = min(cols), max(cols)
    extracted = [[0 for _ in range(right - left + 1)] for _ in range(bottom - top + 1)]
    for r, c in region:
        extracted[r - top][c - left] = grid.cells[r][c]
    return ObjectComponent(top=top, left=left, color=grid.cells[rows[0]][cols[0]], grid=Grid(extracted))


def _decompose_objects(grid: Grid) -> List[ObjectComponent]:
    components = [_extract_region_grid(grid, region) for region in grid.get_contiguous_regions()]
    return sorted(components, key=lambda component: (component.top, component.left, component.color, component.grid.rows, component.grid.cols))


def _compose_objects(components: List[ObjectComponent], rows: int, cols: int) -> Grid:
    canvas = [[0 for _ in range(cols)] for _ in range(rows)]
    for component in components:
        for r in range(component.grid.rows):
            for c in range(component.grid.cols):
                value = component.grid.cells[r][c]
                target_r = component.top + r
                target_c = component.left + c
                if value != 0 and 0 <= target_r < rows and 0 <= target_c < cols:
                    canvas[target_r][target_c] = value
    return Grid(canvas)


def _persist_building_output_metadata(system: ForgivenessSystem, output_id: str) -> None:
    output = system.building_outputs[output_id]
    metadata_file = Path(system.building_path) / f"{output_id}.json"
    with open(metadata_file, "w", encoding="utf-8") as handle:
        json.dump(output.to_dict(), handle, indent=2)


def _record_inference_failure(input_output_pairs: List[Tuple[Grid, Grid]], requires_conditional_flag: bool) -> Dict[str, str]:
    PATTERN_FORGIVENESS_BASE_PATH.mkdir(parents=True, exist_ok=True)
    system = ForgivenessSystem.get_instance(base_path=str(PATTERN_FORGIVENESS_BASE_PATH))
    evidence = json.dumps(
        {
            "pair_count": len(input_output_pairs),
            "requires_conditional": requires_conditional_flag,
            "input_shapes": [(inp.rows, inp.cols) for inp, _ in input_output_pairs],
            "output_shapes": [(out.rows, out.cols) for _, out in input_output_pairs],
        },
        sort_keys=True,
    )
    violation_id = system.log_violation(
        description="Pattern inference failed to find a compositional rule",
        system_source="axioms/pattern_recognition.py",
        evidence=evidence,
    )
    fork_id = system.create_state_fork(violation_id)
    fork = system.forks[fork_id]
    fork.building_context.update(
        {
            "features_built": [
                "expand_pattern_primitive_vocabulary",
                "expand_pattern_property_detectors",
            ],
            "pair_count": len(input_output_pairs),
        }
    )
    system.redirect_energy_to_building(fork_id)
    building_output = system.execute_building_workflow(fork_id, output_type="feature")
    output_id: Optional[str] = None
    if building_output is not None:
        system.building_outputs[building_output.id] = building_output
        _persist_building_output_metadata(system, building_output.id)
        output_id = building_output.id
    return {"violation_id": violation_id, "fork_id": fork_id, "building_output_id": output_id or ""}



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


def _rarest_color(grid: Grid) -> int:
    histogram = grid.get_color_histogram()
    return min(histogram, key=histogram.get) if histogram else 0


def _largest_region_size(grid: Grid) -> int:
    regions = grid.get_contiguous_regions()
    return max((len(region) for region in regions), default=0)


def _nonzero_count(grid: Grid) -> int:
    return _count_nonzero_cells(grid)


def _is_row_count_prime(grid: Grid) -> int:
    prime, _ = is_prime(grid.rows)
    return int(prime)


def _dimension_gcd(grid: Grid) -> int:
    (gcd_value, _, _), _ = gcd_extended(grid.rows, grid.cols)
    return gcd_value


def _property_detectors() -> List[Callable[[Grid], int]]:
    return [
        lambda grid: grid.rows,
        lambda grid: grid.cols,
        lambda grid: grid.rows * grid.cols,
        lambda grid: int(grid.rows == grid.cols),
        _nonzero_count,
        lambda grid: len(grid.get_contiguous_regions()),
        lambda grid: len(grid.get_color_histogram()),
        _dominant_color,
        _rarest_color,
        _largest_region_size,
        lambda grid: int(grid.has_horizontal_symmetry()),
        lambda grid: int(grid.has_vertical_symmetry()),
        lambda grid: mod_peano(_nonzero_count(grid), 2),
        _is_row_count_prime,
        _dimension_gcd,
    ]


def _crop_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if out.rows == 0 or out.cols == 0:
        return None
    for top in range(inp.rows - out.rows + 1):
        for left in range(inp.cols - out.cols + 1):
            cropped = [row[left:left + out.cols] for row in inp.cells[top:top + out.rows]]
            if cropped == out.cells:
                return {"top": top, "left": left, "height": out.rows, "width": out.cols}
    return None


def _fill_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if inp.rows != out.rows or inp.cols != out.cols:
        return None
    source = None
    target = None
    changed = False
    for r in range(inp.rows):
        for c in range(inp.cols):
            src = inp.cells[r][c]
            dst = out.cells[r][c]
            if src == dst:
                continue
            changed = True
            if source is None:
                source = src
                target = dst
            if src != source or dst != target:
                return None
    if not changed or source is None or target is None or source == target:
        return None
    candidate = CompositionalRule([(PrimitiveOperation.FILL, {"source": source, "target": target})])
    return {"source": source, "target": target} if apply_rule(candidate, inp) == out else None


def _translate_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if inp.rows != out.rows or inp.cols != out.cols:
        return None
    for dy in range(-inp.rows + 1, inp.rows):
        for dx in range(-inp.cols + 1, inp.cols):
            if dx == 0 and dy == 0:
                continue
            candidate = CompositionalRule([(PrimitiveOperation.TRANSLATE, {"dx": dx, "dy": dy, "fill": 0})])
            if apply_rule(candidate, inp) == out:
                return {"dx": dx, "dy": dy, "fill": 0}
    return None


def _tile_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if inp.rows == 0 or inp.cols == 0:
        return None
    if out.rows % inp.rows != 0 or out.cols % inp.cols != 0:
        return None
    repeat_y = out.rows // inp.rows
    repeat_x = out.cols // inp.cols
    candidate = CompositionalRule([(PrimitiveOperation.TILE, {"repeat_x": repeat_x, "repeat_y": repeat_y})])
    return {"repeat_x": repeat_x, "repeat_y": repeat_y} if apply_rule(candidate, inp) == out else None


def _scale_params(inp: Grid, out: Grid) -> Optional[Dict[str, int]]:
    if inp.rows == 0 or inp.cols == 0:
        return None
    if out.rows % inp.rows != 0 or out.cols % inp.cols != 0:
        return None
    factor_y = out.rows // inp.rows
    factor_x = out.cols // inp.cols
    if factor_x != factor_y or factor_x <= 0:
        return None
    candidate = CompositionalRule([(PrimitiveOperation.SCALE, {"factor": factor_x})])
    return {"factor": factor_x} if apply_rule(candidate, inp) == out else None


def _infer_per_object_rule(inp: Grid, out: Grid, max_depth: int = 2) -> Optional[CompositionalRule]:
    input_objects = _decompose_objects(inp)
    output_objects = _decompose_objects(out)
    if len(input_objects) < 2 or len(input_objects) != len(output_objects):
        return None
    if any((source.top, source.left) != (target.top, target.left) for source, target in zip(input_objects, output_objects)):
        return None
    object_candidates = _candidate_rules_with_depth(
        input_objects[0].grid,
        output_objects[0].grid,
        max_depth=max(1, min(max_depth, 2)),
    )
    for candidate in object_candidates:
        if not all(apply_rule(candidate, source.grid) == target.grid for source, target in zip(input_objects, output_objects)):
            continue
        rule = CompositionalRule(
            [
                (PrimitiveOperation.DECOMPOSE_OBJECTS, {}),
                (
                    PrimitiveOperation.COMPOSE_OBJECTS,
                    {"object_rule": candidate, "canvas_rows": out.rows, "canvas_cols": out.cols},
                ),
            ]
        )
        if apply_rule(rule, inp) == out:
            return rule
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


def _suffix_rules() -> List[CompositionalRule]:
    return [
        CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
        CompositionalRule([(PrimitiveOperation.ROTATE_180, {})]),
        CompositionalRule([(PrimitiveOperation.ROTATE_270, {})]),
        CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
        CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
    ]


def _freeze(value):
    """Convert nested rule/grid/object state into hashable structural tuples for memoization."""
    if isinstance(value, CompositionalRule):
        return tuple((operation.value, _freeze(params)) for operation, params in value.operations)
    if isinstance(value, Grid):
        return _grid_key(value)
    if isinstance(value, ObjectComponent):
        return (value.top, value.left, value.color, _grid_key(value.grid))
    if isinstance(value, dict):
        return tuple(sorted((key, _freeze(inner)) for key, inner in value.items()))
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _rule_key(rule: CompositionalRule) -> Tuple[Tuple[str, object], ...]:
    return tuple((operation.value, _freeze(params)) for operation, params in rule.operations)


def _operations_key(operations: List[Tuple[PrimitiveOperation, Dict]]) -> Tuple[Tuple[str, object], ...]:
    return tuple((operation.value, _freeze(params)) for operation, params in operations)


def _grid_key(grid: Grid) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in grid.cells)


def _inverse_single_step_rule(rule: CompositionalRule) -> Optional[CompositionalRule]:
    if len(rule.operations) != 1:
        return None
    operation, params = rule.operations[0]
    if operation == PrimitiveOperation.ROTATE_90:
        return CompositionalRule([(PrimitiveOperation.ROTATE_270, {})])
    if operation == PrimitiveOperation.ROTATE_180:
        return CompositionalRule([(PrimitiveOperation.ROTATE_180, {})])
    if operation == PrimitiveOperation.ROTATE_270:
        return CompositionalRule([(PrimitiveOperation.ROTATE_90, {})])
    if operation == PrimitiveOperation.REFLECT_H:
        return CompositionalRule([(PrimitiveOperation.REFLECT_H, {})])
    if operation == PrimitiveOperation.REFLECT_V:
        return CompositionalRule([(PrimitiveOperation.REFLECT_V, {})])
    if operation == PrimitiveOperation.RECOLOR:
        mapping = params.get("mapping", {})
        inverse_mapping: Dict[int, int] = {}
        for src, dst in mapping.items():
            if dst in inverse_mapping:
                return None
            inverse_mapping[dst] = src
        return CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": inverse_mapping})])
    return None


def _candidate_rules_with_depth(
    inp: Grid,
    out: Grid,
    max_depth: int,
    memo: Optional[Dict[MemoKey, List[CompositionalRule]]] = None,
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
            key = _operations_key(operations)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(CompositionalRule(operations))
    for suffix in _suffix_rules():
        inverse_suffix = _inverse_single_step_rule(suffix)
        if inverse_suffix is None:
            continue
        intermediate = apply_rule(inverse_suffix, out)
        for prefix in _candidate_rules_with_depth(inp, intermediate, max_depth - 1, memo):
            operations = prefix.operations + suffix.operations
            key = _operations_key(operations)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(CompositionalRule(operations))
    memo[memo_key] = candidates
    return candidates



def apply_rule(rule: CompositionalRule, grid: Grid) -> Grid:
    current: Any = grid.copy()
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
        elif operation == PrimitiveOperation.DECOMPOSE_OBJECTS:
            if not isinstance(current, Grid):
                raise ValueError("DECOMPOSE_OBJECTS expects a Grid")
            current = {
                "canvas_rows": current.rows,
                "canvas_cols": current.cols,
                "objects": _decompose_objects(current),
            }
        elif operation == PrimitiveOperation.COMPOSE_OBJECTS:
            if not isinstance(current, dict):
                raise ValueError("COMPOSE_OBJECTS expects decomposed object state")
            components = current.get("objects", [])
            if not isinstance(components, list):
                raise ValueError("COMPOSE_OBJECTS expects an object list")
            object_rule = params.get("object_rule")
            transformed_components: List[ObjectComponent] = []
            for component in components:
                if not isinstance(component, ObjectComponent):
                    raise ValueError("COMPOSE_OBJECTS received an invalid component")
                transformed_grid = apply_rule(object_rule, component.grid) if isinstance(object_rule, CompositionalRule) else component.grid
                transformed_components.append(
                    ObjectComponent(
                        top=component.top,
                        left=component.left,
                        color=_dominant_color(transformed_grid),
                        grid=transformed_grid,
                    )
                )
            canvas_rows = int(params.get("canvas_rows", current.get("canvas_rows", 0)))
            canvas_cols = int(params.get("canvas_cols", current.get("canvas_cols", 0)))
            current = _compose_objects(transformed_components, canvas_rows, canvas_cols)
        elif operation == PrimitiveOperation.FILL:
            source = params.get("source")
            target = params.get("target", source)
            current = Grid([[target if cell == source else cell for cell in row] for row in current.cells])
        elif operation == PrimitiveOperation.TILE:
            repeat_x = int(params.get("repeat_x", 1))
            repeat_y = int(params.get("repeat_y", 1))
            tiled: List[List[int]] = []
            for _ in range(repeat_y):
                for row in current.cells:
                    tiled.append(row * repeat_x)
            current = Grid(tiled)
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
            nonzero = _count_nonzero_cells(current)
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
    fill_params = _fill_params(inp, out)
    if fill_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.FILL, fill_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    translate_params = _translate_params(inp, out)
    if translate_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.TRANSLATE, translate_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    tile_params = _tile_params(inp, out)
    if tile_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.TILE, tile_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    scale_params = _scale_params(inp, out)
    if scale_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.SCALE, scale_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    crop_params = _crop_params(inp, out)
    if crop_params is not None:
        rule = CompositionalRule([(PrimitiveOperation.CROP, crop_params)])
        if apply_rule(rule, inp) == out:
            candidates.append(rule)
    per_object_rule = _infer_per_object_rule(inp, out)
    if per_object_rule is not None:
        candidates.append(per_object_rule)
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



def infer_conditional_rule(
    pairs: List[Tuple[Grid, Grid]],
    properties: List[Callable[[Grid], int]],
    max_composition_depth: int = 1,
) -> Optional[CompositionalRule]:
    for prop in properties:
        grouped: Dict[int, List[Tuple[Grid, Grid]]] = {}
        for inp, out in pairs:
            grouped.setdefault(prop(inp), []).append((inp, out))
        value_rules: Dict[int, CompositionalRule] = {}
        valid = True
        for value, group in grouped.items():
            rule, _ = detect_compositional_rule(
                group,
                max_composition_depth=max(1, max_composition_depth - 1),
                record_failure=False,
            )
            if rule is None:
                valid = False
                break
            value_rules[value] = rule
        if valid and len(value_rules) > 1:
            return CompositionalRule([(PrimitiveOperation.CONDITIONAL, {"property": prop, "value_rules": value_rules})])
    return None



def _select_best_rule(
    candidates: List[CompositionalRule],
    pairs: List[Tuple[Grid, Grid]],
) -> CompositionalRule:
    """Select the best rule using ordered composition search with MDL tiebreaker.

    The plain MDL selector (min complexity) can pick a simpler single-step rule
    that satisfies training pairs when a composed multi-step rule is actually
    required to generalise.  This function scores candidates by:
      1. Number of training pairs correctly solved (higher is better).
      2. For ties, prefer rules whose full operation chain produces exact matches
         on every pair (composition_valid flag).
      3. Among fully-valid rules, prefer lower Kolmogorov complexity (MDL).
    """
    def _score(rule: CompositionalRule) -> Tuple[int, int, int]:
        solved = sum(1 for inp, out in pairs if apply_rule(rule, inp) == out)
        composition_valid = 1 if solved == len(pairs) else 0
        return (-solved, -composition_valid, rule.complexity)

    return min(candidates, key=_score)


def detect_compositional_rule(
    input_output_pairs: List[Tuple[Grid, Grid]],
    max_composition_depth: int = 3,
    record_failure: bool = True,
) -> Tuple[Optional[CompositionalRule], ProofObject]:
    candidates: List[CompositionalRule] = []
    if not input_output_pairs:
        proof = ProofObject("PatternRuleDetection", ["No examples provided"], "No rule inferred")
        return None, proof
    requires_conditional_flag = requires_conditional(input_output_pairs)
    first_candidates = _candidate_rules_with_depth(*input_output_pairs[0], max_depth=max_composition_depth)
    for candidate in first_candidates:
        if all(apply_rule(candidate, inp) == out for inp, out in input_output_pairs):
            candidates.append(candidate)
    conditional = None
    if not candidates and requires_conditional_flag:
        conditional = infer_conditional_rule(input_output_pairs, _property_detectors(), max_composition_depth=max_composition_depth)
        if conditional is not None and all(apply_rule(conditional, inp) == out for inp, out in input_output_pairs):
            candidates.append(conditional)
    if not candidates:
        failure_metadata = {"violation_id": "none", "fork_id": "none", "building_output_id": "none"}
        if record_failure:
            failure_metadata = _record_inference_failure(input_output_pairs, requires_conditional_flag)
        proof = ProofObject(
            "PatternRuleDetection",
            [
                f"pairs={len(input_output_pairs)}",
                f"requires_conditional={requires_conditional_flag}",
                f"forgiveness_violation_id={failure_metadata['violation_id']}",
                f"forgiveness_fork_id={failure_metadata['fork_id']}",
                f"forgiveness_building_output_id={failure_metadata['building_output_id']}",
            ],
            "No compositional rule inferred",
        )
        return None, proof
    rule = _select_best_rule(candidates, input_output_pairs)
    candidate_complexities = sorted(candidate.complexity for candidate in candidates)
    proof = ProofObject(
        "PatternRuleDetection",
        [
            f"candidate_count={len(candidates)}",
            f"candidate_complexities={candidate_complexities}",
            "selection_strategy=minimum_description_length",
            f"selected_complexity={rule.complexity}",
        ],
        f"Inferred rule with operations {[op.value for op, _ in rule.operations]}",
    )
    claim = YeshuaClaim(
        source="axioms/pattern_recognition.py",
        statement=proof.conclusion,
        derivation=proof,
    )
    violations = verify_yeshua_standard(claim)
    if violations:
        rejection_proof = ProofObject(
            "PatternRuleDetection",
            [violation.detail for violation in violations],
            "Rule rejected by Yeshua standard",
        )
        return None, rejection_proof
    proof = ProofObject(
        "PatternRuleDetection",
        proof.premises + [f"yeshua_hash_commitment={claim.hash_commitment}", "yeshua_violations=0"],
        proof.conclusion,
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
