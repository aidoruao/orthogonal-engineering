"""Unit tests for :mod:`tools.frontmatter_audit`.

These tests exercise the pure helpers (detection, inference, injection) on a
temporary directory so they run in milliseconds and do not depend on the
exact set of Markdown files currently committed to the repository.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools import frontmatter_audit  # noqa: E402


def test_has_frontmatter_recognises_valid_block() -> None:
    text = "---\ntags: [a]\nregister: technical\n---\n\nBody"
    assert frontmatter_audit.has_frontmatter(text)


def test_has_frontmatter_rejects_missing_block() -> None:
    text = "# Heading\n\nBody"
    assert not frontmatter_audit.has_frontmatter(text)


def test_has_frontmatter_rejects_unterminated_block() -> None:
    text = "---\ntags: [a]\n"
    assert not frontmatter_audit.has_frontmatter(text)


def test_infer_metadata_domain_path() -> None:
    tags, register = frontmatter_audit.infer_metadata(Path("src/domains/d_graphics_reality/README.md"))
    assert "src" in tags
    assert "domains" in tags
    assert "d-graphics-reality" in tags
    assert register == "technical"


def test_infer_metadata_tools_path() -> None:
    tags, register = frontmatter_audit.infer_metadata(Path("tools/standards_check.md"))
    assert "tools" in tags
    assert register == "tooling"


def test_infer_metadata_root_file() -> None:
    tags, register = frontmatter_audit.infer_metadata(Path("CHANGELOG.md"))
    assert "changelog" in tags
    assert register == "documentation"


def test_infer_metadata_evidence_path_routes_to_audit() -> None:
    tags, register = frontmatter_audit.infer_metadata(
        Path("evidence/bowers_mcneil/FORENSIC_DISCREPANCY_REPORT.md")
    )
    assert "evidence" in tags
    assert register == "audit"


def test_infer_metadata_failure_log_path_routes_to_audit() -> None:
    tags, register = frontmatter_audit.infer_metadata(
        Path("failure_log/PHANTOM_EDIT_001.md")
    )
    assert "failure-log" in tags
    assert register == "audit"


def test_prepend_frontmatter_adds_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frontmatter_audit, "REPO_ROOT", tmp_path)
    target = tmp_path / "NOTES.md"
    target.write_text("# Hello\n\nworld\n", encoding="utf-8")

    modified = frontmatter_audit.prepend_frontmatter(target)

    assert modified is True
    body = target.read_text(encoding="utf-8")
    assert body.startswith("---\n")
    assert "tags:" in body
    assert "register:" in body
    assert "# Hello" in body


def test_prepend_frontmatter_skips_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frontmatter_audit, "REPO_ROOT", tmp_path)
    target = tmp_path / "NOTES.md"
    original = "---\ntags: [keep]\nregister: technical\n---\n\nBody\n"
    target.write_text(original, encoding="utf-8")

    modified = frontmatter_audit.prepend_frontmatter(target)

    assert modified is False
    assert target.read_text(encoding="utf-8") == original


def test_prepend_frontmatter_skips_non_utf8(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frontmatter_audit, "REPO_ROOT", tmp_path)
    target = tmp_path / "legacy.md"
    target.write_bytes(b"\xff\xfe# L\x00e\x00g\x00a\x00c\x00y\x00")

    modified = frontmatter_audit.prepend_frontmatter(target)

    assert modified is False
    assert target.read_bytes().startswith(b"\xff\xfe")


def test_is_exempt_covers_pytest_cache() -> None:
    assert frontmatter_audit.is_exempt(Path(".pytest_cache/README.md"))


def test_is_exempt_skips_regular_paths() -> None:
    assert not frontmatter_audit.is_exempt(Path("src/domains/d_necessity/README.md"))


def test_verify_flags_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frontmatter_audit, "REPO_ROOT", tmp_path)
    (tmp_path / "MISSING.md").write_text("# no frontmatter\n", encoding="utf-8")
    files = frontmatter_audit.find_markdown_files(tmp_path)

    code = frontmatter_audit.cmd_verify(files)

    assert code == 1


def test_verify_passes_when_all_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(frontmatter_audit, "REPO_ROOT", tmp_path)
    (tmp_path / "OK.md").write_text(
        "---\ntags: [ok]\nregister: technical\n---\n\nBody\n", encoding="utf-8"
    )
    files = frontmatter_audit.find_markdown_files(tmp_path)

    code = frontmatter_audit.cmd_verify(files)

    assert code == 0
