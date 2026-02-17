"""
Manifest Generation Example

Demonstrates manifest generation and verification.
"""

from pathlib import Path
import tempfile
import shutil

from scaffold import ManifestGenerator


def main():
    """Run manifest generation example."""
    print("=" * 60)
    print("Manifest Generation Example")
    print("=" * 60)
    
    # Create temporary repository
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test repository structure
        print("\n--- Creating Test Repository ---")
        
        # Root files
        (temp_dir / "README.md").write_text("# Test Repository\n\nThis is a test.")
        (temp_dir / "config.json").write_text('{"name": "test", "version": "1.0"}')
        
        # Source directory
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("def main():\n    print('Hello')")
        (src_dir / "utils.py").write_text("def util():\n    pass")
        
        # Data directory
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        (data_dir / "data.txt").write_text("Sample data")
        
        print(f"✓ Created test repository at: {temp_dir}")
        
        # Generate manifest
        print("\n--- Generating Manifest ---")
        generator = ManifestGenerator(
            repo_path=temp_dir,
            checkpoint_interval=2  # Save checkpoint every 2 files
        )
        
        processed = generator.generate(resume=False)
        stats = generator.get_statistics()
        
        print(f"✓ Manifest generated")
        print(f"  Total files found: {stats['total_files']}")
        print(f"  Files processed: {stats['processed_files']}")
        print(f"  Files skipped: {stats['skipped_files']}")
        print(f"  Errors: {stats['errors']}")
        
        # Display manifest entries
        print("\n--- Manifest Entries ---")
        for i, entry in enumerate(generator.iter_entries(), 1):
            print(f"{i}. {entry.canonical_path}")
            print(f"   Type: {entry.file_type}")
            print(f"   Hash: {entry.canonical_hash[:16]}...")
            print(f"   Size: {entry.size} bytes")
            print(f"   Content address: {entry.content_address[:30]}...")
        
        # Verify manifest
        print("\n--- Verifying Manifest ---")
        errors = generator.verify_manifest()
        
        if not errors:
            print("✓ Manifest verification: PASSED")
            print("  All files match their recorded hashes")
        else:
            print(f"✗ Manifest verification: FAILED ({len(errors)} errors)")
            for error in errors:
                print(f"  - {error}")
        
        # Demonstrate change detection
        print("\n--- Testing Change Detection ---")
        print("Modifying a file...")
        (temp_dir / "README.md").write_text("# Modified\n\nContent changed!")
        
        errors = generator.verify_manifest()
        
        if errors:
            print(f"✓ Change detected: {len(errors)} file(s) modified")
            for error in errors[:3]:  # Show first 3
                print(f"  - {error}")
        else:
            print("✗ No changes detected (unexpected)")
        
        # Demonstrate checkpoint resume
        print("\n--- Testing Checkpoint Resume ---")
        
        # Add a new file
        (temp_dir / "new_file.txt").write_text("New content")
        
        # Resume generation
        generator2 = ManifestGenerator(temp_dir, checkpoint_interval=2)
        processed_new = generator2.generate(resume=True)
        
        print(f"✓ Resumed generation")
        print(f"  Newly processed files: {processed_new}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("\n✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("Manifest generation example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
