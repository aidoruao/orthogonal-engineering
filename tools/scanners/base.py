"""Shared base classes and types for the OE structural scanner suite.

Standard: Yeshua
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Finding:
    """A single structural finding.

    Falsifies if: file, line, or category is missing or malformed.
    falsifies_if: file, line, or category is missing or malformed.
    """

    scanner: str
    file: Path
    line: Optional[int]
    category: str
    kind: str
    snippet: str
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scanner": self.scanner,
            "file": str(self.file),
            "line": self.line,
            "category": self.category,
            "kind": self.kind,
            "snippet": self.snippet,
            "context": _json_safe(self.context),
        }


@dataclass(frozen=True)
class ScannerResult:
    """Aggregated result from one scanner run.

    Falsifies if: scanner name is empty or findings list is None.
    falsifies_if: scanner name is empty or findings list is None.
    """

    scanner: str
    findings: Tuple[Finding, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scanner:
            raise ValueError("scanner name must not be empty")
        if self.findings is None:
            raise ValueError("findings must not be None")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scanner": self.scanner,
            "metadata": _json_safe(self.metadata),
            "findings": [f.to_dict() for f in self.findings],
        }

    def merkle_hash(self) -> str:
        """Return SHA-256 over the canonical JSON of this result."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Scanner(ABC):
    """Abstract base for all structural scanners.

    Falsifies if: scan() mutates filesystem state or returns non-deterministic
    findings for identical inputs.
    falsifies_if: scan() mutates filesystem state or returns non-deterministic
    findings for identical inputs.
    """

    name: str = "base"

    @abstractmethod
    def scan(self, root: Path) -> ScannerResult:
        """Scan ``root`` and return a deterministic ScannerResult."""
        raise NotImplementedError

    def verify_integrity(self, result: ScannerResult) -> Tuple[bool, ProofObject]:
        """Verify that ``result`` has a valid Merkle hash.

        Returns (ok, proof).
        """
        expected = result.merkle_hash()
        ok = len(expected) == 64 and all(c in "0123456789abcdef" for c in expected)
        proof = ProofObject(
            rule="ScannerIntegrity",
            premises=[f"scanner={result.scanner}", f"findings={len(result.findings)}"],
            conclusion=f"Merkle hash is valid SHA-256 hex: {ok}",
            falsifies_if="hash is not 64-char lowercase hex",
        )
        return ok, proof


def _line_number(node: Any) -> Optional[int]:
    """Safely extract line number from an AST node."""
    return getattr(node, "lineno", None)


def _read_text_safely(path: Path) -> Optional[str]:
    """Read text safely, returning None on decode errors."""
    try:
        return path.read_text(encoding="utf-8", errors="surrogateescape")
    except (OSError, UnicodeError):
        return None


def _count_fractions(findings: List[Finding]) -> Fraction:
    """Return the ratio of findings that mention Fraction explicitly."""
    total = len(findings)
    if total == 0:
        return Fraction(0)
    frac_count = sum(1 for f in findings if "Fraction" in f.snippet)
    return Fraction(frac_count, total)


def _json_safe(value: Any) -> Any:
    """Recursively convert Fraction and Path values to JSON-serialisable forms."""
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, set):
        return sorted(_json_safe(v) for v in value)
    return value


__all__ = [
    "Finding",
    "ScannerResult",
    "Scanner",
    "_line_number",
    "_read_text_safely",
    "_count_fractions",
]
