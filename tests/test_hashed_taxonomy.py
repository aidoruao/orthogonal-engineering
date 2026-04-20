"""Tests for tools/generate_hashed_taxonomy.py.

Falsifies if: two runs over the same working tree produce different
``audit_sha256`` commitments, or if any detector flags a line that does not
contain the pattern it claims to detect.
falsifies_if: two runs over the same working tree produce different
audit_sha256 commitments.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.generate_hashed_taxonomy import (
    ISSUE_SEVERITY,
    NAMESPACE_KEYWORDS,
    _canonical_json,
    _namespaces_for_text,
    _scan_check_function,
    _scan_line_level,
    _sha256_text,
    build_entries,
    main,
)


def test_canonical_json_is_sorted_and_compact() -> None:
    """Canonical JSON must be stable across dict ordering and have no spaces."""
    a = _canonical_json({"b": 2, "a": 1})
    b = _canonical_json({"a": 1, "b": 2})
    assert a == b
    assert a == '{"a":1,"b":2}'


def test_sha256_is_64_hex() -> None:
    """``_sha256_text`` returns 64-char lowercase hex.

    Falsifies if: the digest is not 64 lowercase hex characters.
    falsifies_if: the digest is not 64 lowercase hex characters.
    """
    digest = _sha256_text("hello")
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_namespace_classification_matches_known_keywords() -> None:
    """Every namespace label has at least one keyword defined."""
    for label, kws in NAMESPACE_KEYWORDS.items():
        assert kws, f"namespace {label} has no keywords"
    hits = _namespaces_for_text("using the yeshua standard", "src/domains/d_aerospace/file.py")
    assert "yeshua" in hits
    assert "aerospace" in hits


def test_line_level_scanner_finds_each_pattern() -> None:
    """Each pattern family is detected on a representative Python line."""
    text = "\n".join(
        [
            "# TODO: fix later",
            "x = float(1)",
            "    pass",
            "raise NotImplementedError",
            "y: float = 0.0",
            "assert x > 0",
        ]
    )
    hits = _scan_line_level(text, is_python=True)
    kinds = {kind for _, kind, _ in hits}
    assert {
        "TODO",
        "FLOAT_CALL",
        "STUB_PASS",
        "STUB_NOTIMPL",
        "FLOAT_ANNOT",
        "ASSERT_USE",
    }.issubset(kinds)


def test_line_level_scanner_skips_python_only_patterns_for_non_python() -> None:
    """Non-Python text should only match prose-level patterns like TODO.

    Falsifies if: running the scanner against non-Python text emits issue
    types that are meant to be Python-only (``ASSERT_USE``, ``STUB_PASS``,
    etc.), producing cross-language false positives.
    falsifies_if: non-Python text emits Python-only issue types.
    """
    text = "\n".join(
        [
            "# TODO: fix later",
            "The word assert appears in prose.",
            "pass",  # prose paragraph mentioning 'pass'
            "float(1) referenced in documentation",
        ]
    )
    hits = _scan_line_level(text, is_python=False)
    kinds = {kind for _, kind, _ in hits}
    assert kinds == {"TODO"}


def test_check_function_scanner_flags_missing_contract(tmp_path: Path) -> None:
    """``check_*`` without ``Tuple[bool, ProofObject]`` annotation is flagged."""
    src = tmp_path / "m.py"
    src.write_text(
        '''
def check_thing():
    """No return annotation, no falsifies_if doc."""
    return True
'''
    )
    hits = _scan_check_function(src, src.read_text())
    kinds = {kind for _, kind, _ in hits}
    assert "CHECK_MISSING_PROOFOBJECT" in kinds
    assert "CHECK_MISSING_FALSIFIES_IF_PAIR" in kinds


def test_build_entries_is_deterministic(tmp_path: Path) -> None:
    """Two runs of ``build_entries`` over the same tree yield equal output.

    Falsifies if: repeated invocations produce different entry lists or summaries.
    falsifies_if: repeated invocations produce different entry lists or summaries.
    """
    (tmp_path / "a.py").write_text(
        "# TODO: demo\n"
        "def check_x():\n"
        "    pass\n"
    )
    (tmp_path / "b.md").write_text("# yeshua popperian projection\n")
    e1, s1 = build_entries(tmp_path)
    e2, s2 = build_entries(tmp_path)
    assert s1 == s2
    assert sorted(e["entry_sha256"] for e in e1) == sorted(e["entry_sha256"] for e in e2)


def test_main_writes_artifacts(tmp_path: Path) -> None:
    """``main`` writes a JSONL and a summary JSON with ``audit_sha256``."""
    out_jsonl = tmp_path / "tax.jsonl"
    out_json = tmp_path / "gap.json"
    rc = main(["--root", str(tmp_path), "--out", str(out_jsonl), "--summary", str(out_json)])
    assert rc == 0
    assert out_jsonl.exists()
    assert out_json.exists()
    doc = json.loads(out_json.read_text())
    assert doc["schema"] == "OE-GAP-ANALYSIS-1.0"
    assert len(doc["audit_sha256"]) == 64


def test_severity_map_covers_all_issue_types() -> None:
    """Every issue type that the scanners can emit has a severity mapping."""
    known_issue_types = {
        "TODO",
        "FIXME",
        "HACK",
        "STUB_PASS",
        "STUB_NOTIMPL",
        "FLOAT_CALL",
        "FLOAT_ANNOT",
        "CHECK_MISSING_PROOFOBJECT",
        "CHECK_MISSING_FALSIFIES_IF_PAIR",
        "ASSERT_USE",
    }
    assert known_issue_types.issubset(set(ISSUE_SEVERITY.keys()))


def test_namespace_counts_account_for_unclassified(tmp_path: Path) -> None:
    """Per-namespace counts must sum to at least the total issue count.

    Falsifies if: summed namespace counts are less than the total issue
    count, indicating silently dropped ``unclassified`` entries.
    falsifies_if: summed namespace counts < issue_count_total.
    """
    (tmp_path / "no_namespace.py").write_text(
        "# TODO: nothing classifiable here\n"
        "assert True\n"
    )
    _, summary = build_entries(tmp_path)
    total = summary["issue_count_total"]
    ns_total = sum(summary["issue_count_by_namespace"].values())
    assert ns_total >= total
    assert "unclassified" in summary["issue_count_by_namespace"]


def test_gap_analysis_metadata_is_outside_commitment(tmp_path: Path) -> None:
    """Non-deterministic fields live under ``metadata`` and are documented.

    Falsifies if: ``generated_at_utc`` or ``jsonl_path`` appear at the top
    level of the gap-analysis document (where they could mislead readers
    into thinking they are covered by ``audit_sha256``).
    falsifies_if: non-deterministic fields are not segregated under
    ``metadata``.
    """
    out_jsonl = tmp_path / "tax.jsonl"
    out_json = tmp_path / "gap.json"
    (tmp_path / "a.py").write_text("# TODO: x\n")
    rc = main(["--root", str(tmp_path), "--out", str(out_jsonl), "--summary", str(out_json)])
    assert rc == 0
    doc = json.loads(out_json.read_text())
    assert "generated_at_utc" not in doc
    assert "jsonl_path" not in doc
    assert "repo_root" not in doc
    assert doc["metadata"]["not_covered_by_audit_sha256"]
    assert "generated_at_utc" in doc["metadata"]


def test_check_function_window_does_not_bleed_into_adjacent_def(tmp_path: Path) -> None:
    """A second ``check_*`` function's docstring must not satisfy the first.

    Falsifies if: ``_scan_check_function`` fails to flag
    ``CHECK_MISSING_PROOFOBJECT`` / ``CHECK_MISSING_FALSIFIES_IF_PAIR`` on a
    bare ``check_*`` whose next-40-lines window overlaps a well-formed
    adjacent ``check_*`` (window-bleed false negative).
    falsifies_if: bleed-through masks missing contract on first check_*.
    """
    src = tmp_path / "adjacent.py"
    src.write_text(
        "from typing import Tuple\n"
        "from axioms.logic import ProofObject\n"
        "\n"
        "def check_a():\n"
        "    return True\n"
        "\n"
        "def check_b() -> Tuple[bool, ProofObject]:\n"
        "    '''Invariant.\n"
        "\n"
        "    Falsifies if: b fails.\n"
        "    falsifies_if: b fails.\n"
        "    '''\n"
        "    return True, ProofObject()\n"
    )
    hits = _scan_check_function(src, src.read_text())
    lines = {(line, kind) for line, kind, _ in hits}
    first_def_line = 4  # ``def check_a()``
    assert (first_def_line, "CHECK_MISSING_PROOFOBJECT") in lines
    assert (first_def_line, "CHECK_MISSING_FALSIFIES_IF_PAIR") in lines


def test_falsifies_if_title_case_is_strictly_enforced(tmp_path: Path) -> None:
    """Lowercase-only ``falsifies if:`` must NOT satisfy title-case check.

    Falsifies if: a docstring containing only lowercase ``falsifies if:`` and
    ``falsifies_if:`` passes the title-case contract and no
    ``CHECK_MISSING_FALSIFIES_IF_PAIR`` is emitted.
    falsifies_if: scanner accepts lowercase-only docstrings.
    """
    src = tmp_path / "case.py"
    src.write_text(
        "from typing import Tuple\n"
        "from axioms.logic import ProofObject\n"
        "\n"
        "def check_case() -> Tuple[bool, ProofObject]:\n"
        "    '''Invariant.\n"
        "\n"
        "    falsifies if: lower only.\n"
        "    falsifies_if: lower only.\n"
        "    '''\n"
        "    return True, ProofObject()\n"
    )
    hits = _scan_check_function(src, src.read_text())
    kinds = {kind for _, kind, _ in hits}
    assert "CHECK_MISSING_FALSIFIES_IF_PAIR" in kinds


def test_projection_namespace_keywords_are_narrow() -> None:
    """The bare English word 'projection' must not alone classify the file.

    Falsifies if: the ``projection`` namespace matches text that contains
    only the English word ``projection`` (without the specific compound
    keywords such as ``projected_namespace``).
    falsifies_if: bare 'projection' classifies as projection namespace.
    """
    ns = _namespaces_for_text("The projection operator is linear.", "docs/math.md")
    assert "projection" not in ns
    ns2 = _namespaces_for_text("A projected_namespace view of domain X.", "src/x.py")
    assert "projection" in ns2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
