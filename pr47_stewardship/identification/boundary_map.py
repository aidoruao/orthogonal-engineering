# pr47_stewardship/identification/boundary_map.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# BoundaryMap: classifies paths into public / local / encrypted boundaries.
# All boundary types are explicit; no path is implicitly public.

from __future__ import annotations

from enum import Enum


class Boundary(str, Enum):
    """The three recognized artifact boundaries."""
    PUBLIC = "public"
    LOCAL = "local"
    ENCRYPTED = "encrypted"


# Default boundary classifications by path prefix.
# Entries are matched longest-prefix-first.
DEFAULT_BOUNDARY_RULES: list[tuple[str, Boundary]] = [
    ("hrt_backups/", Boundary.LOCAL),
    ("hrt_sanitization_backups/", Boundary.LOCAL),
    ("chat_jsonl/", Boundary.LOCAL),
    ("downloads/", Boundary.LOCAL),
    ("forgiveness_all_exports_output/", Boundary.LOCAL),
    ("forgiveness_main_exports_output/", Boundary.LOCAL),
]


class BoundaryMap:
    """
    Maps a relative repository path to its target boundary.

    Parameters:
      rules — ordered list of (prefix, Boundary) pairs.
              Longest match wins. If no rule matches, the path is PUBLIC.
    """

    def __init__(
        self, rules: list[tuple[str, Boundary]] | None = None
    ) -> None:
        self._rules: list[tuple[str, Boundary]] = (
            rules if rules is not None else list(DEFAULT_BOUNDARY_RULES)
        )
        # Sort by descending prefix length so longest match is found first.
        self._rules.sort(key=lambda r: len(r[0]), reverse=True)

    def classify(self, rel_path: str) -> Boundary:
        """
        Return the Boundary for rel_path.

        The first (longest) matching prefix rule wins.
        Paths with no matching rule are classified as PUBLIC.
        """
        for prefix, boundary in self._rules:
            if rel_path.startswith(prefix):
                return boundary
        return Boundary.PUBLIC

    def add_rule(self, prefix: str, boundary: Boundary) -> None:
        """Add a new prefix rule and re-sort."""
        self._rules.append((prefix, boundary))
        self._rules.sort(key=lambda r: len(r[0]), reverse=True)
