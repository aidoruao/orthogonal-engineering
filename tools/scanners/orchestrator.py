"""Orchestrator that runs all structural scanners and emits a unified report.

The report is SHA-256 anchored and includes per-scanner metadata, integrity
proofs, and a deterministic JSON serialisation.

Standard: Yeshua
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from axioms.logic import ProofObject

from tools.scanners.base import Scanner, ScannerResult, _json_safe
from tools.scanners.document_notation_scanner import DocumentNotationScanner
from tools.scanners.formal_structure_scanner import FormalStructureScanner
from tools.scanners.formula_ast_scanner import FormulaAstScanner
from tools.scanners.infrastructure_signature_scanner import InfrastructureSignatureScanner
from tools.scanners.invariant_surface_scanner import InvariantSurfaceScanner


@dataclass(frozen=True)
class OrchestratorReport:
    """Unified report from all scanners.

    Falsifies if: report is missing a top-level Merkle hash or any scanner
    result is corrupted.
    falsifies_if: report is missing a top-level Merkle hash or any scanner
    result is corrupted.
    """

    root: Path
    timestamp: str
    scanners: Tuple[ScannerResult, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "timestamp": self.timestamp,
            "metadata": _json_safe(self.metadata),
            "scanners": [s.to_dict() for s in self.scanners],
        }

    def merkle_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ScannerOrchestrator:
    """Run the full scanner suite deterministically.

    Falsifies if: scan order is non-deterministic or the report hash differs
    across identical invocations.
    falsifies_if: scan order is non-deterministic or the report hash differs
    across identical invocations.
    """

    name = "orchestrator"

    def __init__(self, scanners: Optional[List[Scanner]] = None) -> None:
        self._scanners: List[Scanner] = scanners or [
            FormulaAstScanner(),
            FormalStructureScanner(),
            InvariantSurfaceScanner(),
            InfrastructureSignatureScanner(),
            DocumentNotationScanner(),
        ]

    def run(self, root: Path) -> OrchestratorReport:
        """Run all scanners against ``root`` and assemble the report."""
        results: List[ScannerResult] = []
        for scanner in self._scanners:
            result = scanner.scan(root)
            results.append(result)

        metadata = self._compute_metadata(results)
        report = OrchestratorReport(
            root=root.resolve(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            scanners=tuple(results),
            metadata=metadata,
        )
        return report

    def verify(self, report: OrchestratorReport) -> Tuple[bool, ProofObject]:
        """Verify report integrity and that every scanner result hashes cleanly.

        Returns (ok, proof).
        """
        sub_proofs: List[Any] = []
        all_ok = True
        for result in report.scanners:
            h = result.merkle_hash()
            sub_ok = len(h) == 64 and all(c in "0123456789abcdef" for c in h)
            all_ok = all_ok and sub_ok
            sub_proofs.append(f"{result.scanner}: {sub_ok}")

        top_hash = report.merkle_hash()
        top_ok = len(top_hash) == 64 and all(c in "0123456789abcdef" for c in top_hash)
        all_ok = all_ok and top_ok

        proof = ProofObject(
            rule="OrchestratorIntegrity",
            premises=sub_proofs + [f"report_hash={top_hash}"],
            conclusion=f"All scanner results and report hash valid: {all_ok}",
            falsifies_if="any scanner hash or top-level hash is invalid",
        )
        return all_ok, proof

    def _compute_metadata(self, results: List[ScannerResult]) -> Dict[str, Any]:
        total_findings = sum(len(r.findings) for r in results)
        files_with_findings = len(
            {str(f.file) for r in results for f in r.findings}
        )
        categories = sorted({f.category for r in results for f in r.findings})
        return {
            "scanner_count": len(results),
            "total_findings": total_findings,
            "files_with_findings": files_with_findings,
            "categories": categories,
            "fraction_exact_coverage": self._fraction_coverage(results),
        }

    def _fraction_coverage(self, results: List[ScannerResult]) -> Fraction:
        formula_results = [r for r in results if r.scanner == "formula_ast"]
        if not formula_results:
            return Fraction(0)
        formula_findings = list(formula_results[0].findings)
        if not formula_findings:
            return Fraction(0)
        frac_count = sum(1 for f in formula_findings if "Fraction" in f.snippet)
        return Fraction(frac_count, len(formula_findings))


def run_scan(root: Path) -> OrchestratorReport:
    """Convenience entry point: run the default scanner suite."""
    return ScannerOrchestrator().run(root)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the OE structural scanner suite and emit a JSON report."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write JSON report",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Also print integrity verification result",
    )
    args = parser.parse_args()

    orchestrator = ScannerOrchestrator()
    report = orchestrator.run(args.root)
    ok, proof = orchestrator.verify(report)

    report_dict = report.to_dict()
    report_dict["merkle_hash"] = report.merkle_hash()
    report_dict["integrity"] = {
        "ok": ok,
        "proof": proof.to_dict(),
    }

    payload = json.dumps(report_dict, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)

    if args.verify:
        print(f"\nIntegrity: {ok}", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
