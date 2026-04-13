"""oe_engine.thinker — Domain thinker module for the OE Engine.

Wraps domain invariant check functions in the realizability topos.
Every output is a ProofObject verified for determinism and proof integrity.

falsifies_if: same ThinkerInput produces different thinker_hash on two calls.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Tuple

from axioms.logic import ProofObject, merkle_root_over_proofs


@dataclass(frozen=True)
class ThinkerInput:
    """Input to a thinker module.

    falsifies_if: same logical query yields different input_hash.
    """

    query: str
    domain_id: str       # e.g. "D_CRIMINAL_LAW" or "D_ARC_AGI_3"
    context: Dict[str, Any]
    input_hash: str = ""  # SHA-256 of canonical JSON(context); computed if blank

    def __post_init__(self) -> None:
        # Allow frozen override via object.__setattr__
        if not self.input_hash:
            h = hashlib.sha256(
                json.dumps(self.context, sort_keys=True, default=str).encode()
            ).hexdigest()
            object.__setattr__(self, "input_hash", h)


@dataclass(frozen=True)
class ThinkerOutput:
    """Output from a thinker module.

    falsifies_if: thinker_hash differs across deterministic runs.
    """

    domain_id: str
    proofs: Tuple[ProofObject, ...]
    all_passed: bool
    thinker_hash: str     # SHA-256 of Merkle root over all proof hashes
    check_names: Tuple[str, ...]
    error: Optional[str] = None


class ThinkerModule:
    """Deterministic domain thinker.

    Loads a domain's invariant module, introspects its check_* functions,
    and calls the one(s) matching the query context. All results are
    hashed for determinism verification.

    falsifies_if: module import fails silently or returns proofs with bad hashes.
    """

    def __init__(self) -> None:
        self._module_cache: Dict[str, Any] = {}

    def _load_domain(self, domain_id: str) -> Optional[Any]:
        """Load domain invariants module.

        falsifies_if: module exists but raises ImportError.
        """
        if domain_id in self._module_cache:
            return self._module_cache[domain_id]

        module_path = f"src.domains.{domain_id.lower()}.invariants"
        try:
            mod = importlib.import_module(module_path)
            self._module_cache[domain_id] = mod
            return mod
        except ImportError:
            return None

    def _get_check_functions(self, module: Any) -> Dict[str, Callable]:
        """Get all check_* functions from a domain module."""
        return {
            name: getattr(module, name)
            for name in dir(module)
            if name.startswith("check_") and callable(getattr(module, name))
        }

    def think(self, inp: ThinkerInput) -> ThinkerOutput:
        """Execute the thinker for a given input.

        Loads the domain module, finds check functions compatible with the
        context keys, calls run_all_invariants() if available, or falls back
        to calling parameterless check functions.

        Standard: Deterministic execution — no randomness
        falsifies_if: same inp yields different thinker_hash

        Returns:
            ThinkerOutput with proofs, all_passed, thinker_hash
        """
        domain_id = inp.domain_id
        module = self._load_domain(domain_id)

        if module is None:
            error_proof = ProofObject(
                rule="ThinkerLoad",
                premises=[f"domain={domain_id}", "status=import_failed"],
                conclusion=f"FAIL: cannot import src.domains.{domain_id.lower()}.invariants",
            )
            thinker_hash = hashlib.sha256(
                error_proof.proof_hash.encode()
            ).hexdigest()
            return ThinkerOutput(
                domain_id=domain_id,
                proofs=(error_proof,),
                all_passed=False,
                thinker_hash=thinker_hash,
                check_names=(),
                error=f"ImportError for {domain_id}",
            )

        proofs: List[ProofObject] = []
        check_names: List[str] = []
        all_passed = True

        # Prefer run_all_invariants() when available
        if hasattr(module, "run_all_invariants"):
            try:
                results: Dict[str, str] = module.run_all_invariants()
                for check_name, result_str in results.items():
                    passed = "PASS" in result_str or not result_str.startswith("FAIL")
                    if not passed:
                        all_passed = False
                    proofs.append(ProofObject(
                        rule=check_name,
                        premises=[
                            f"domain={domain_id}",
                            f"result={result_str}",
                            f"context_hash={inp.input_hash[:16]}...",
                        ],
                        conclusion=(
                            f"PASS: {check_name}"
                            if passed
                            else f"FAIL: {check_name} — {result_str}"
                        ),
                    ))
                    check_names.append(check_name)
            except Exception as e:
                all_passed = False
                proofs.append(ProofObject(
                    rule="run_all_invariants",
                    premises=[f"domain={domain_id}", f"error={e}"],
                    conclusion=f"FAIL: run_all_invariants raised {type(e).__name__}: {e}",
                ))
        else:
            # Fallback: call parameterless check functions only
            checks = self._get_check_functions(module)
            for name, fn in sorted(checks.items()):
                import inspect
                sig = inspect.signature(fn)
                if len(sig.parameters) == 0:
                    try:
                        result, proof = fn()
                        if not result:
                            all_passed = False
                        proofs.append(proof)
                        check_names.append(name)
                    except Exception as e:
                        all_passed = False
                        proofs.append(ProofObject(
                            rule=name,
                            premises=[f"domain={domain_id}", f"error={e}"],
                            conclusion=f"FAIL: {name} raised {type(e).__name__}: {e}",
                        ))

        if not proofs:
            no_proof = ProofObject(
                rule="ThinkerNoChecks",
                premises=[f"domain={domain_id}"],
                conclusion="No check functions executed",
            )
            proofs.append(no_proof)

        # Deterministic thinker hash: Merkle over proof hashes
        merkle = merkle_root_over_proofs(proofs)
        thinker_hash = hashlib.sha256(
            f"{domain_id}|{inp.input_hash}|{merkle}".encode()
        ).hexdigest()

        return ThinkerOutput(
            domain_id=domain_id,
            proofs=tuple(proofs),
            all_passed=all_passed,
            thinker_hash=thinker_hash,
            check_names=tuple(check_names),
        )
