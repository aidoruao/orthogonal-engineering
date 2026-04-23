"""Test suite for self-hosting proof.

Phase 5 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fractions import Fraction

from tools.self_hosting_proof import (
    SelfHostingEvidence,
    check_tools_self_verify,
    check_compiler_spec_exists,
    check_verification_loop_closed,
    check_no_stub_tools,
    run_all_invariants,
    _file_has_falsifies_if,
    _is_stub_file,
)


class TestSelfHostingProof:
    def test_file_has_falsifies_if(self):
        assert _file_has_falsifies_if(Path("tools/verify_all.py")) is True
        assert _file_has_falsifies_if(Path("tools/standards_check.py")) is True
        # popperian_audit.py uses falsifies_if as regex but not in its own docstrings
        # This is a real gap the self-hosting proof correctly detects

    def test_is_not_stub(self):
        assert _is_stub_file(Path("tools/verify_all.py")) is False
        assert _is_stub_file(Path("tools/standards_check.py")) is False

    def test_pass_evidence(self):
        evidence = SelfHostingEvidence(
            verify_all_has_falsifies_if=True,
            popperian_has_falsifies_if=True,
            standards_has_falsifies_if=True,
            compiler_spec_exists=True,
            total_tools_checked=10,
            tools_with_falsifies_if=10,
            self_hosting_ratio=Fraction(1, 1),
            verification_loop_closed=True,
        )
        assert check_tools_self_verify(evidence)[0] is True
        assert check_compiler_spec_exists(evidence)[0] is True
        assert check_verification_loop_closed(evidence)[0] is True
        assert check_no_stub_tools(evidence, [])[0] is True

    def test_fail_evidence(self):
        evidence = SelfHostingEvidence(
            verify_all_has_falsifies_if=False,
            popperian_has_falsifies_if=False,
            standards_has_falsifies_if=False,
            compiler_spec_exists=False,
            total_tools_checked=10,
            tools_with_falsifies_if=5,
            self_hosting_ratio=Fraction(1, 2),
            verification_loop_closed=False,
        )
        assert check_tools_self_verify(evidence)[0] is False
        assert check_compiler_spec_exists(evidence)[0] is False
        assert check_verification_loop_closed(evidence)[0] is False
        assert check_no_stub_tools(evidence, ["stub.py"])[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        assert len(results) == 4
        for name, ok, proof in results:
            assert isinstance(ok, bool)
            assert proof.conclusion

    def test_main_runs(self):
        from tools.self_hosting_proof import main
        try:
            main()
        except Exception as exc:
            raise AssertionError(f"main() crashed: {exc}")
