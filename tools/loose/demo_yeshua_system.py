#!/usr/bin/env python3
"""
Demonstration script for Yeshua Mathematics system.
Shows all components working together with practical examples.
Author: Orthogonal Engineering
"""

import json
import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))


def demonstrate_inventory():
    """Demonstrate repository inventory functionality."""
    print("=" * 60)
    print("DEMONSTRATION 1: Repository Inventory")
    print("=" * 60)

    try:
        from inventory.repository_inventory import hash_file, inventory_repository

        repo_root = Path(__file__).parent
        inventory = inventory_repository(repo_root)

        print(f"✓ Inventory generated successfully")
        print(f"  Files analyzed: {len(inventory['files'])}")
        print(
            f"  Domains detected: {len([d for d in inventory['domains'] if inventory['domains'][d]])}"
        )
        print(f"  Merkle root: {inventory['merkle_root'][:16]}...")

        # Show some example file mappings
        print("\n  Example file mappings:")
        example_files = list(inventory["files"].keys())[:3]
        for file_path in example_files:
            entry = inventory["files"][file_path]
            domains = entry["domains"]
            if domains:
                print(f"    {file_path[:40]}... → {', '.join(domains)}")

        return True
    except Exception as e:
        print(f"✗ Inventory demonstration failed: {e}")
        return False


def demonstrate_axioms():
    """Demonstrate the eight Yeshua axioms."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 2: The Eight Axioms")
    print("=" * 60)

    try:
        axioms_path = Path(__file__).parent / "yeshua" / "axioms" / "eight_axioms.json"
        with open(axioms_path) as f:
            axioms = json.load(f)

        print(f"✓ Loaded {len(axioms['axioms'])} Yeshua axioms")

        for axiom in axioms["axioms"]:
            print(f"\n  Axiom {axiom['number']}: {axiom['statement']}")
            print(f"     Enforcement: {axiom['enforcement']}")
            print(f"     Falsification: {axiom['falsification']}")

        print(f"\n  Monetization keywords blocked:")
        for kw in axioms["monetization_keywords"]:
            print(f"    - {kw}")

        return True
    except Exception as e:
        print(f"✗ Axioms demonstration failed: {e}")
        return False


def demonstrate_domains():
    """Demonstrate the 39 mathematical domains."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 3: 39 Mathematical Domains")
    print("=" * 60)

    try:
        domains_path = (
            Path(__file__).parent / "yeshua" / "domains" / "39_domain_table.json"
        )
        with open(domains_path) as f:
            domains_data = json.load(f)

        domains = domains_data["domains"]
        summary = domains_data["summary"]

        print(
            f"✓ Loaded {summary['total']} domains ({summary['operational']} operational, {summary['specified']} specified)"
        )

        # Group by category
        categories = {}
        for domain in domains:
            category = domain["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(domain)

        print("\n  Domains by category:")
        for category, domain_list in categories.items():
            print(f"\n    {category} ({len(domain_list)} domains):")
            for domain in domain_list[:3]:  # Show first 3 per category
                status_icon = "✅" if domain["status"] == "OPERATIONAL" else "📋"
                print(f"      {status_icon} {domain['id']}: {domain['name']}")
            if len(domain_list) > 3:
                print(f"      ... and {len(domain_list) - 3} more")

        return True
    except Exception as e:
        print(f"✗ Domains demonstration failed: {e}")
        return False


def demonstrate_verification():
    """Demonstrate the verification system."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 4: End-to-End Verification")
    print("=" * 60)

    try:
        from generators.verify_all import YeshuaVerifier

        repo_root = Path(__file__).parent
        verifier = YeshuaVerifier(repo_root)

        print("Running verification...")
        success = verifier.run()

        if success:
            print("\n✓ Verification PASSED - All Yeshua axioms satisfied")
        else:
            print(
                f"\n✗ Verification FAILED - {len(verifier.violations)} violations found"
            )
            if verifier.violations:
                print("\n  Example violations:")
                for violation in verifier.violations[:5]:  # Show first 5
                    print(f"    • {violation[:80]}...")
                if len(verifier.violations) > 5:
                    print(f"    ... and {len(verifier.violations) - 5} more")

        return success
    except Exception as e:
        print(f"✗ Verification demonstration failed: {e}")
        return False


def demonstrate_game_grace_proof():
    """Demonstrate the Game Grace Proof system."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 5: Game Grace Proof")
    print("=" * 60)

    try:
        from researches.game_grace_proof.implementation import PlayerRunCounter

        print("Creating player and simulating dungeon runs...")

        # Create a player
        player = PlayerRunCounter("demo_player_001")

        # Simulate some runs
        dungeons = ["deadmines", "shadowfang", "scarlet_monastery"]
        bosses = ["van_cleef", "arugal", "whitemane"]

        for i in range(15):
            dungeon = dungeons[i % len(dungeons)]
            boss = bosses[i % len(bosses)]
            result = player.record_run(dungeon, boss)

            if (i + 1) % 5 == 0:
                print(
                    f"  Run {i + 1}: {dungeon}/{boss} → Hash: {result['proof']['hash'][:8]}..."
                )

        print(f"\n✓ Player statistics:")
        print(f"  Total runs: {player.run_count}")
        print(f"  Can claim item (threshold 50): {player.can_claim_item(50)}")
        print(f"  Can claim item (threshold 10): {player.can_claim_item(10)}")
        print(f"  Proof chain Merkle root: {player.get_proof_chain_hash()[:16]}...")

        # Demonstrate Peano arithmetic
        print(f"\n✓ Peano arithmetic demonstration:")
        print(f"  successor(5) = {player.successor(5)}")
        print(f"  peano_add(7, 8) = {player.peano_add(7, 8)}")
        print(f"  peano_add(15, 27) = {player.peano_add(15, 27)}")

        return True
    except Exception as e:
        print(f"✗ Game Grace Proof demonstration failed: {e}")
        return False


