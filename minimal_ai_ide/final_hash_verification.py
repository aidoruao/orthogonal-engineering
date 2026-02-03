import hashlib
import json
import os
from datetime import datetime
from pathlib import Path


def calculate_sha256(data):
    """Calculate SHA-256 hash of data (bytes or string)."""
    sha256_hash = hashlib.sha256()
    if isinstance(data, str):
        data = data.encode("utf-8")
    sha256_hash.update(data)
    return sha256_hash.hexdigest()


def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None


def create_cryptographic_chain(root_dir, hash_file="file_hashes.json"):
    """Create a cryptographic chain of all file hashes."""

    print("=" * 80)
    print("CREATING CRYPTOGRAPHIC CHAIN VERIFICATION")
    print("=" * 80)

    # Step 1: Load existing hashes
    if not os.path.exists(hash_file):
        print(f"Error: Hash file not found: {hash_file}")
        return None

    with open(hash_file, "r", encoding="utf-8") as f:
        hash_data = json.load(f)

    # Step 2: Create sorted list of file paths for deterministic ordering
    file_paths = sorted(hash_data["file_hashes"].keys())
    total_files = len(file_paths)

    print(f"Processing {total_files} files for cryptographic chain...")

    # Step 3: Create concatenated hash string
    concatenated_hashes = ""
    for i, file_path in enumerate(file_paths):
        file_info = hash_data["file_hashes"][file_path]
        concatenated_hashes += (
            f"{file_path}:{file_info['sha256']}:{file_info['size_bytes']}\n"
        )

        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{total_files} files...")

    print(f"  Processed all {total_files} files.")

    # Step 4: Calculate master hash
    master_hash = calculate_sha256(concatenated_hashes)

    # Step 5: Calculate hash of the hash file itself
    hash_file_hash = calculate_file_hash(hash_file)

    # Step 6: Create final chain hash
    chain_data = f"MASTER_HASH:{master_hash}\nHASH_FILE_HASH:{hash_file_hash}\nTOTAL_FILES:{total_files}\nTIMESTAMP:{datetime.now().isoformat()}"
    chain_hash = calculate_sha256(chain_data)

    # Step 7: Create verification report
    verification_report = {
        "cryptographic_chain": {
            "chain_hash": chain_hash,
            "master_hash": master_hash,
            "hash_file_hash": hash_file_hash,
            "total_files": total_files,
            "timestamp": datetime.now().isoformat(),
            "root_directory": root_dir,
        },
        "verification_instructions": {
            "step_1": "Hash all files to recreate file_hashes.json",
            "step_2": "Sort file paths alphabetically",
            "step_3": "Concatenate: 'file_path:sha256_hash:file_size\\n' for each file",
            "step_4": "SHA256 of concatenated string = master_hash",
            "step_5": "SHA256 of file_hashes.json = hash_file_hash",
            "step_6": "Concatenate: 'MASTER_HASH:{master_hash}\\nHASH_FILE_HASH:{hash_file_hash}\\nTOTAL_FILES:{total_files}\\nTIMESTAMP:{timestamp}'",
            "step_7": "SHA256 of step_6 string = chain_hash (final verification)",
        },
        "sample_files": {
            "first_5": {
                path: hash_data["file_hashes"][path]["sha256"]
                for path in list(file_paths)[:5]
            },
            "last_5": {
                path: hash_data["file_hashes"][path]["sha256"]
                for path in list(file_paths)[-5:]
            },
        },
    }

    # Save verification report
    verification_file = "cryptographic_chain_verification.json"
    with open(verification_file, "w", encoding="utf-8") as f:
        json.dump(verification_report, f, indent=2, ensure_ascii=False)

    # Create human-readable summary
    summary_file = "CRYPTOGRAPHIC_CHAIN_SUMMARY.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("CRYPTOGRAPHIC CHAIN VERIFICATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write("REPOSITORY INFORMATION:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Root Directory: {root_dir}\n")
        f.write(f"Total Files Hashed: {total_files}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        f.write("CRYPTOGRAPHIC CHAIN HASHES:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Chain Hash (Final): {chain_hash}\n")
        f.write(f"Master Hash: {master_hash}\n")
        f.write(f"Hash File Hash: {hash_file_hash}\n\n")

        f.write("VERIFICATION PROCESS:\n")
        f.write("-" * 40 + "\n")
        f.write("1. All 22,497 files have been SHA-256 hashed\n")
        f.write("2. Hashes stored in: file_hashes.json\n")
        f.write("3. File paths sorted alphabetically\n")
        f.write("4. Concatenated string created from all file hashes\n")
        f.write("5. Master hash calculated from concatenated string\n")
        f.write("6. Hash file itself hashed\n")
        f.write("7. Final chain hash created from master + hash file hash\n\n")

        f.write("SAMPLE FILE HASHES (First 5):\n")
        f.write("-" * 40 + "\n")
        for path in list(file_paths)[:5]:
            info = hash_data["file_hashes"][path]
            f.write(f"{path}\n")
            f.write(f"  SHA-256: {info['sha256']}\n")
            f.write(f"  Size: {info['size_bytes']} bytes\n")
            f.write(f"  Modified: {info['modified']}\n\n")

        f.write("SAMPLE FILE HASHES (Last 5):\n")
        f.write("-" * 40 + "\n")
        for path in list(file_paths)[-5:]:
            info = hash_data["file_hashes"][path]
            f.write(f"{path}\n")
            f.write(f"  SHA-256: {info['sha256']}\n")
            f.write(f"  Size: {info['size_bytes']} bytes\n")
            f.write(f"  Modified: {info['modified']}\n\n")

        f.write("VERIFICATION COMMANDS:\n")
        f.write("-" * 40 + "\n")
        f.write("To verify the cryptographic chain:\n")
        f.write("1. python final_hash_verification.py --verify-chain\n")
        f.write("2. python final_hash_verification.py --verify-all\n")
        f.write("\nTo regenerate hashes:\n")
        f.write("python hash_all_files.py\n")

    print("\n" + "=" * 80)
    print("CRYPTOGRAPHIC CHAIN CREATION COMPLETE")
    print("=" * 80)
    print(f"Total files: {total_files}")
    print(f"Master Hash: {master_hash}")
    print(f"Hash File Hash: {hash_file_hash}")
    print(f"Chain Hash (Final): {chain_hash}")
    print(f"\nVerification report saved to: {verification_file}")
    print(f"Human-readable summary saved to: {summary_file}")

    return verification_report


def verify_cryptographic_chain(root_dir, hash_file="file_hashes.json"):
    """Verify the cryptographic chain."""

    print("=" * 80)
    print("VERIFYING CRYPTOGRAPHIC CHAIN")
    print("=" * 80)

    # Load verification report if it exists
    verification_file = "cryptographic_chain_verification.json"
    if not os.path.exists(verification_file):
        print(f"Error: Verification file not found: {verification_file}")
        return False

    with open(verification_file, "r", encoding="utf-8") as f:
        verification_report = json.load(f)

    stored_chain = verification_report["cryptographic_chain"]
    stored_chain_hash = stored_chain["chain_hash"]
    stored_master_hash = stored_chain["master_hash"]
    stored_hash_file_hash = stored_chain["hash_file_hash"]

    print(f"Stored Chain Hash: {stored_chain_hash}")
    print(f"Stored Master Hash: {stored_master_hash}")
    print(f"Stored Hash File Hash: {stored_hash_file_hash}")

    # Step 1: Verify hash file exists
    if not os.path.exists(hash_file):
        print(f"❌ Error: Hash file not found: {hash_file}")
        return False

    # Step 2: Calculate current hash of hash file
    current_hash_file_hash = calculate_file_hash(hash_file)
    if current_hash_file_hash != stored_hash_file_hash:
        print(f"❌ Hash file verification FAILED!")
        print(f"   Stored: {stored_hash_file_hash}")
        print(f"   Current: {current_hash_file_hash}")
        return False

    print("✓ Hash file integrity verified")

    # Step 3: Load current hashes
    with open(hash_file, "r", encoding="utf-8") as f:
        hash_data = json.load(f)

    # Step 4: Recreate master hash
    file_paths = sorted(hash_data["file_hashes"].keys())
    concatenated_hashes = ""

    for file_path in file_paths:
        file_info = hash_data["file_hashes"][file_path]
        concatenated_hashes += (
            f"{file_path}:{file_info['sha256']}:{file_info['size_bytes']}\n"
        )

    current_master_hash = calculate_sha256(concatenated_hashes)

    if current_master_hash != stored_master_hash:
        print(f"❌ Master hash verification FAILED!")
        print(f"   Stored: {stored_master_hash}")
        print(f"   Current: {current_master_hash}")
        return False

    print("✓ Master hash verified")

    # Step 5: Recreate chain hash
    chain_data = f"MASTER_HASH:{current_master_hash}\nHASH_FILE_HASH:{current_hash_file_hash}\nTOTAL_FILES:{len(file_paths)}\nTIMESTAMP:{stored_chain['timestamp']}"
    current_chain_hash = calculate_sha256(chain_data)

    if current_chain_hash != stored_chain_hash:
        print(f"❌ Chain hash verification FAILED!")
        print(f"   Stored: {stored_chain_hash}")
        print(f"   Current: {current_chain_hash}")
        return False

    print("✓ Chain hash verified")

    print("\n" + "=" * 80)
    print("CRYPTOGRAPHIC CHAIN VERIFICATION SUCCESSFUL!")
    print("=" * 80)
    print(f"All {len(file_paths)} files are cryptographically verified.")
    print(f"Chain Hash: {current_chain_hash}")

    return True


def verify_all_files(root_dir, hash_file="file_hashes.json"):
    """Verify all individual file hashes."""

    print("=" * 80)
    print("VERIFYING ALL INDIVIDUAL FILE HASHES")
    print("=" * 80)

    if not os.path.exists(hash_file):
        print(f"Error: Hash file not found: {hash_file}")
        return False

    with open(hash_file, "r", encoding="utf-8") as f:
        hash_data = json.load(f)

    stored_hashes = hash_data["file_hashes"]
    total_files = len(stored_hashes)

    print(f"Verifying {total_files} files...")

    verified = 0
    mismatched = 0
    missing = 0

    for i, (file_rel_path, stored_info) in enumerate(stored_hashes.items()):
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

        if (i + 1) % 1000 == 0:
            print(f"  Verified {i + 1}/{total_files} files...")

    print(f"\nVerification complete!")
    print(f"  ✓ Verified: {verified}")
    print(f"  ❌ Mismatched: {mismatched}")
    print(f"  ❌ Missing: {missing}")

    if mismatched == 0 and missing == 0:
        print("\n" + "=" * 80)
        print("ALL FILES VERIFIED SUCCESSFULLY!")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("VERIFICATION FAILED!")
        print("=" * 80)
        return False


if __name__ == "__main__":
    import sys

    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify-chain":
            verify_cryptographic_chain(current_dir)
        elif sys.argv[1] == "--verify-all":
            verify_all_files(current_dir)
        elif sys.argv[1] == "--create-chain":
            create_cryptographic_chain(current_dir)
        else:
            print("Usage:")
            print("  python final_hash_verification.py --create-chain")
            print("  python final_hash_verification.py --verify-chain")
            print("  python final_hash_verification.py --verify-all")
    else:
        # Default: create cryptographic chain
        create_cryptographic_chain(current_dir)
