"""oe_engine._paths — Base path resolution for frozen and source builds.

When PyInstaller bundles the app as a single-file executable, data files are
extracted to a temporary directory accessible via ``sys._MEIPASS``.  Running
from source uses the repository root (current working directory).

falsifies_if: _base_path() returns a directory that does not contain src/domains.
"""

from __future__ import annotations

import pathlib
import sys


def _base_path() -> pathlib.Path:
    """Return the base path for data files.

    When frozen (PyInstaller), data is extracted to ``sys._MEIPASS``.
    When running from source, use the repository root (current working directory).

    Standard: PyInstaller one-file bundle path resolution convention.
    falsifies_if: returned path does not contain src/domains when engine loads.

    Returns:
        pathlib.Path pointing to the root of bundled data.
    """
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return pathlib.Path(".")
