"""Full engine boot/import integration checks."""

from __future__ import annotations

from oe_engine._paths import _base_path
from oe_engine.manifest import EngineManifest
from oe_engine.thinker import ThinkerInput, ThinkerModule


def test_full_engine_boot_and_all_domain_thinks() -> None:
    """Engine manifest count/imports should match runtime thinker execution."""
    manifest = EngineManifest()
    thinker = ThinkerModule()

    invariants_files = list((_base_path() / "src" / "domains").glob("*/invariants.py"))
    assert manifest.domain_count == len(invariants_files)

    for entry in manifest.entries:
        out = thinker.think(
            ThinkerInput(
                query=f"boot-check:{entry.domain_id}",
                domain_id=entry.domain_id,
                context={},
            )
        )
        assert out.error is None, f"{entry.domain_id} import failed: {out.error}"
        assert len(out.proofs) > 0, f"{entry.domain_id} produced no proofs"
