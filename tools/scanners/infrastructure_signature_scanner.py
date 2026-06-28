"""Scanner for infrastructure signatures: Merkle trees, hashes, capability gates.

Detects usage patterns structurally: SHA-256 calls, Merkle helpers, consent
append operations, capability checks, and state-witness feeds. It avoids
keyword-only classification by requiring an import or a call to a known
infrastructure primitive.

Standard: Yeshua
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

from tools.scanners.base import Finding, Scanner, ScannerResult, _line_number, _read_text_safely


class InfrastructureSignatureScanner(Scanner):
    """Detect infrastructure signatures across the repository.

    Falsifies if: a finding is emitted for a call that is not to a known
    infrastructure primitive (hashlib, Merkle, consent, capability, witness).
    falsifies_if: a finding is emitted for a call that is not to a known
    infrastructure primitive (hashlib, Merkle, consent, capability, witness).
    """

    name = "infrastructure_signature"

    _HASH_FUNCS: FrozenSet[str] = frozenset({
        "hashlib.sha256", "sha256", "hashlib.sha3_256", "hashlib.md5",
        "hashlib.blake2b", "hashlib.blake2s",
    })
    _MERKLE_FUNCS: FrozenSet[str] = frozenset({
        "merkle_root", "merkle_root_over_proofs", "inclusion_proof",
        "verify_inclusion", "build_merkle_tree",
    })
    _CONSENT_FUNCS: FrozenSet[str] = frozenset({
        "append_consent", "record_consent", "log_consent", "register_consent",
    })
    _CAPABILITY_FUNCS: FrozenSet[str] = frozenset({
        "require_capability", "check_capability", "has_capability",
        "capability_gate", "assert_capability",
    })
    _WITNESS_FUNCS: FrozenSet[str] = frozenset({
        "generate_feed_entry", "state_witness", "witness_state",
        "append_witness", "verify_chain",
    })

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

        self._InfrastructureVisitor(self, path, source).visit(tree)

    class _InfrastructureVisitor(ast.NodeVisitor):
        def __init__(self, scanner: "InfrastructureSignatureScanner", path: Path, source: str) -> None:
            self._scanner = scanner
            self._path = path
            self._source = source

        def _record(self, node: ast.AST, category: str, kind: str) -> None:
            snippet = ast.get_source_segment(self._source, node)
            if not snippet:
                lines = self._source.splitlines()
                lineno = _line_number(node)
                if lineno and 1 <= lineno <= len(lines):
                    snippet = lines[lineno - 1]
            if snippet:
                self._scanner._findings.append(
                    Finding(
                        scanner=self._scanner.name,
                        file=self._path,
                        line=_line_number(node),
                        category=category,
                        kind=kind,
                        snippet=snippet.strip(),
                        context={},
                    )
                )

        def _callable_name(self, node: ast.AST) -> Optional[str]:
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Attribute):
                prefix = self._callable_name(node.value)
                return f"{prefix}.{node.attr}" if prefix else node.attr
            return None

        def visit_Call(self, node: ast.Call) -> None:
            name = self._callable_name(node.func)
            if name in self._scanner._HASH_FUNCS:
                self._record(node, "cryptographic_integrity", "hash_call")
            elif name and name.split(".")[-1] in self._scanner._MERKLE_FUNCS:
                self._record(node, "merkle_infrastructure", "merkle_call")
            elif name and name.split(".")[-1] in self._scanner._CONSENT_FUNCS:
                self._record(node, "consent_infrastructure", "consent_call")
            elif name and name.split(".")[-1] in self._scanner._CAPABILITY_FUNCS:
                self._record(node, "capability_gate", "capability_call")
            elif name and name.split(".")[-1] in self._scanner._WITNESS_FUNCS:
                self._record(node, "state_witness", "witness_call")
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                if alias.name == "hashlib":
                    self._record(node, "cryptographic_integrity", "hashlib_import")
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.module == "hashlib":
                self._record(node, "cryptographic_integrity", "hashlib_import")
            self.generic_visit(node)


def main() -> None:
    import json
    result = InfrastructureSignatureScanner().scan(Path("."))
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
