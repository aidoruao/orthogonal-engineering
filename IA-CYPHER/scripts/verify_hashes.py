"""
verify_hashes.py — IA-CYPHER-0002 Hash Verifier

Verifies that the SHA-256 hashes of prompt.txt and response.txt in a case directory
match the values stored in hashes.json at the time of capture.

Usage:
    python scripts/verify_hashes.py --case-dir cases/case_0001

Prints a verification result for each file and exits with:
    0 — all hashes verified
    1 — one or more hash mismatches or errors
"""

import argparse
import hashlib
import json
import os
import sys


# ---------------------------------------------------------------------------
# Hashing utility
# ---------------------------------------------------------------------------

def sha256_of_file(path: str) -> str:
    """Return the hex SHA-256 digest of a file's raw bytes."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Verification logic
# ---------------------------------------------------------------------------

def verify_case(case_dir: str) -> bool:
    """
    Verify the hashes for a single case directory.

    Parameters
    ----------
    case_dir : str
        Path to the case directory containing prompt.txt, response.txt, hashes.json.

    Returns
    -------
    bool
        True if all hashes verify, False otherwise.
    """
    case_id = os.path.basename(os.path.normpath(case_dir))
    hashes_path = os.path.join(case_dir, "hashes.json")
    prompt_path = os.path.join(case_dir, "prompt.txt")
    response_path = os.path.join(case_dir, "response.txt")

    print(f"\n[verify_hashes] Case: {case_id}")
    print(f"[verify_hashes] Directory: {case_dir}")

    # Check required files exist
    for path, label in [
        (hashes_path, "hashes.json"),
        (prompt_path, "prompt.txt"),
        (response_path, "response.txt"),
    ]:
        if not os.path.isfile(path):
            print(f"  [ERROR] Missing required file: {label} ({path})")
            return False

    # Load stored hashes
    with open(hashes_path, "r", encoding="utf-8") as f:
        stored = json.load(f)

    stored_prompt_hash = stored.get("prompt_sha256", "")
    stored_response_hash = stored.get("response_sha256", "")

    if not stored_prompt_hash or stored_prompt_hash.startswith("PLACEHOLDER"):
        print("  [SKIP] prompt_sha256 is a placeholder — case not yet populated.")
        return False

    if not stored_response_hash or stored_response_hash.startswith("PLACEHOLDER"):
        print("  [SKIP] response_sha256 is a placeholder — case not yet populated.")
        return False

    all_ok = True

    # Verify prompt.txt
    actual_prompt_hash = sha256_of_file(prompt_path)
    if actual_prompt_hash == stored_prompt_hash:
        print(f"  [OK]   prompt.txt   SHA-256: {actual_prompt_hash}")
    else:
        print(f"  [FAIL] prompt.txt   SHA-256 MISMATCH")
        print(f"         Stored:   {stored_prompt_hash}")
        print(f"         Computed: {actual_prompt_hash}")
        all_ok = False

    # Verify response.txt
    actual_response_hash = sha256_of_file(response_path)
    if actual_response_hash == stored_response_hash:
        print(f"  [OK]   response.txt SHA-256: {actual_response_hash}")
    else:
        print(f"  [FAIL] response.txt SHA-256 MISMATCH")
        print(f"         Stored:   {stored_response_hash}")
        print(f"         Computed: {actual_response_hash}")
        all_ok = False

    if all_ok:
        print(f"  [VERIFIED] Case {case_id} integrity confirmed.")
    else:
        print(f"  [INTEGRITY FAILURE] Case {case_id} has hash mismatches — do not trust its contents.")

    return all_ok


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="IA-CYPHER-0002: Verify hashes for one or more cases."
    )
    parser.add_argument(
        "--case-dir",
        required=True,
        help="Path to the case directory to verify (e.g. cases/case_0001)",
    )
    args = parser.parse_args()

    ok = verify_case(args.case_dir)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
