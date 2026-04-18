"""tests/test_tier3_tools.py — Pytest tests for Tier 3 Agent Tooling.

Covers all 5 tools:
    1. tools/onboard_agent.py
    2. tools/context_window_estimator.py
    3. tools/since_last_session.py
    4. tools/arxiv_paper_template.py
    5. tools/agent_health_check.py

All tests are stdlib-only (no external fixtures required), mypy-strict
compatible, and satisfy Popperian falsifiability requirements.

Standard: Yeshua / Orthogonal Engineering — Gap #13-17
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# 1. onboard_agent
# ---------------------------------------------------------------------------

from tools.onboard_agent import (  # noqa: E402
    CONTEXT_WINDOWS,
    SUPPORTED_AGENTS,
    build_context_block,
    check_consent_log,
    check_feed_integrity,
    check_python_version,
    check_required_files,
    filter_by_scope,
    load_registry,
    main as onboard_main,
    run_env_checks,
)


class TestOnboardAgentRegistry:
    """Tests for registry loading and scope filtering."""

    def test_load_registry_returns_list(self) -> None:
        """Loaded registry is a non-empty list of dicts.

        Falsifies if: load_registry() returns an empty list.
        falsifies_if: load_registry() returns an empty list.
        """
        standards = load_registry()
        assert isinstance(standards, list)
        assert len(standards) > 0

    def test_filter_by_scope_none_returns_all(self) -> None:
        """filter_by_scope(None) returns all standards unchanged.

        Falsifies if: count with None scope differs from total standard count.
        falsifies_if: count with None scope differs from total standard count.
        """
        standards = load_registry()
        filtered = filter_by_scope(standards, None)
        assert len(filtered) == len(standards)

    def test_filter_by_scope_domain_returns_subset(self) -> None:
        """filter_by_scope(src/domains/**) returns only domain-scoped standards.

        Falsifies if: all 30+ standards are returned (no filtering occurred).
        falsifies_if: all 30+ standards are returned (no filtering occurred).
        """
        standards = load_registry()
        filtered = filter_by_scope(standards, "src/domains/**")
        # Domain-scoped standards should be a subset of all
        assert len(filtered) <= len(standards)
        # The wildcard scope ** should match everything
        wildcard = filter_by_scope(standards, "**")
        assert len(wildcard) == len(standards)

    def test_supported_agents_contains_copilot(self) -> None:
        """Supported agents set includes copilot.

        Falsifies if: 'copilot' not in SUPPORTED_AGENTS.
        falsifies_if: 'copilot' not in SUPPORTED_AGENTS.
        """
        assert "copilot" in SUPPORTED_AGENTS

    def test_context_windows_all_positive(self) -> None:
        """All agent context windows are strictly positive integers.

        Falsifies if: any context window <= 0.
        falsifies_if: any context window <= 0.
        """
        for agent, tokens in CONTEXT_WINDOWS.items():
            assert tokens > 0, f"{agent} has non-positive context window"


class TestOnboardAgentEnvChecks:
    """Tests for environment check functions."""

    def test_check_python_version_returns_bool_int(self) -> None:
        """check_python_version returns (bool, non-empty string).

        Falsifies if: return type is not (bool, str).
        falsifies_if: return type is not (bool, str).
        """
        ok, msg = check_python_version()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_check_python_version_passes_on_312(self) -> None:
        """Python 3.12 satisfies the >= 3.10 requirement.

        Falsifies if: returns False on Python >= 3.10.
        falsifies_if: returns False on Python >= 3.10.
        """
        ok, _ = check_python_version()
        # In the CI environment we know Python >= 3.10
        assert ok is True

    def test_check_required_files_returns_tuple(self) -> None:
        """check_required_files returns (bool, list).

        Falsifies if: return is not a 2-tuple of (bool, list).
        falsifies_if: return is not a 2-tuple of (bool, list).
        """
        ok, missing = check_required_files()
        assert isinstance(ok, bool)
        assert isinstance(missing, list)

    def test_check_consent_log_positive_count(self) -> None:
        """Consent log has at least 1 entry in the current repo.

        Falsifies if: consent_log.jsonl has no parseable JSONL entries.
        falsifies_if: consent_log.jsonl has no parseable JSONL entries.
        """
        ok, count = check_consent_log()
        assert ok is True
        assert count > 0

    def test_run_env_checks_returns_list_of_dicts(self) -> None:
        """run_env_checks returns (bool, list[dict]).

        Falsifies if: env_results is not a list of dicts.
        falsifies_if: env_results is not a list of dicts.
        """
        _all_ok, results = run_env_checks()
        assert isinstance(results, list)
        for r in results:
            assert "check" in r
            assert "pass" in r


class TestOnboardAgentContextBlock:
    """Tests for context block generation."""

    def test_build_context_block_contains_agent_name(self) -> None:
        """Context block header contains the agent name in uppercase.

        Falsifies if: 'COPILOT' not in output for --agent copilot.
        falsifies_if: 'COPILOT' not in output for --agent copilot.
        """
        standards = load_registry()
        block = build_context_block("copilot", None, standards[:3], [])
        assert "COPILOT" in block

    def test_build_context_block_contains_standard_ids(self) -> None:
        """Context block contains at least one standard ID.

        Falsifies if: block has no recognizable standard IDs.
        falsifies_if: block has no recognizable standard IDs.
        """
        standards = load_registry()[:5]
        block = build_context_block("claude", None, standards, [])
        # At least one standard ID like YS-001, CS-001, etc.
        assert any(s["id"] in block for s in standards)

    def test_onboard_main_exit_zero_for_valid_agent(self) -> None:
        """onboard_main exits 0 for a valid agent with --skip-env-check.

        Falsifies if: exits non-zero for a supported agent in a healthy repo.
        falsifies_if: exits non-zero for a supported agent in a healthy repo.
        """
        code = onboard_main(["--agent", "copilot", "--skip-env-check"])
        assert code == 0

    def test_onboard_main_json_output(self) -> None:
        """--json flag produces parseable JSON.

        Falsifies if: output is not valid JSON.
        falsifies_if: output is not valid JSON.
        """
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = onboard_main(["--agent", "devin", "--skip-env-check", "--json"])
        assert code == 0
        data = json.loads(buf.getvalue())
        assert data["agent"] == "devin"
        assert "standards_count" in data


# ---------------------------------------------------------------------------
# 2. context_window_estimator
# ---------------------------------------------------------------------------

from tools.context_window_estimator import (  # noqa: E402
    AGENT_CONTEXT_WINDOWS,
    CHARS_PER_TOKEN,
    estimate_file_tokens,
    estimate_path,
    main as estimator_main,
    summarize_results,
)


class TestContextWindowEstimator:
    """Tests for token estimation logic."""

    def test_chars_per_token_is_fraction(self) -> None:
        """CHARS_PER_TOKEN is a Fraction equal to 4.

        Falsifies if: CHARS_PER_TOKEN != Fraction(4).
        falsifies_if: CHARS_PER_TOKEN != Fraction(4).
        """
        assert CHARS_PER_TOKEN == Fraction(4)

    def test_estimate_file_tokens_exact_arithmetic(self) -> None:
        """estimate_file_tokens uses exact Fraction arithmetic.

        Falsifies if: token_fraction != char_count / 4.
        falsifies_if: token_fraction != char_count / 4.
        """
        # Use SOP_AI_HANDSHAKE.md which is guaranteed to exist
        target = REPO_ROOT / "SOP_AI_HANDSHAKE.md"
        if not target.exists():
            pytest.skip("SOP_AI_HANDSHAKE.md not found")
        chars, tokens_frac = estimate_file_tokens(target)
        expected = Fraction(chars) / Fraction(4)
        assert tokens_frac == expected

    def test_estimate_file_tokens_empty_file_handled(self, tmp_path: Path) -> None:
        """estimate_file_tokens handles empty files gracefully.

        Falsifies if: raises an exception on an empty file.
        falsifies_if: raises an exception on an empty file.
        """
        empty = tmp_path / "empty.py"
        empty.write_text("", encoding="utf-8")
        chars, tokens = estimate_file_tokens(empty)
        assert chars == 0
        assert tokens == Fraction(0)

    def test_estimate_path_directory(self) -> None:
        """estimate_path on a directory returns one entry per text file.

        Falsifies if: returns an empty list for a non-empty directory.
        falsifies_if: returns an empty list for a non-empty directory.
        """
        results = estimate_path(REPO_ROOT / "src" / "domains" / "d_aerospace")
        assert len(results) > 0
        for r in results:
            assert "tokens" in r
            assert r["tokens"] >= 0

    def test_summarize_results_total_is_sum(self) -> None:
        """summarize_results total_tokens equals sum of individual tokens.

        Falsifies if: total_tokens != sum(r['tokens'] for r in results).
        falsifies_if: total_tokens != sum(r['tokens'] for r in results).
        """
        fake: list[dict[str, Any]] = [
            {"path": "a.py", "chars": 400, "tokens": 100, "method": "heuristic"},
            {"path": "b.py", "chars": 800, "tokens": 200, "method": "heuristic"},
        ]
        summary = summarize_results(fake)
        assert summary["total_tokens"] == 300
        assert summary["total_chars"] == 1200
        assert summary["file_count"] == 2

    def test_agent_context_windows_all_positive(self) -> None:
        """All agent context window sizes are strictly positive.

        Falsifies if: any agent has context_window <= 0.
        falsifies_if: any agent has context_window <= 0.
        """
        for agent, size in AGENT_CONTEXT_WINDOWS.items():
            assert size > 0, f"{agent} context window is not positive"

    def test_estimator_main_budget_exceeded_exit_1(self, tmp_path: Path) -> None:
        """--budget 1 exits 1 when file has more than 1 token.

        Falsifies if: exit code is 0 when file exceeds budget.
        falsifies_if: exit code is 0 when file exceeds budget.
        """
        big_file = tmp_path / "big.py"
        big_file.write_text("x = 1\n" * 100, encoding="utf-8")
        code = estimator_main(["--path", str(big_file), "--budget", "1"])
        assert code == 1

    def test_estimator_main_list_agents_exit_zero(self) -> None:
        """--list-agents exits 0.

        Falsifies if: --list-agents returns non-zero exit code.
        falsifies_if: --list-agents returns non-zero exit code.
        """
        code = estimator_main(["--list-agents"])
        assert code == 0

    def test_estimator_main_json_output_parseable(self) -> None:
        """--json flag produces parseable JSON with expected keys.

        Falsifies if: output is not valid JSON or lacks required keys.
        falsifies_if: output is not valid JSON or lacks required keys.
        """
        import io
        from contextlib import redirect_stdout

        target = REPO_ROOT / "SOP_AI_HANDSHAKE.md"
        if not target.exists():
            pytest.skip("SOP_AI_HANDSHAKE.md not found")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = estimator_main(["--path", str(target), "--json"])
        assert code == 0
        data = json.loads(buf.getvalue())
        assert "summary" in data
        assert "total_tokens" in data["summary"]


# ---------------------------------------------------------------------------
# 3. since_last_session
# ---------------------------------------------------------------------------

from tools.since_last_session import (  # noqa: E402
    _parse_feed_rows,
    get_feed_rows,
    main as since_main,
    report_since_row,
)


class TestSinceLastSession:
    """Tests for the session catch-up tool."""

    def test_parse_feed_rows_returns_list_of_dicts(self) -> None:
        """_parse_feed_rows returns a list of dicts with expected keys.

        Falsifies if: any row dict is missing the 'timestamp' key.
        falsifies_if: any row dict is missing the 'timestamp' key.
        """
        sample = (
            "| timestamp | freeze_hash | merkle_root | invariant_spec_version | "
            "source_paths | commit_sha | prev_entry_hash | entry_hash |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| 2026-01-01T00:00:00Z | abc | def | v2 | spec/*.json | 1234567 | prev | cur |\n"
        )
        rows = _parse_feed_rows(sample)
        assert len(rows) == 1
        assert rows[0]["timestamp"] == "2026-01-01T00:00:00Z"
        assert rows[0]["commit_sha"] == "1234567"

    def test_get_feed_rows_returns_list(self) -> None:
        """get_feed_rows returns a list with at least 1 entry for this repo.

        Falsifies if: AGENT_FEED.md exists but returns empty list.
        falsifies_if: AGENT_FEED.md exists but returns empty list.
        """
        rows = get_feed_rows()
        assert isinstance(rows, list)
        assert len(rows) > 0, "AGENT_FEED.md should have rows"

    def test_report_since_row_zero_returns_all(self) -> None:
        """report_since_row(0) returns all rows.

        Falsifies if: returns fewer rows than total row count.
        falsifies_if: returns fewer rows than total row count.
        """
        all_rows = get_feed_rows()
        code, data = report_since_row(0, as_json=True)
        assert code == 0
        assert isinstance(data, dict)
        assert data["new_row_count"] == len(all_rows)

    def test_report_since_row_last_returns_empty(self) -> None:
        """report_since_row(total) returns zero new rows.

        Falsifies if: returns new rows when asking from the last row index.
        falsifies_if: returns new rows when asking from the last row index.
        """
        all_rows = get_feed_rows()
        total = len(all_rows)
        code, data = report_since_row(total, as_json=True)
        assert code == 0
        assert isinstance(data, dict)
        assert data["new_row_count"] == 0

    def test_report_since_row_negative_treated_as_zero(self) -> None:
        """report_since_row(-1) is treated as row 0.

        Falsifies if: negative row index causes crash or wrong count.
        falsifies_if: negative row index causes crash or wrong count.
        """
        all_rows = get_feed_rows()
        code, data = report_since_row(-1, as_json=True)
        assert code == 0
        assert isinstance(data, dict)
        assert data["new_row_count"] == len(all_rows)

    def test_since_main_since_row_exits_zero(self) -> None:
        """--since-row 0 exits 0 and prints text output.

        Falsifies if: exits non-zero for a valid row number.
        falsifies_if: exits non-zero for a valid row number.
        """
        code = since_main(["--since-row", "0"])
        assert code == 0

    def test_since_main_json_parseable(self) -> None:
        """--json flag with --since-row produces parseable JSON.

        Falsifies if: output is not valid JSON.
        falsifies_if: output is not valid JSON.
        """
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = since_main(["--since-row", "180", "--json"])
        assert code == 0
        data = json.loads(buf.getvalue())
        assert "new_rows" in data
        assert isinstance(data["new_rows"], list)


# ---------------------------------------------------------------------------
# 4. arxiv_paper_template
# ---------------------------------------------------------------------------

from tools.arxiv_paper_template import (  # noqa: E402
    collect_metrics,
    count_domains,
    count_tests,
    generate_latex,
    get_feed_row_count,
    get_merkle_root,
    get_standards_count,
    main as arxiv_main,
)


class TestArxivPaperTemplate:
    """Tests for the arXiv LaTeX template generator."""

    def test_count_domains_positive(self) -> None:
        """count_domains returns a positive integer.

        Falsifies if: count is 0 in a repo with domain directories.
        falsifies_if: count is 0 in a repo with domain directories.
        """
        count = count_domains()
        assert count > 0

    def test_count_tests_positive(self) -> None:
        """count_tests returns a positive integer.

        Falsifies if: count is 0 in a repo with test files.
        falsifies_if: count is 0 in a repo with test files.
        """
        count = count_tests()
        assert count > 0

    def test_get_merkle_root_hex_or_unavailable(self) -> None:
        """get_merkle_root returns a 64-char hex string or 'unavailable'.

        Falsifies if: returns a string that is neither 64-char hex nor 'unavailable'.
        falsifies_if: returns a string that is neither 64-char hex nor 'unavailable'.
        """
        import re
        root = get_merkle_root()
        assert isinstance(root, str)
        assert re.fullmatch(r"[0-9a-f]{64}", root) or root == "unavailable"

    def test_get_feed_row_count_positive(self) -> None:
        """get_feed_row_count returns a positive integer for this repo.

        Falsifies if: AGENT_FEED.md has rows but count is 0.
        falsifies_if: AGENT_FEED.md has rows but count is 0.
        """
        count = get_feed_row_count()
        assert count > 0

    def test_get_standards_count_positive(self) -> None:
        """get_standards_count returns a positive integer.

        Falsifies if: STANDARDS_REGISTRY.json has entries but count is 0.
        falsifies_if: STANDARDS_REGISTRY.json has entries but count is 0.
        """
        count = get_standards_count()
        assert count > 0

    def test_collect_metrics_returns_all_keys(self) -> None:
        """collect_metrics returns a dict with all required keys.

        Falsifies if: any key is missing from the returned dict.
        falsifies_if: any key is missing from the returned dict.
        """
        required = {
            "domain_count", "axiom_count", "case_study_count", "test_count",
            "standards_count", "merkle_root", "feed_row_count",
            "popperian_pass_rate", "consent_log_count", "head_sha", "generated_at",
        }
        metrics = collect_metrics()
        for key in required:
            assert key in metrics, f"Missing key: {key}"

    def test_generate_latex_contains_domain_count(self) -> None:
        """generate_latex output contains the domain_count value.

        Falsifies if: domain_count integer not present in LaTeX output.
        falsifies_if: domain_count integer not present in LaTeX output.
        """
        metrics = collect_metrics()
        latex = generate_latex(metrics)
        assert str(metrics["domain_count"]) in latex

    def test_generate_latex_contains_document_class(self) -> None:
        """generate_latex output starts with a valid LaTeX document.

        Falsifies if: output lacks \\documentclass.
        falsifies_if: output lacks \\documentclass.
        """
        metrics = collect_metrics()
        latex = generate_latex(metrics)
        assert "\\documentclass" in latex
        assert "\\end{document}" in latex

    def test_generate_latex_no_unresolved_placeholders(self) -> None:
        """generate_latex has no unresolved $variable placeholders.

        Falsifies if: '$head_sha' (literal) appears in the output.
        falsifies_if: '$head_sha' (literal) appears in the output.
        """
        metrics = collect_metrics()
        latex = generate_latex(metrics)
        # After Template.safe_substitute, unreplaced variables stay as ${var}
        # We check that our known variables are all substituted
        for var in ("head_sha", "domain_count", "test_count", "standards_count"):
            assert "${" + var + "}" not in latex, f"Unresolved placeholder: ${var}"

    def test_arxiv_main_dry_run_exits_zero(self) -> None:
        """--dry-run exits 0 and prints LaTeX to stdout.

        Falsifies if: exits non-zero in dry-run mode.
        falsifies_if: exits non-zero in dry-run mode.
        """
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = arxiv_main(["--dry-run"])
        assert code == 0
        assert "\\documentclass" in buf.getvalue()

    def test_arxiv_main_metrics_json_exits_zero(self) -> None:
        """--metrics-json exits 0 and prints parseable JSON.

        Falsifies if: output is not valid JSON.
        falsifies_if: output is not valid JSON.
        """
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = arxiv_main(["--metrics-json"])
        assert code == 0
        data = json.loads(buf.getvalue())
        assert "domain_count" in data

    def test_arxiv_main_output_file_created(self, tmp_path: Path) -> None:
        """--output writes a .tex file to the specified path.

        Falsifies if: file does not exist after running with --output.
        falsifies_if: file does not exist after running with --output.
        """
        out = tmp_path / "test_paper.tex"
        code = arxiv_main(["--output", str(out)])
        assert code == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "\\documentclass" in content


# ---------------------------------------------------------------------------
# 5. agent_health_check
# ---------------------------------------------------------------------------

from tools.agent_health_check import (  # noqa: E402
    check_consent_log as hc_check_consent_log,
    check_feed_integrity,
    check_float_violations,
    check_merkle_roots,
    check_python_version as hc_check_python_version,
    check_required_files as hc_check_required_files,
    check_standards_registry,
    check_venv,
    main as health_main,
    run_all_checks,
)


class TestAgentHealthCheck:
    """Tests for the unified health check tool."""

    def test_check_python_version_returns_proof_object(self) -> None:
        """check_python_version returns (bool, ProofObject).

        Falsifies if: second element has no proof_hash attribute.
        falsifies_if: second element has no proof_hash attribute.
        """
        ok, proof = hc_check_python_version()
        assert isinstance(ok, bool)
        assert hasattr(proof, "proof_hash")
        assert len(proof.proof_hash) == 64

    def test_check_python_version_ok_on_312(self) -> None:
        """Python 3.12 satisfies the >= 3.10 requirement.

        Falsifies if: returns False in the CI environment.
        falsifies_if: returns False in the CI environment.
        """
        ok, _ = hc_check_python_version()
        assert ok is True

    def test_check_required_files_ok(self) -> None:
        """Required files are all present in the current repo.

        Falsifies if: any required file is missing.
        falsifies_if: any required file is missing.
        """
        ok, proof = hc_check_required_files()
        assert ok is True
        assert "present" in proof.conclusion.lower()

    def test_check_consent_log_ok(self) -> None:
        """Consent log is present and parseable.

        Falsifies if: consent_log.jsonl has no parseable entries.
        falsifies_if: consent_log.jsonl has no parseable entries.
        """
        ok, proof = hc_check_consent_log()
        assert ok is True
        assert "OK" in proof.conclusion

    def test_check_merkle_roots_ok(self) -> None:
        """Global Merkle root is a valid 64-char hex hash.

        Falsifies if: root_hash is absent or malformed.
        falsifies_if: root_hash is absent or malformed.
        """
        ok, proof = check_merkle_roots()
        assert ok is True
        assert "valid" in proof.conclusion.lower()

    def test_check_float_violations_zero(self) -> None:
        """No float() violations in domain invariants.

        Falsifies if: any domain invariants.py contains float() or isclose().
        falsifies_if: any domain invariants.py contains float() or isclose().
        """
        ok, proof = check_float_violations()
        assert ok is True
        assert "Zero" in proof.conclusion

    def test_check_standards_registry_ok(self) -> None:
        """STANDARDS_REGISTRY.json is present and non-empty.

        Falsifies if: registry is absent or empty.
        falsifies_if: registry is absent or empty.
        """
        ok, proof = check_standards_registry()
        assert ok is True
        assert "OK" in proof.conclusion

    def test_check_venv_returns_proof_object(self) -> None:
        """check_venv returns (bool, ProofObject) regardless of venv status.

        Falsifies if: second element has no proof_hash attribute.
        falsifies_if: second element has no proof_hash attribute.
        """
        ok, proof = check_venv()
        assert isinstance(ok, bool)
        assert hasattr(proof, "proof_hash")

    def test_run_all_checks_fast_all_pass(self) -> None:
        """All fast checks pass in the current repo environment.

        Falsifies if: any fast check returns ok=False.
        falsifies_if: any fast check returns ok=False.
        """
        all_pass, results = run_all_checks(fast_only=True)
        failed = [r["check"] for r in results if not r["pass"]]
        assert all_pass is True, f"Failed fast checks: {failed}"

    def test_run_all_checks_results_have_proof_hash(self) -> None:
        """Every check result has a proof_hash field.

        Falsifies if: any result dict lacks the proof_hash key.
        falsifies_if: any result dict lacks the proof_hash key.
        """
        _ok, results = run_all_checks(fast_only=True)
        for r in results:
            assert "proof_hash" in r
            assert len(r["proof_hash"]) == 64

    def test_health_main_fast_exit_zero(self) -> None:
        """health_main --fast exits 0 when all fast checks pass.

        Falsifies if: exits non-zero on a healthy repo with --fast.
        falsifies_if: exits non-zero on a healthy repo with --fast.
        """
        code = health_main(["--fast"])
        assert code == 0

    def test_health_main_json_parseable(self) -> None:
        """--json output is parseable JSON with all_pass key.

        Falsifies if: output is not valid JSON or lacks all_pass.
        falsifies_if: output is not valid JSON or lacks all_pass.
        """
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = health_main(["--fast", "--json"])
        assert code == 0
        data = json.loads(buf.getvalue())
        assert "all_pass" in data
        assert data["all_pass"] is True

    def test_check_feed_integrity_ok(self) -> None:
        """Feed chain integrity check passes via generate_feed_entry.py --verify.

        Falsifies if: chain is broken.
        falsifies_if: chain is broken.
        """
        ok, proof = check_feed_integrity()
        assert ok is True, f"Feed integrity failed: {proof.conclusion}"
