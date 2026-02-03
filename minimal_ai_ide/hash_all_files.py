import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None


def should_ignore_path(path, gitignore_patterns):
    """Check if path should be ignored based on .gitignore patterns."""
    path_str = str(path)
    for pattern in gitignore_patterns:
        # Simple pattern matching - for production use, implement proper gitignore parsing
        if pattern.startswith("*"):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False


def read_gitignore(root_dir):
    """Read .gitignore file and return list of patterns."""
    gitignore_path = os.path.join(root_dir, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def hash_all_files(root_dir, output_file="file_hashes.json"):
    """Hash all files in directory and subdirectories."""
    root_path = Path(root_dir)
    gitignore_patterns = read_gitignore(root_dir)

    file_hashes = {}
    total_files = 0
    hashed_files = 0
    errors = 0

    print(f"Starting SHA-256 hashing of all files in: {root_dir}")
    print(f"Ignoring patterns from .gitignore: {gitignore_patterns}")

    # Walk through all files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip directories that should be ignored
        dirpath_rel = Path(dirpath).relative_to(root_path)
        if should_ignore_path(dirpath_rel, gitignore_patterns):
            continue

        for filename in filenames:
            file_path = Path(dirpath) / filename
            file_rel_path = file_path.relative_to(root_path)

            # Skip files that should be ignored
            if should_ignore_path(file_rel_path, gitignore_patterns):
                continue

            total_files += 1

            # Calculate hash
            file_hash = calculate_file_hash(file_path)

            if file_hash:
                file_hashes[str(file_rel_path)] = {
                    "sha256": file_hash,
                    "size_bytes": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat(),
                }
                hashed_files += 1

                # Progress indicator
                if hashed_files % 100 == 0:
                    print(f"  Hashed {hashed_files} files...")
            else:
                errors += 1

    # Save results to JSON file
    results = {
        "metadata": {
            "root_directory": str(root_dir),
            "timestamp": datetime.now().isoformat(),
            "total_files_scanned": total_files,
            "files_hashed": hashed_files,
            "errors": errors,
        },
        "file_hashes": file_hashes,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nHashing complete!")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files successfully hashed: {hashed_files}")
    print(f"  Errors: {errors}")
    print(f"  Results saved to: {output_file}")

    # Also create a verification summary
    verification_file = "hash_verification_summary.txt"
    with open(verification_file, "w", encoding="utf-8") as f:
        f.write(f"SHA-256 File Hash Verification Summary\n")
        f.write(f"======================================\n")
        f.write(f"Root Directory: {root_dir}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Files: {total_files}\n")
        f.write(f"Hashed Files: {hashed_files}\n")
        f.write(f"Errors: {errors}\n\n")

        # Write a few sample hashes
        f.write("Sample File Hashes (first 10):\n")
        f.write("=" * 50 + "\n")
        for i, (file_path, hash_info) in enumerate(list(file_hashes.items())[:10]):
            f.write(f"{file_path}\n")
            f.write(f"  SHA-256: {hash_info['sha256']}\n")
            f.write(f"  Size: {hash_info['size_bytes']} bytes\n")
            f.write(f"  Modified: {hash_info['modified']}\n\n")

    print(f"Verification summary saved to: {verification_file}")

    return results


def verify_hashes(hash_file="file_hashes.json"):
    """Verify that current file hashes match stored hashes."""
    if not os.path.exists(hash_file):
        print(f"Hash file not found: {hash_file}")
        return False

    with open(hash_file, "r", encoding="utf-8") as f:
        stored_data = json.load(f)

    root_dir = stored_data["metadata"]["root_directory"]
    stored_hashes = stored_data["file_hashes"]

    print(f"Verifying hashes against: {hash_file}")
    print(f"Root directory: {root_dir}")

    verified = 0
    mismatched = 0
    missing = 0

    for file_rel_path, stored_info in stored_hashes.items():
        file_path = os.path.join(root_dir, file_rel_path)

        if not os.path.exists(file_path):
            print(f"  ❌ Missing: {file_rel_path}")
            missing += 1
            continue

        current_hash = calculate_file_hash(file_path)

        if current_hash == stored_info["sha256"]:
            verified += 1
        else:
            print(f"  ❌ Mismatch: {file_rel_path}")
            print(f"     Stored: {stored_info['sha256']}")
            print(f"     Current: {current_hash}")
            mismatched += 1

    print(f"\nVerification complete!")
    print(f"  Verified: {verified}")
    print(f"  Mismatched: {mismatched}")
    print(f"  Missing: {missing}")

    return mismatched == 0 and missing == 0


if __name__ == "__main__":
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Hash all files in the current directory
    hash_all_files(current_dir)

    print("\nTo verify hashes later, run:")
    print("  python hash_all_files.py --verify")
    print("\nOr import and call verify_hashes() function.")
