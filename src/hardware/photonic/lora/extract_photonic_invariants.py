#!/usr/bin/env python3
"""Extract photonic invariants from src/hardware/photonic/*.py for LoRA training.

Category 15: LoRA Training Dataset — extraction step.
"""

from __future__ import annotations

import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def _extract_falsifies_if(docstring: str) -> str:
    """Extract falsifies_if clause from docstring."""
    for line in docstring.splitlines():
        match = re.search(r"falsifies_if:\s*(.+)", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_thresholds(source: str) -> List[str]:
    """Extract Fraction threshold literals from source code."""
    return re.findall(r"Fraction\(\s*[-\d_]+\s*,\s*[-\d_]+\s*\)", source)


def extract_invariants_from_module(module) -> List[Dict[str, Any]]:
    """Extract check_* functions from a loaded module."""
    results: List[Dict[str, Any]] = []
    try:
        source = inspect.getsource(module)
    except (TypeError, OSError):
        source = ""

    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("check_"):
            continue
        doc = inspect.getdoc(obj) or ""
        falsifies = _extract_falsifies_if(doc)
        # Extract function body thresholds
        func_source = inspect.getsource(obj)
        thresholds = _extract_thresholds(func_source)
        results.append(
            {
                "id": f"PHOTON_{name}",
                "function": name,
                "module": getattr(module, "__name__", "unknown"),
                "docstring": doc.split("\n\n")[0] if doc else "",
                "falsifies_if": falsifies,
                "thresholds": thresholds,
            }
        )
    return results


def main() -> int:
    """CLI entry point."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    photonic_dir = repo_root / "src" / "hardware" / "photonic"
    out_dir = repo_root / "src" / "hardware" / "photonic" / "lora"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_invariants: List[Dict[str, Any]] = []

    # Dynamically import all non-test photonic modules
    for py_file in sorted(photonic_dir.glob("*.py")):
        if py_file.name.startswith("test_"):
            continue
        module_name = f"src.hardware.photonic.{py_file.stem}"
        try:
            # Add repo root to path for imports
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))
            module = __import__(module_name, fromlist=["*"])
            # Force reload in case previous import failed
            if module_name in sys.modules:
                import importlib
                module = importlib.reload(sys.modules[module_name])
            invariants = extract_invariants_from_module(module)
            all_invariants.extend(invariants)
        except Exception as exc:
            print(f"WARN: could not import {module_name}: {exc}", file=sys.stderr)

    out_path = out_dir / "photonic_invariants.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(all_invariants, fh, indent=2, sort_keys=True)

    print(f"Extracted {len(all_invariants)} invariants → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
