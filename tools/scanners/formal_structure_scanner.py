"""Structural scanner for formal mathematical constructs.

This scanner does not rely on raw keyword frequency. It requires a formal
symbol to appear as a defined identifier (class, function, or module-level
name) and to be corroborated by contextual evidence in docstrings, base
classes, type annotations, or adjacent formal vocabulary.

Standard: Yeshua
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from tools.scanners.base import Finding, Scanner, ScannerResult, _line_number, _read_text_safely


@dataclass(frozen=True)
class _FormalSignature:
    """A formal-structure signature: identifier + corroboration tokens."""

    field: str
    kind: str
    identifiers: FrozenSet[str]
    corroboration: FrozenSet[str]


_SIGNATURES: Tuple[_FormalSignature, ...] = (
    _FormalSignature(
        field="category_theory",
        kind="functor",
        identifiers=frozenset({"functor", "functors", "Functor"}),
        corroboration=frozenset({
            "map", "morphism", "object", "category", "covariant",
            "contravariant", "natural transformation",
        }),
    ),
    _FormalSignature(
        field="category_theory",
        kind="monad",
        identifiers=frozenset({"monad", "monads", "Monad"}),
        corroboration=frozenset({
            "unit", "join", "bind", "return", "kleisli", "functor",
        }),
    ),
    _FormalSignature(
        field="category_theory",
        kind="adjunction",
        identifiers=frozenset({"adjunction", "adjoint", "Adjunction", "Adjoint"}),
        corroboration=frozenset({
            "left adjoint", "right adjoint", "unit", "counit", "hom",
            "natural isomorphism", "universal",
        }),
    ),
    _FormalSignature(
        field="topology",
        kind="sheaf",
        identifiers=frozenset({"sheaf", "sheaves", "Sheaf"}),
        corroboration=frozenset({
            "stalk", "section", "restriction", "open set", "topology",
            "locale", "etale",
        }),
    ),
    _FormalSignature(
        field="topology",
        kind="topos",
        identifiers=frozenset({"topos", "topoi", "Topos"}),
        corroboration=frozenset({
            "sheaf", "subobject classifier", "site", "grothendieck",
            "exponential", "power object",
        }),
    ),
    _FormalSignature(
        field="logic",
        kind="forcing",
        identifiers=frozenset({"forcing", "Forcing"}),
        corroboration=frozenset({
            "condition", "poset", "generic", "dense", "filter", "name",
            "boolean valued",
        }),
    ),
    _FormalSignature(
        field="logic",
        kind="realizability",
        identifiers=frozenset({"realizability", "realizable", "Realizability"}),
        corroboration=frozenset({
            "realizer", "partial combinatory algebra", "pca", "troelstra",
            "kleene", "realizes",
        }),
    ),
    _FormalSignature(
        field="logic",
        kind="proof_object",
        identifiers=frozenset({"ProofObject", "proof_object"}),
        corroboration=frozenset({
            "rule", "premises", "conclusion", "falsifies_if", "merkle",
            "hash",
        }),
    ),
    _FormalSignature(
        field="algebra",
        kind="group_like",
        identifiers=frozenset({"group", "ring", "field", "module", "algebra"}),
        corroboration=frozenset({
            "operation", "identity", "inverse", "associative", "commutative",
            "distributive", "homomorphism",
        }),
    ),
    _FormalSignature(
        field="computation",
        kind="computability",
        identifiers=frozenset({"turing", "computable", "computability", "automaton"}),
        corroboration=frozenset({
            "machine", "state", "transition", "halting", "oracle", "tape",
        }),
    ),
)


class FormalStructureScanner(Scanner):
    """Detect formal mathematical structures with contextual corroboration.

    Falsifies if: a finding is emitted without both an identifier match and a
    corroboration token in the same lexical scope.
    falsifies_if: a finding is emitted without both an identifier match and a
    corroboration token in the same lexical scope.
    """

    name = "formal_structure"

    def __init__(self) -> None:
        self._findings: List[Finding] = []

    def scan(self, root: Path) -> ScannerResult:
        self._findings = []
        for path in sorted(root.rglob("*.py")):
            if ".venv" in path.parts or "node_modules" in path.parts:
                continue
            self._scan_file(path)

        metadata: Dict[str, Any] = {
            "files_scanned": len(set(f.file for f in self._findings)) or 0,
            "finding_count": len(self._findings),
            "fields": sorted({f.context.get("field") for f in self._findings}),
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

        self._StructureVisitor(self, path, source).visit(tree)

    class _StructureVisitor(ast.NodeVisitor):
        def __init__(self, scanner: "FormalStructureScanner", path: Path, source: str) -> None:
            self._scanner = scanner
            self._path = path
            self._source = source

        def _context_text(self, node: ast.AST) -> str:
            """Collect corroboration text from docstring, bases, annotations."""
            parts: List[str] = []
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    parts.append(doc)
                for base in getattr(node, "bases", []):
                    parts.append(ast.get_source_segment(self._source, base) or "")
                for decorator in node.decorator_list:
                    parts.append(ast.get_source_segment(self._source, decorator) or "")
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None:
                    parts.append(ast.get_source_segment(self._source, node.returns) or "")
            if isinstance(node, ast.Assign):
                if node.value is not None:
                    parts.append(ast.get_source_segment(self._source, node.value) or "")
            return "\n".join(parts).lower()

        def _identifier_names(self, node: ast.AST) -> FrozenSet[str]:
            names: Set[str] = set()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                names.add(elt.id)
            return frozenset(names)

        def _record(self, node: ast.AST, signature: _FormalSignature, matched: str) -> None:
            snippet = ast.get_source_segment(self._source, node)
            if not snippet:
                lines = self._source.splitlines()
                lineno = _line_number(node)
                if lineno and 1 <= lineno <= len(lines):
                    snippet = lines[lineno - 1]
            self._scanner._findings.append(
                Finding(
                    scanner=self._scanner.name,
                    file=self._path,
                    line=_line_number(node),
                    category=f"formal_{signature.field}",
                    kind=signature.kind,
                    snippet=snippet.strip() if snippet else matched,
                    context={
                        "field": signature.field,
                        "matched_identifier": matched,
                        "corroboration_hits": sorted(
                            t for t in signature.corroboration
                            if t.lower() in self._context_text(node)
                        ),
                    },
                )
            )

        def _check_node(self, node: ast.AST) -> None:
            names = self._identifier_names(node)
            context = self._context_text(node).lower()
            for sig in _SIGNATURES:
                matched = self._match_identifier(names, sig.identifiers)
                if not matched:
                    continue
                corroborated = any(token.lower() in context for token in sig.corroboration)
                if not corroborated:
                    continue
                self._record(node, sig, matched)

        def _match_identifier(self, names: FrozenSet[str], identifiers: FrozenSet[str]) -> Optional[str]:
            """Find the first identifier that is an exact or substring match."""
            for name in names:
                lower_name = name.lower()
                for ident in identifiers:
                    if ident.lower() == lower_name or ident.lower() in lower_name:
                        return ident
            return None

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self._check_node(node)
            self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._check_node(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._check_node(node)
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            # Only module-level assignments are likely to define named structures.
            self._check_node(node)
            self.generic_visit(node)


def main() -> None:
    import json
    result = FormalStructureScanner().scan(Path("."))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
