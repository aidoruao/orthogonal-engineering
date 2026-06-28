"""Scanner that maps the entire invariant surface of the repository.

Parses every ``src/domains/*/invariants.py`` and
``src/domains/*/implementation.py`` to extract ``check_*`` functions, their
docstrings, falsifies_if conditions, and declared standards. It reports the
shape of the proof surface rather than searching for raw strings.

Standard: Yeshua
"""

from __future__ import annotations

import ast
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tools.scanners.base import Finding, Scanner, ScannerResult, _line_number, _read_text_safely


class InvariantSurfaceScanner(Scanner):
    """Map the invariant surface across all OE domains.

    Falsifies if: a check_* function lacks both ``Falsifies if:`` and
    ``falsifies_if:`` in its docstring, or its return annotation is not
    ``Tuple[bool, ProofObject]``.
    falsifies_if: a check_* function lacks both ``Falsifies if:`` and
    ``falsifies_if:`` in its docstring, or its return annotation is not
    ``Tuple[bool, ProofObject]``.
    """

    name = "invariant_surface"

    _RETURN_RE = re.compile(r"Tuple\s*\[\s*bool\s*,\s*ProofObject\s*\]")

    def __init__(self) -> None:
        self._findings: List[Finding] = []

    def scan(self, root: Path) -> ScannerResult:
        self._findings = []
        domains_root = root / "src" / "domains"
        if not domains_root.exists():
            domains_root = root

        files_scanned = 0
        for invariants_file in sorted(domains_root.rglob("invariants.py")):
            self._scan_invariants_file(invariants_file)
            files_scanned += 1
        for impl_file in sorted(domains_root.rglob("implementation.py")):
            self._scan_invariants_file(impl_file)
            files_scanned += 1

        metadata = self._compute_metadata(files_scanned)
        return ScannerResult(
            scanner=self.name,
            findings=tuple(self._findings),
            metadata=metadata,
        )

    def _scan_invariants_file(self, path: Path) -> None:
        source = _read_text_safely(path)
        if source is None:
            return
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return

        domain = path.parent.name
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("check_"):
                continue
            docstring = ast.get_docstring(node) or ""
            standard, falsifies = self._extract_docstring_meta(docstring)
            has_falsifies = bool(falsifies)
            has_falsifies_title = "Falsifies if:" in docstring
            return_type = ast.get_source_segment(source, node.returns) if node.returns else ""
            typed_correctly = bool(return_type and self._RETURN_RE.search(return_type))

            self._findings.append(
                Finding(
                    scanner=self.name,
                    file=path,
                    line=_line_number(node),
                    category="invariant_surface",
                    kind="check_function",
                    snippet=node.name,
                    context={
                        "domain": domain,
                        "function": node.name,
                        "standard": standard,
                        "falsifies_if": falsifies,
                        "has_falsifies_if": has_falsifies,
                        "has_falsifies_title": has_falsifies_title,
                        "typed_correctly": typed_correctly,
                        "return_type": return_type or None,
                        "docstring_length": len(docstring),
                    },
                )
            )

    def _extract_docstring_meta(self, docstring: str) -> Tuple[str, str]:
        standard_match = re.search(r"Standard:\s*([^\n]+)", docstring, re.IGNORECASE)
        standard = standard_match.group(1).strip() if standard_match else ""
        falsifies_match = re.search(r"falsifies_if:\s*([^\n]+)", docstring, re.IGNORECASE)
        falsifies = falsifies_match.group(1).strip() if falsifies_match else ""
        return standard, falsifies

    def _compute_metadata(self, files_scanned: int) -> Dict[str, Any]:
        total = len(self._findings)
        if total == 0:
            return {
                "files_scanned": files_scanned,
                "total_invariants": 0,
                "falsifies_coverage": Fraction(0),
                "typed_coverage": Fraction(0),
                "domains": [],
            }
        falsifies_ok = sum(1 for f in self._findings if f.context.get("has_falsifies_if"))
        typed_ok = sum(1 for f in self._findings if f.context.get("typed_correctly"))
        domains = sorted({f.context.get("domain") for f in self._findings})
        standards = sorted({f.context.get("standard") for f in self._findings if f.context.get("standard")})
        return {
            "files_scanned": files_scanned,
            "total_invariants": total,
            "falsifies_coverage": Fraction(falsifies_ok, total),
            "typed_coverage": Fraction(typed_ok, total),
            "domains": domains,
            "standards": standards,
        }


def main() -> None:
    import json
    result = InvariantSurfaceScanner().scan(Path("."))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
