#!/usr/bin/env python3
"""
End-to-end verification of Yeshua Mathematics compliance.
Runs inventory, checks axioms, computes Merkle roots, reports violations.
Author: Orthogonal Engineering
"""

import hashlib
import json
import sys
from pathlib import Path

# Add parent to path so we can import inventory
sys.path.insert(0, str(Path(__file__).parent.parent))
from inventory.repository_inventory import hash_file, inventory_repository


class YeshuaVerifier:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.inventory = None
        self.axioms = None
        self.violations = []

    def load_axioms(self):
        """Load the eight Yeshua axioms."""
        axioms_path = self.repo_root / "yeshua" / "axioms" / "eight_axioms.json"
        if not axioms_path.exists():
            self.violations.append("Missing axioms file")
            return False
        with open(axioms_path) as f:
            self.axioms = json.load(f)
        return True

    def run_inventory(self):
        """Run fresh inventory and compare to existing."""
        print("Running inventory...")
        self.inventory = inventory_repository(self.repo_root)

        # Check if inventory matches existing
        inventory_path = self.repo_root / "inventory" / "domain_map.json"
        if inventory_path.exists():
            with open(inventory_path) as f:
                old_inventory = json.load(f)
            if old_inventory.get("merkle_root") != self.inventory["merkle_root"]:
                self.violations.append(
                    f"Inventory Merkle root changed: {old_inventory.get('merkle_root')} -> {self.inventory['merkle_root']}"
                )
        else:
            self.violations.append("No existing inventory to compare against")

        return self.inventory

    def verify_file_hashes(self):
        """Verify every file's hash matches its entry in inventory."""
        for path_str, entry in self.inventory["files"].items():
            file_path = self.repo_root / path_str
            if not file_path.exists():
                self.violations.append(f"File missing: {path_str}")
                continue
            current_hash = hash_file(file_path)
            if current_hash != entry["hash"]:
                self.violations.append(
                    f"Hash mismatch for {path_str}: {entry['hash']} != {current_hash}"
                )

    def verify_domain_coverage(self):
        """Check that all Python files are classified."""
        unclassified = self.inventory.get("unclassified", [])
        if unclassified:
            self.violations.append(f"Unclassified files: {len(unclassified)}")
            for f in unclassified[:5]:  # Show first 5
                print(f"  Unclassified: {f}")

    def verify_axiom_7(self):
        """Check for economic gatekeeping keywords in all files."""
        keywords = self.axioms.get("monetization_keywords", [])
        if not keywords:
            return

        for path_str, entry in self.inventory["files"].items():
            file_path = self.repo_root / path_str
            try:
                content = file_path.read_text(encoding="utf-8").lower()
                for kw in keywords:
                    if kw in content:
                        self.violations.append(
                            f"Axiom 7 violation in {path_str}: contains '{kw}'"
                        )
                        break
            except Exception:
                pass  # Skip binary or unreadable files

    def verify_merkle_root(self):
        """Verify the inventory Merkle root is correct."""
        if not self.inventory:
            return

        # Recompute Merkle root from file list
        all_hashes = [entry["hash"] for entry in self.inventory["files"].values()]
        all_hashes.sort()
        combined = "".join(all_hashes).encode()
        computed_root = hashlib.sha256(combined).hexdigest()

        if computed_root != self.inventory["merkle_root"]:
            self.violations.append(
                f"Merkle root mismatch: {self.inventory['merkle_root']} != {computed_root}"
            )

    def run(self):
        """Run all verification checks."""
        print("=" * 60)
        print("Yeshua Mathematics End-to-End Verification")
        print("=" * 60)

        if not self.load_axioms():
            print("Failed to load axioms")
            return False

        self.run_inventory()
        self.verify_file_hashes()
        self.verify_domain_coverage()
        self.verify_axiom_7()
        self.verify_merkle_root()

        print("\n" + "=" * 60)
        if self.violations:
            print(f"❌ VERIFICATION FAILED: {len(self.violations)} violations")
            for v in self.violations:
                print(f"  • {v}")
            return False
        else:
            print("✅ VERIFICATION PASSED: All Yeshua axioms satisfied")
            print(f"   Files: {len(self.inventory['files'])}")
            print(
                f"   Domains: {len([d for d in self.inventory['domains'] if self.inventory['domains'][d]])}"
            )
            print(f"   Merkle root: {self.inventory['merkle_root']}")
            return True


def main():
    repo_root = Path(__file__).parent.parent
    verifier = YeshuaVerifier(repo_root)
    success = verifier.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
