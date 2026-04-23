"""tools/self_hosting_proof.py — Self-hosting proof (strange loop).

Phase 5 of Depositive Campaign.

Demonstrates that OE's verification tools verify themselves,
producing a ProofObject that proves the verification infrastructure
is self-consistent.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class SelfHostingEvidence:
    """Evidence that the verification infrastructure is self-hosting."""
    verify_all_has_falsifies_if: bool
    popperian_has_falsifies_if: bool
    standards_has_falsifies_if: bool
    compiler_spec_exists: bool
    total_tools_checked: int
    tools_with_falsifies_if: int
    self_hosting_ratio: Fraction
    verification_loop_closed: bool


# ---------------------------------------------------------------------------
# Tool inspection helpers
# ---------------------------------------------------------------------------

def _file_has_falsifies_if(path: Path) -> bool:
    """Check if a Python file contains 'falsifies_if' in any docstring."""
    if not path.exists():
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring and "falsifies_if" in docstring:
                return True
    return False


def _is_stub_file(path: Path) -> bool:
    """Detect if a file is essentially a stub (only pass/NotImplemented/ellipsis)."""
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    # If file has no def/class with a real body, it's a stub
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body = node.body
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                continue
            if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and body[0].value.value is ...:
                continue
            # Has real implementation
            return False
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    item_body = item.body
                    if len(item_body) == 1 and isinstance(item_body[0], ast.Pass):
                        continue
                    if len(item_body) == 1 and isinstance(item_body[0], ast.Expr) and isinstance(item_body[0].value, ast.Constant) and item_body[0].value.value is ...:
                        continue
                    return False
    return True


def inspect_tools(tools_dir: Path = Path("tools")) -> Tuple[int, int, List[str]]:
    """Inspect all Python files in tools/ for falsifies_if and stub status."""
    total = 0
    with_falsifies = 0
    stubs: List[str] = []
    for py_file in sorted(tools_dir.glob("*.py")):
        if py_file.name.startswith("test_"):
            continue
        total += 1
        if _file_has_falsifies_if(py_file):
            with_falsifies += 1
        if _is_stub_file(py_file):
            stubs.append(py_file.name)
    return total, with_falsifies, stubs


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_tools_self_verify(evidence: SelfHostingEvidence) -> Tuple[bool, ProofObject]:
    """All tools must have falsifies_if (Gemini Target 2 / Lawvere fixed-point).

    Falsifies if: self_hosting_ratio < Fraction(1, 1).
    falsifies_if: self_hosting_ratio < Fraction(1, 1).
    """
    if evidence.self_hosting_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Self-hosting ratio {evidence.self_hosting_ratio} < 1 — "
                f"{evidence.tools_with_falsifies_if}/{evidence.total_tools_checked} tools have falsifies_if"
            ),
            premises=[
                f"Total: {evidence.total_tools_checked}",
                f"With falsifies_if: {evidence.tools_with_falsifies_if}",
            ],
            rule="self_hosting_tools_verify",
        )
    return True, ProofObject(
        conclusion=(
            f"All {evidence.total_tools_checked} tools self-verify: "
            f"ratio={evidence.self_hosting_ratio}"
        ),
        premises=[
            f"Total: {evidence.total_tools_checked}",
            f"With falsifies_if: {evidence.tools_with_falsifies_if}",
        ],
        rule="self_hosting_tools_verify",
    )


def check_compiler_spec_exists(evidence: SelfHostingEvidence) -> Tuple[bool, ProofObject]:
    """Seven Pillars compiler spec must exist (1a.py).

    Falsifies if: compiler_spec_exists == False.
    falsifies_if: compiler_spec_exists == False.
    """
    if not evidence.compiler_spec_exists:
        return False, ProofObject(
            conclusion="VIOLATION: Compiler spec (1a.py) missing",
            premises=["compiler_spec_exists: False"],
            rule="self_hosting_compiler_spec",
        )
    return True, ProofObject(
        conclusion="Compiler spec exists",
        premises=["compiler_spec_exists: True"],
        rule="self_hosting_compiler_spec",
    )


def check_verification_loop_closed(evidence: SelfHostingEvidence) -> Tuple[bool, ProofObject]:
    """G5 Logos grounding model: verification loop must be closed.

    Falsifies if: verification_loop_closed == False.
    falsifies_if: verification_loop_closed == False.
    """
    if not evidence.verification_loop_closed:
        return False, ProofObject(
            conclusion="VIOLATION: Verification loop open — not all tools self-verify",
            premises=[f"Closed: {evidence.verification_loop_closed}"],
            rule="self_hosting_loop_closed",
        )
    return True, ProofObject(
        conclusion="Verification loop closed",
        premises=[f"Closed: {evidence.verification_loop_closed}"],
        rule="self_hosting_loop_closed",
    )


def check_no_stub_tools(evidence: SelfHostingEvidence, stubs: List[str]) -> Tuple[bool, ProofObject]:
    """CS-004: no stub tools allowed.

    Falsifies if: any tool file is a stub (pass-only body).
    falsifies_if: len(stubs) > 0.
    """
    if stubs:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(stubs)} stub tool(s): {', '.join(stubs)}",
            premises=[f"Stubs: {stubs}"],
            rule="self_hosting_no_stubs",
        )
    return True, ProofObject(
        conclusion="Zero stub tools",
        premises=["Stubs: []"],
        rule="self_hosting_no_stubs",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all self-hosting checks and return results with ProofObjects."""
    total, with_falsifies, stubs = inspect_tools()
    compiler_spec = Path("minimal_ai_ide/1a.py").exists()
    ratio = Fraction(with_falsifies, total) if total > 0 else Fraction(0, 1)
    loop_closed = (
        _file_has_falsifies_if(Path("tools/verify_all.py"))
        and _file_has_falsifies_if(Path("tools/standards_check.py"))
        and _file_has_falsifies_if(Path("audit/popperian_audit.py"))
        and compiler_spec
        and len(stubs) == 0
    )

    evidence = SelfHostingEvidence(
        verify_all_has_falsifies_if=_file_has_falsifies_if(Path("tools/verify_all.py")),
        popperian_has_falsifies_if=_file_has_falsifies_if(Path("audit/popperian_audit.py")),
        standards_has_falsifies_if=_file_has_falsifies_if(Path("tools/standards_check.py")),
        compiler_spec_exists=compiler_spec,
        total_tools_checked=total,
        tools_with_falsifies_if=with_falsifies,
        self_hosting_ratio=ratio,
        verification_loop_closed=loop_closed,
    )

    checks = [
        ("check_tools_self_verify", check_tools_self_verify(evidence)),
        ("check_compiler_spec_exists", check_compiler_spec_exists(evidence)),
        ("check_verification_loop_closed", check_verification_loop_closed(evidence)),
        ("check_no_stub_tools", check_no_stub_tools(evidence, stubs)),
    ]

    return [(name, ok, proof) for name, (ok, proof) in checks]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Print self-hosting proof report."""
    total, with_falsifies, stubs = inspect_tools()
    compiler_spec = Path("minimal_ai_ide/1a.py").exists()
    ratio = Fraction(with_falsifies, total) if total > 0 else Fraction(0, 1)
    loop_closed = (
        _file_has_falsifies_if(Path("tools/verify_all.py"))
        and _file_has_falsifies_if(Path("tools/standards_check.py"))
        and _file_has_falsifies_if(Path("audit/popperian_audit.py"))
        and compiler_spec
        and len(stubs) == 0
    )

    print("=" * 55)
    print("SELF-HOSTING PROOF")
    print("=" * 55)
    print(f"Tools checked: {total}")
    print(f"Tools with falsifies_if: {with_falsifies}")
    print(f"Self-hosting ratio: {ratio}")
    print(f"Compiler spec: {'EXISTS' if compiler_spec else 'MISSING'}")
    print(f"Verification loop: {'CLOSED' if loop_closed else 'OPEN'}")
    if stubs:
        print(f"Stub tools: {', '.join(stubs)}")
    print("=" * 55)

    results = run_all_invariants()
    all_pass = all(ok for _, ok, _ in results)
    verdict = "SELF-HOSTING" if all_pass else "NOT SELF-HOSTING"
    print(f"VERDICT: {verdict}")
    print("=" * 55)

    for name, ok, proof in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}: {proof.conclusion}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
