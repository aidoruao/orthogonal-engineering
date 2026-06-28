"""Scanner for mathematical notation embedded in documents.

Extracts LaTeX math fragments (inline ``$...$`` and display ``$$...$$``) and
Unicode mathematical symbols from Markdown, text, YAML, JSON, and TOML files.
It does not flag every Greek letter; it only records sequences that contain an
operator, relation, quantifier, or known formulaic token.

Standard: Yeshua
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple

from tools.scanners.base import Finding, Scanner, ScannerResult, _read_text_safely


class DocumentNotationScanner(Scanner):
    """Extract mathematical notation from documents.

    Falsifies if: a reported fragment contains no operator, relation,
    quantifier, or known formulaic token.
    falsifies_if: a reported fragment contains no operator, relation,
    quantifier, or known formulaic token.
    """

    name = "document_notation"

    _LATEX_INLINE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")
    _LATEX_DISPLAY = re.compile(r"\$\$(.+?)\$\$")
    _UNICODE_MATH = re.compile(
        r"[\u2200-\u22FF\u2100-\u214F\u2190-\u21FF\u2200-\u22FF"
        r"\u27C0-\u27EF\u2980-\u29FF\u2A00-\u2AFF]+",
        re.UNICODE,
    )

    _FORMULAIC_TOKENS: FrozenSet[str] = frozenset({
        "\\frac", "\\sum", "\\prod", "\\int", "\\forall", "\\exists",
        "\\implies", "\\Rightarrow", "\\to", "\\mapsto", "\\in", "\\notin",
        "\\subset", "\\cap", "\\cup", "\\setminus", "\\infty", "\\partial",
        "\\nabla", "\\cdot", "\\times", "\\oplus", "\\otimes", "\\equiv",
        "\\cong", "\\sim", "\\simeq", "\\approx", "\\neq", "\\leq", "\\geq",
        "\\lambda", "\\mu", "\\sigma", "\\delta", "\\alpha", "\\beta",
        "\\gamma", "\\Gamma", "\\omega", "\\Omega",
    })

    _OPERATOR_RELATION: FrozenSet[str] = frozenset({
        "=", "≠", "≈", "≡", "≤", "≥", "<", ">", "+", "-", "×", "÷", "·", "∂",
        "∑", "∏", "∫", "∀", "∃", "∈", "∉", "⊂", "∩", "∪", "→", "⇒", "↦",
        "∞", "∇", "√", "±", "∓", "⊗", "⊕", "∧", "∨", "¬",
    })

    _DOC_SUFFIXES: Tuple[str, ...] = (
        ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".oe",
    )

    def __init__(self) -> None:
        self._findings: List[Finding] = []

    def scan(self, root: Path) -> ScannerResult:
        self._findings = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if ".venv" in path.parts or "node_modules" in path.parts:
                continue
            if path.suffix.lower() not in self._DOC_SUFFIXES:
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
        text = _read_text_safely(path)
        if text is None:
            return
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in self._LATEX_DISPLAY.finditer(line):
                fragment = match.group(1).strip()
                if self._is_formulaic(fragment):
                    self._record(path, lineno, "latex_display", fragment)
            for match in self._LATEX_INLINE.finditer(line):
                fragment = match.group(1).strip()
                if self._is_formulaic(fragment):
                    self._record(path, lineno, "latex_inline", fragment)
            for match in self._UNICODE_MATH.finditer(line):
                fragment = match.group(0)
                if self._has_operator_or_relation(fragment):
                    self._record(path, lineno, "unicode_math", fragment)

    def _is_formulaic(self, fragment: str) -> bool:
        if any(token in fragment for token in self._FORMULAIC_TOKENS):
            return True
        return self._has_operator_or_relation(fragment)

    def _has_operator_or_relation(self, fragment: str) -> bool:
        return any(token in fragment for token in self._OPERATOR_RELATION)

    def _record(self, path: Path, line: int, kind: str, snippet: str) -> None:
        self._findings.append(
            Finding(
                scanner=self.name,
                file=path,
                line=line,
                category="document_math",
                kind=kind,
                snippet=snippet,
                context={"line_length": len(snippet)},
            )
        )


def main() -> None:
    import json
    result = DocumentNotationScanner().scan(Path("."))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
