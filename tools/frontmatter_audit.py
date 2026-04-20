#!/usr/bin/env python3
"""Markdown YAML-frontmatter audit and backfill tool.

Every tracked Markdown file under the repository is required to begin with a
YAML frontmatter block of the form::

    ---
    tags: [<tag>, <tag>, ...]
    register: <register>
    ---

This module exposes three modes:

``--verify``
    Exit 0 if every non-exempt ``*.md`` file starts with a frontmatter block,
    exit 1 otherwise and print the offending paths.

``--add``
    Backfill missing frontmatter on every non-exempt file. Tags and register
    are inferred deterministically from the file path. Existing frontmatter
    blocks are never touched.

``--list``
    List every ``*.md`` file and whether it has frontmatter.

The tool uses only the standard library — no ``PyYAML`` dependency — and
writes UTF-8 with ``\\n`` line endings.

Exemptions live in :data:`EXEMPT_GLOBS` and cover auto-generated or vendored
paths (e.g. ``.git/``, ``.pytest_cache/``) where imposing frontmatter has no
reader; everything else must carry metadata.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

EXEMPT_GLOBS: Tuple[str, ...] = (
    ".git/*",
    ".git/**",
    ".pytest_cache/*",
    ".pytest_cache/**",
    "node_modules/*",
    "node_modules/**",
    "**/__pycache__/**",
    "htmlcov/*",
    "htmlcov/**",
    "venv/*",
    "venv/**",
    ".venv/*",
    ".venv/**",
    "site/*",
    "site/**",
    "_site/*",
    "_site/**",
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def is_exempt(rel: Path) -> bool:
    """Return True if ``rel`` matches any entry in :data:`EXEMPT_GLOBS`."""
    s = str(rel).replace("\\", "/")
    for glob in EXEMPT_GLOBS:
        if fnmatch.fnmatch(s, glob):
            return True
    return False


def find_markdown_files(root: Path) -> List[Path]:
    """Return every tracked ``*.md`` file under ``root`` in sorted order."""
    results: List[Path] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if is_exempt(rel):
            continue
        results.append(path)
    results.sort()
    return results


def has_frontmatter(text: str) -> bool:
    """Return True iff ``text`` starts with a ``---`` frontmatter block."""
    lstripped = text.lstrip("\ufeff")
    if not lstripped.startswith("---"):
        return False
    return bool(FRONTMATTER_RE.match(lstripped))


def _slug(segment: str) -> str:
    """Normalise a path segment into a slug-style tag."""
    s = segment.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "root"


def infer_metadata(rel: Path) -> Tuple[List[str], str]:
    """Infer ``(tags, register)`` for ``rel`` based on its path.

    The inference is deterministic and purely structural: directory segments
    become tags, and the top-level segment selects a register. This mirrors
    the pattern already present in manually-authored files such as
    ``CLAUDE.md`` and ``AGENT_CAPABILITIES_MATRIX.md``.
    """
    parts = rel.parts
    tags: List[str] = []
    for segment in parts[:-1]:
        tag = _slug(segment)
        if tag and tag not in tags:
            tags.append(tag)

    stem_tag = _slug(rel.stem)
    if stem_tag and stem_tag not in tags:
        tags.append(stem_tag)

    if not tags:
        tags = ["documentation"]

    top = parts[0].lower() if parts else ""
    if top in {"axioms", "kernel", "yeshua", "src", "oe_engine", "runtime", "automation"}:
        register = "technical"
    elif top in {"audit", "investigations", "evidence", "failure_log"}:
        register = "audit"
    elif top in {"tools", "toolkit"}:
        register = "tooling"
    elif top in {"docs", "documentation", "wiki"}:
        register = "documentation"
    elif top in {".github", "github"}:
        register = "governance"
    else:
        register = "documentation"

    return tags, register


def build_frontmatter(tags: Sequence[str], register: str) -> str:
    """Render a frontmatter block for the given ``tags`` and ``register``."""
    tag_list = "[" + ", ".join(tags) + "]"
    return f"---\ntags: {tag_list}\nregister: {register}\n---\n\n"


def _read_utf8_or_none(path: Path) -> str | None:
    """Return the file contents decoded as UTF-8, or ``None`` if not decodable.

    UTF-16/binary files masquerading as ``.md`` (e.g. legacy Windows exports)
    are skipped rather than rewritten, because prepending an ASCII frontmatter
    block would corrupt their byte order mark.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def prepend_frontmatter(path: Path) -> bool:
    """Prepend inferred frontmatter to ``path``.

    Returns True if the file was modified, False if it already had a
    frontmatter block or could not be decoded as UTF-8.
    """
    text = _read_utf8_or_none(path)
    if text is None:
        return False
    if has_frontmatter(text):
        return False
    rel = path.relative_to(REPO_ROOT)
    tags, register = infer_metadata(rel)
    fm = build_frontmatter(tags, register)
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    new_text = fm + text
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def cmd_list(files: Iterable[Path]) -> int:
    """Print every candidate file with its frontmatter status."""
    missing = 0
    total = 0
    for path in files:
        total += 1
        text = _read_utf8_or_none(path)
        if text is None:
            status = "SKIP"
        else:
            status = "OK  " if has_frontmatter(text) else "MISS"
        if status == "MISS":
            missing += 1
        print(f"{status} {path.relative_to(REPO_ROOT)}")
    print(f"\n{total} files, {missing} missing frontmatter")
    return 0


def cmd_verify(files: Iterable[Path]) -> int:
    """Exit non-zero if any candidate file lacks frontmatter."""
    missing: List[Path] = []
    total = 0
    for path in files:
        total += 1
        text = _read_utf8_or_none(path)
        if text is None:
            continue
        if not has_frontmatter(text):
            missing.append(path)
    if missing:
        sys.stderr.write(
            f"frontmatter_audit: {len(missing)} file(s) missing YAML frontmatter:\n"
        )
        for path in missing:
            sys.stderr.write(f"  {path.relative_to(REPO_ROOT)}\n")
        sys.stderr.write(
            "\nAdd a '--- tags: [...] register: ... ---' block at the top of each file,\n"
            "or run: python tools/frontmatter_audit.py --add\n"
        )
        return 1
    print(f"frontmatter_audit: {total} file(s) OK")
    return 0


def cmd_add(files: Iterable[Path]) -> int:
    """Backfill missing frontmatter on every candidate file."""
    modified = 0
    for path in files:
        if prepend_frontmatter(path):
            modified += 1
    print(f"frontmatter_audit: backfilled {modified} file(s)")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="List all markdown files and status.")
    mode.add_argument("--verify", action="store_true", help="Exit non-zero if any file lacks frontmatter.")
    mode.add_argument("--add", action="store_true", help="Backfill frontmatter on missing files.")
    args = parser.parse_args(argv)

    files = find_markdown_files(REPO_ROOT)
    if args.list:
        return cmd_list(files)
    if args.verify:
        return cmd_verify(files)
    if args.add:
        return cmd_add(files)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
