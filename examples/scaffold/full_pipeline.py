"""
Full Pipeline Example

Demonstrates complete scaffold workflow:
1. Backup repository
2. Index files
3. Build Merkle tree
4. Verify integrity
5. Process handling.meta
"""

import sys
import tempfile
from pathlib import Path
import shutil

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.scaffold.cli import ScaffoldCLI


def main():
    """Run full pipeline demonstration."""
    print("=" * 70)
    print("Full Scaffold Pipeline Example")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a sample repository
        print("\n1. Setting up test repository")
        print("-" * 70)
        
        repo_path = temp_path / "test_repo"
        repo_path.mkdir()
        
        # Create sample files
        (repo_path / "file1.txt").write_text("Content 1\n")
        (repo_path / "file2.txt").write_text("Content 2\n")
        (repo_path / "data.json").write_text('{"z": 3, "a": 1}')
        
        # Create handling.meta
        from toolkit.oe.scaffold.handling_pipeline import create_sample_handling_meta
        create_sample_handling_meta(repo_path / "handling.meta")
        
        print(f"Created test repository at: {repo_path}")
        print(f"Files: {len(list(repo_path.glob('*')))}")
        
        # Initialize CLI
        cli = ScaffoldCLI()
        
        # Step 1: Backup
        print("\n2. Creating backup")
        print("-" * 70)
        
        backup_path = temp_path / "backup"
        result = cli.run(["backup", str(repo_path), "--output", str(backup_path)])
        
        if result == 0:
            print("✓ Backup created successfully")
        else:
            print("✗ Backup failed")
            return 1
        
        # Step 2: Index repository
        print("\n3. Indexing repository")
        print("-" * 70)
        
        manifest_path = repo_path / "manifest.jsonl"
        result = cli.run([
            "index", str(repo_path),
            "--apply",
            "--output", str(manifest_path)
        ])
        
        if result == 0:
            print("✓ Manifest generated successfully")
            
            # Show manifest
            with open(manifest_path) as f:
                line_count = sum(1 for _ in f)
            print(f"  Entries: {line_count}")
        else:
            print("✗ Indexing failed")
            return 1
        
        # Step 3: Build Merkle tree
        print("\n4. Building Merkle tree")
        print("-" * 70)
        
        proofs_path = repo_path / "merkle_proofs.jsonl"
        result = cli.run([
            "merkle", str(repo_path),
            "--apply",
            "--output", str(proofs_path)
        ])
        
        if result == 0:
            print("✓ Merkle tree built successfully")
            
            # Show proofs
            with open(proofs_path) as f:
                proof_count = sum(1 for _ in f)
            print(f"  Proofs: {proof_count}")
        else:
            print("✗ Merkle tree building failed")
            return 1
        
        # Step 4: Verify integrity
        print("\n5. Verifying integrity")
        print("-" * 70)
        
        result = cli.run([
            "verify", str(manifest_path),
            "--repo-path", str(repo_path)
        ])
        
        if result == 0:
            print("✓ All files verified successfully")
        else:
            print("⚠ Some files failed verification (expected if logs changed)")
        
        # Step 5: Process handling.meta
        print("\n6. Processing handling.meta")
        print("-" * 70)
        
        handling_path = repo_path / "handling.meta"
        report_path = temp_path / "handling_report.json"
        
        result = cli.run([
            "handling-clamp", str(handling_path),
            "--report", str(report_path)
        ])
        
        if result == 0:
            print("✓ Handling.meta processed successfully")
            
            # Show report
            import json
            with open(report_path) as f:
                report = json.load(f)
            print(f"  Vehicles processed: {len(report)}")
            
            total_violations = sum(len(r.get("violations", [])) for r in report)
            print(f"  Violations found: {total_violations}")
        else:
            print("✗ Handling processing failed")
            return 1
        
        # Summary
        print("\n" + "=" * 70)
        print("Pipeline Summary")
        print("=" * 70)
        
        print("\nArtifacts created:")
        print(f"  ✓ Backup: {backup_path}")
        print(f"  ✓ Manifest: {manifest_path}")
        print(f"  ✓ Merkle proofs: {proofs_path}")
        print(f"  ✓ Handling report: {report_path}")
        
        print("\nLogs created:")
        for log_file in repo_path.glob("*.jsonl"):
            if log_file.name not in ["manifest.jsonl", "merkle_proofs.jsonl"]:
                print(f"  ✓ {log_file.name}")
        
        print("\n" + "=" * 70)
        print("Full pipeline completed successfully!")
        print("=" * 70)
        
        return 0


if __name__ == "__main__":
    sys.exit(main())