def demonstrate_zed_integration():
    """Demonstrate Zed IDE integration."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 6: Zed IDE Integration")
    print("=" * 60)

    try:
        hook_path = Path(__file__).parent / ".zed" / "hooks" / "on_save.py"

        if hook_path.exists():
            print("✓ Zed on-save hook installed:")
            print(f"  Location: {hook_path}")
            print("\n  The hook automatically runs when you save files in Zed:")
            print("  1. Checks if saved file is in inventory")
            print("  2. Verifies domain mapping")
            print("  3. Reports any issues")
            print("\n  Example output when saving a file:")
            print("    🔍 Yeshua verification running...")
            print(
                "    ✅ inventory/repository_inventory.py mapped to domains: AXIOM-001"
            )
            print("    ✅ Yeshua verification complete")
        else:
            print("✗ Zed hook not found at expected location")
            return False

        return True
    except Exception as e:
        print(f"✗ Zed integration demonstration failed: {e}")
        return False


def demonstrate_powershell_fix():
    """Demonstrate PowerShell execution policy fix."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 7: PowerShell Fix for GitHub Runners")
    print("=" * 60)

    try:
        ps_script_path = (
            Path(__file__).parent / "scripts" / "fix_windows_execution_policy.ps1"
        )

        if ps_script_path.exists():
            print("✓ PowerShell fix script available:")
            print(f"  Location: {ps_script_path}")
            print("\n  Usage (run as Administrator):")
            print("    .\\scripts\\fix_windows_execution_policy.ps1")
            print("\n  The script will:")
            print("  1. Check current execution policy")
            print("  2. Change to RemoteSigned if needed")
            print("  3. Test runner script functionality")
            print("  4. Report completion status")
        else:
            print("✗ PowerShell script not found at expected location")
            return False

        return True
    except Exception as e:
        print(f"✗ PowerShell fix demonstration failed: {e}")
        return False


def main():
    """Run all demonstrations."""
    print("🚀 Yeshua Mathematics System Demonstration")
    print("=" * 60)

    results = []

    # Run all demonstrations
    results.append(("Repository Inventory", demonstrate_inventory()))
    results.append(("Eight Axioms", demonstrate_axioms()))
    results.append(("39 Domains", demonstrate_domains()))
    results.append(("Verification System", demonstrate_verification()))
    results.append(("Game Grace Proof", demonstrate_game_grace_proof()))
    results.append(("Zed Integration", demonstrate_zed_integration()))
    results.append(("PowerShell Fix", demonstrate_powershell_fix()))

    # Summary
    print("\n" + "=" * 60)
    print("DEMONSTRATION SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nCompleted {successful}/{total} demonstrations successfully")

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {name}")

    if successful == total:
        print("\n🎉 All demonstrations completed successfully!")
        print("\nNext steps:")
        print("  1. Run: python inventory/repository_inventory.py")
        print("  2. Run: python generators/verify_all.py")
        print("  3. Try the Game Grace Proof with your own data")
        print("  4. Enable Zed hooks for real-time verification")
    else:
        print(f"\n⚠️ {total - successful} demonstrations failed")
        print("Check the error messages above and ensure all files are in place.")

    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
