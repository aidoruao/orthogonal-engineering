"""oe_engine.manifest — Domain hash registry for the OE Engine.

Enumerates all registered domain invariant modules, computes a SHA-256
commitment over each module's source, and produces a deterministic
manifest hash for the full engine state.

falsifies_if: manifest_hash changes without a corresponding domain source change.
"""

from __future__ import annotations

import hashlib
import importlib
import pathlib
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class DomainEntry:
    """A single domain registered in the engine manifest.

    falsifies_if: domain_id is empty or source_hash is not a valid SHA-256 hex.
    """

    domain_id: str
    module_path: str
    source_hash: str  # SHA-256 of the invariants.py source text
    check_count: int  # number of check_* functions found


class EngineManifest:
    """Deterministic registry of all domain invariant modules.

    Loads every src/domains/d_*/invariants.py, hashes its source, and
    produces a single manifest_hash that commits to the full domain state.

    falsifies_if: manifest_hash == prior_hash after modifying any invariants.py.
    """

    def __init__(self) -> None:
        self._entries: List[DomainEntry] = []
        self._manifest_hash: str = ""
        self._load()

    def _load(self) -> None:
        base = pathlib.Path("src/domains")
        entries: List[DomainEntry] = []
        for inv_file in sorted(base.glob("*/invariants.py")):
            domain_dir = inv_file.parent.name  # e.g. "d_criminal_law"
            domain_id = domain_dir.upper()     # e.g. "D_CRIMINAL_LAW"
            source = inv_file.read_text(encoding="utf-8")
            source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()

            # Count check_* functions (simple grep; no AST needed for manifest)
            import ast
            try:
                tree = ast.parse(source)
                check_count = sum(
                    1
                    for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name.startswith("check_")
                )
            except SyntaxError:
                check_count = 0

            module_path = f"src.domains.{domain_dir}.invariants"
            entries.append(DomainEntry(
                domain_id=domain_id,
                module_path=module_path,
                source_hash=source_hash,
                check_count=check_count,
            ))

        self._entries = entries
        # Deterministic manifest hash: SHA-256 of sorted domain hashes
        combined = "|".join(
            f"{e.domain_id}:{e.source_hash}" for e in self._entries
        )
        self._manifest_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @property
    def domain_count(self) -> int:
        """Number of registered domains."""
        return len(self._entries)

    @property
    def domain_hashes(self) -> Dict[str, str]:
        """Map of domain_id → source_hash."""
        return {e.domain_id: e.source_hash for e in self._entries}

    @property
    def manifest_hash(self) -> str:
        """SHA-256 commitment over all domain sources."""
        return self._manifest_hash

    @property
    def entries(self) -> List[DomainEntry]:
        """Ordered list of domain entries."""
        return list(self._entries)

    def check_manifest_integrity(self) -> Tuple[bool, ProofObject]:
        """Verify manifest is self-consistent.

        Standard: SHA-256 determinism
        falsifies_if: recomputed hash != stored manifest_hash

        Returns:
            Tuple of (success: bool, proof: ProofObject)
        """
        # Recompute
        combined = "|".join(
            f"{e.domain_id}:{e.source_hash}" for e in self._entries
        )
        recomputed = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        success = recomputed == self._manifest_hash
        return success, ProofObject(
            rule="ManifestIntegrity",
            premises=[
                f"domain_count={len(self._entries)}",
                f"stored_hash={self._manifest_hash[:16]}...",
                f"recomputed_hash={recomputed[:16]}...",
            ],
            conclusion=(
                f"Manifest integrity verified: {len(self._entries)} domains"
                if success
                else f"FAIL: manifest hash mismatch"
            ),
        )
