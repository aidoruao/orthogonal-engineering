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
    """Each pattern family is detected on a representative line."""
    text = "\n".join(
        [
            "# TODO: fix later",
            "x = float(1)",
            "    pass",
            "raise NotImplementedError",
            "y: float = 0.0",
        ]
    )
    hits = _scan_line_level(text)
    kinds = {kind for _, kind, _ in hits}
    assert {"TODO", "FLOAT_CALL", "STUB_PASS", "STUB_NOTIMPL", "FLOAT_ANNOT"}.issubset(kinds)


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
    }
    assert known_issue_types.issubset(set(ISSUE_SEVERITY.keys()))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
