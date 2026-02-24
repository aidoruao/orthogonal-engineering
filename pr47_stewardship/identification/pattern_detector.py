# pr47_stewardship/identification/pattern_detector.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# PatternDetector: identifies artifacts needing boundary transition.
#
# Design constraints:
#   - Reason codes are opaque (e.g. "R1") — no personal identifiers recorded.
#   - No sensitive terms appear in log output or reason strings.
#   - Detection is purely pattern-based; no content is read.

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


# Opaque reason codes (keys) paired with their regex patterns (values).
# Codes are deliberately terse so log output contains no sensitive terms.
SENSITIVE_PATTERNS: list[tuple[str, str]] = [
    ("R1", r"(?i)(hrt.*(backup|export|log)|backup.*hrt)"),
    ("R2", r"(?i)chat.*\.jsonl?$"),
    ("R3", r"(?i)conversation.*\.txt$"),
    ("R4", r"(?i)personal.*\.md$"),
    ("R5", r"(?i)(export|backup).*\.(zip|tar\.gz|tgz|gz)$"),
]

_COMPILED: list[tuple[str, re.Pattern]] = [
    (code, re.compile(pattern)) for code, pattern in SENSITIVE_PATTERNS
]


@dataclass(frozen=True)
class Candidate:
    """An artifact path that matches at least one sensitive pattern."""
    path: str
    reason_code: str  # opaque: "R1"–"R5"


class PatternDetector:
    """
    Identify artifacts that need a boundary transition without recording
    personal identifiers or sensitive terms in the output.

    Parameters:
      extra_patterns — additional (reason_code, regex_str) pairs to append.
    """

    def __init__(
        self, extra_patterns: list[tuple[str, str]] | None = None
    ) -> None:
        self._patterns: list[tuple[str, re.Pattern]] = list(_COMPILED)
        if extra_patterns:
            for code, pattern in extra_patterns:
                self._patterns.append((code, re.compile(pattern)))

    def find_candidates(self, repo_path: str | Path) -> List[Candidate]:
        """
        Walk repo_path and return all files matching a sensitive pattern.

        Returns:
          List[Candidate]: each with path (relative to repo_path) and reason_code.
          A file matching multiple patterns is reported once (first match wins).
        """
        root = Path(repo_path)
        candidates: List[Candidate] = []
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file():
                continue
            rel = str(file_path.relative_to(root))
            for code, pattern in self._patterns:
                if pattern.search(rel):
                    candidates.append(Candidate(path=rel, reason_code=code))
                    break
        return candidates
