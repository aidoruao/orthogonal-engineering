#!/usr/bin/env python3
"""
Zed on-save hook for Yeshua Mathematics verification.
Runs when any file is saved in Zed.
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

try:
    from generators.verify_all import YeshuaVerifier

    # Quick verification of just the saved file would go here
    # For now, we'll run a lightweight check
    print("🔍 Yeshua verification running...")

    verifier = YeshuaVerifier(repo_root)
    verifier.load_axioms()
    inventory = verifier.run_inventory()

    # Check if the saved file is in inventory and properly classified
    saved_file = sys.argv[1] if len(sys.argv) > 1 else None
    if saved_file:
        rel_path = str(Path(saved_file).relative_to(repo_root))
        if rel_path in inventory["files"]:
            entry = inventory["files"][rel_path]
            domains = entry["domains"]
            if domains:
                print(f"✅ {rel_path} mapped to domains: {', '.join(domains)}")
            else:
                print(f"⚠️ {rel_path} has no domain mapping")
        else:
            print(f"⚠️ {rel_path} not in inventory")

    print("✅ Yeshua verification complete")

except Exception as e:
    print(f"⚠️ Verification error: {e}")
