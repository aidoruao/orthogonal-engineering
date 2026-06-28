"""AST-based scanner for mathematical formulas in Python source.

Instead of grepping for operators, this scanner reconstructs expressions from
the abstract syntax tree, categorising each by its algebraic shape. It focuses
on exact-arithmetic patterns (Fraction), comparisons, recurrences, and
algebraic identities.

Standard: Yeshua
"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from tools.scanners.base import Finding, Scanner, ScannerResult, _line_number, _read_text_safely


@dataclass(frozen=True)
class _ExprContext:
    """Context used to classify an extracted expression."""

    node_type: str
    parent_type: Optional[str]
    in_assignment: bool
    in_return: bool
    in_call: bool


class FormulaAstScanner(Scanner):
    """Scan Python files and extract structural mathematical formulas.

    Falsifies if: scan reports a formula whose AST cannot be re-parsed or whose
    source span is empty.
    falsifies_if: scan reports a formula whose AST cannot be re-parsed or whose
    source span is empty.
    """

    name = "formula_ast"

    # Operators that indicate genuine mathematical structure rather than
    # incidental arithmetic.
    _MATH_OPS: Tuple[type, ...] = (
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )

    _COMPARISON_OPS: Tuple[type, ...] = (
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
    )

    def __init__(self) -> None:
        self._findings: List[Finding] = []

    def scan(self, root: Path) -> ScannerResult:
        """Scan all ``.py`` files under ``root`` for mathematical formulas."""
        self._findings = []
        for path in sorted(root.rglob("*.py")):
            if ".venv" in path.parts or "node_modules" in path.parts:
                continue
            self._scan_file(path)

        metadata: Dict[str, Any] = {
            "files_scanned": len(set(f.file for f in self._findings)) or 0,
            "finding_count": len(self._findings),
            "categories": sorted({f.category for f in self._findings}),
        }
        return ScannerResult(
            scanner=self.name,
            findings=tuple(self._findings),
            metadata=metadata,
        )

    def _scan_file(self, path: Path) -> None:
        source = _read_text_safely(path)
        if source is None:
            return
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return

        self._FormulaVisitor(self, path, source).visit(tree)

    class _FormulaVisitor(ast.NodeVisitor):
        def __init__(self, scanner: "FormulaAstScanner", path: Path, source: str) -> None:
            self._scanner = scanner
            self._path = path
            self._source = source
            self._parents: List[ast.AST] = []

        def visit(self, node: ast.AST) -> None:
            self._parents.append(node)
            super().visit(node)
            self._parents.pop()

        def _parent_type(self) -> Optional[str]:
            if len(self._parents) < 2:
                return None
            return type(self._parents[-2]).__name__

        def _context(self, node: ast.AST) -> _ExprContext:
            parent = self._parent_type()
            in_assignment = any(isinstance(p, ast.Assign) for p in self._parents)
            in_return = any(isinstance(p, ast.Return) for p in self._parents)
            in_call = any(isinstance(p, ast.Call) for p in self._parents)
            return _ExprContext(
                node_type=type(node).__name__,
                parent_type=parent,
                in_assignment=in_assignment,
                in_return=in_return,
                in_call=in_call,
            )

        def _record(self, node: ast.AST, category: str, kind: str, snippet: Optional[str] = None) -> None:
            text = snippet or self._source_segment(node)
            if not text or not text.strip():
                return
            ctx = self._context(node)
            self._scanner._findings.append(
                Finding(
                    scanner=self._scanner.name,
                    file=self._path,
                    line=_line_number(node),
                    category=category,
                    kind=kind,
                    snippet=text.strip(),
                    context={
                        "node_type": ctx.node_type,
                        "parent_type": ctx.parent_type,
                        "in_assignment": ctx.in_assignment,
                        "in_return": ctx.in_return,
                        "in_call": ctx.in_call,
                    },
                )
            )

        def _source_segment(self, node: ast.AST) -> Optional[str]:
            try:
                segment = ast.get_source_segment(self._source, node)
            except Exception:
                segment = None
            if segment:
                return segment
            lines = self._source.splitlines()
            lineno = getattr(node, "lineno", None)
            end_lineno = getattr(node, "end_lineno", None)
            if lineno is None or end_lineno is None or lineno < 1 or end_lineno > len(lines):
                return None
            if lineno == end_lineno:
                return lines[lineno - 1]
            return "\n".join(lines[lineno - 1 : end_lineno])

        def visit_BinOp(self, node: ast.BinOp) -> None:
            kind = self._binop_kind(node.op)
            if self._is_fraction_expr(node):
                self._record(node, "fraction_arithmetic", kind)
            elif self._is_symbolic_expr(node):
                self._record(node, "algebraic_expression", kind)
            self.generic_visit(node)

        def visit_Compare(self, node: ast.Compare) -> None:
            if self._is_fraction_expr(node.left) or any(
                self._is_fraction_expr(c) for c in node.comparators
            ):
                self._record(node, "fraction_comparison", "comparison")
            elif self._has_math_operands(node):
                self._record(node, "algebraic_comparison", "comparison")
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            func_name = self._callable_name(node.func)
            if func_name in {"Fraction", "fractions.Fraction"}:
                self._record(node, "fraction_construction", "exact_literal")
            elif func_name and self._is_math_library(func_name):
                self._record(node, "math_library_call", func_name)
            self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if any(d.id == "property" for d in node.decorator_list if isinstance(d, ast.Name)):
                # Properties returning expressions often encode formulas.
                pass
            self.generic_visit(node)

        def _binop_kind(self, op: ast.operator) -> str:
            mapping = {
                ast.Add: "addition",
                ast.Sub: "subtraction",
                ast.Mult: "multiplication",
                ast.Div: "division",
                ast.FloorDiv: "floor_division",
                ast.Mod: "modulo",
                ast.Pow: "exponentiation",
            }
            return mapping.get(type(op), "unknown")

        def _is_fraction_expr(self, node: ast.AST) -> bool:
            """True if the expression directly constructs or combines Fractions."""
            if isinstance(node, ast.Call):
                return self._callable_name(node.func) in {"Fraction", "fractions.Fraction"}
            if isinstance(node, ast.BinOp):
                return self._is_fraction_expr(node.left) or self._is_fraction_expr(node.right)
            if isinstance(node, ast.UnaryOp):
                return self._is_fraction_expr(node.operand)
            if isinstance(node, ast.Name):
                # Heuristic: variable names like `ratio`, `frac`, `proportion`
                # often carry Fractions; we require contextual evidence.
                return node.id.lower() in {"fraction", "frac", "ratio", "proportion"}
            return False

        def _is_symbolic_expr(self, node: ast.AST) -> bool:
            """True if the expression combines names/constants in a formula."""
            if isinstance(node, ast.BinOp):
                return self._has_symbolic_operand(node.left) or self._has_symbolic_operand(node.right)
            return False

        def _has_symbolic_operand(self, node: ast.AST) -> bool:
            return isinstance(node, (ast.Name, ast.Constant, ast.BinOp, ast.UnaryOp))

        def _has_math_operands(self, node: ast.Compare) -> bool:
            operands = [node.left] + list(node.comparators)
            return any(isinstance(o, (ast.BinOp, ast.Call, ast.UnaryOp)) for o in operands)

        def _callable_name(self, node: ast.AST) -> Optional[str]:
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Attribute):
                prefix = self._callable_name(node.value)
                return f"{prefix}.{node.attr}" if prefix else node.attr
            return None

        def _is_math_library(self, name: str) -> bool:
            math_prefixes = ("math.", "numpy.", "sympy.", "statistics.", "fractions.")
            return name.startswith(math_prefixes) or name in {
                "gcd",
                "lcm",
                "prod",
                "sum",
                "max",
                "min",
            }


def main() -> None:
    import json
    result = FormulaAstScanner().scan(Path("."))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
