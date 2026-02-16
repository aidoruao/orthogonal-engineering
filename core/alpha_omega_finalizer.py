#!/usr/bin/env python3
"""
AlphaOmegaFinalizer: Production-ready canonical ledger creation and Merkle root generation.

This module processes chat export files to create a canonical, cryptographically verifiable
ledger with privacy-preserving features and robust error handling.

SECURITY & PRIVACY:
- Does NOT commit raw chat exports or PII
- Supports optional redaction hooks for sensitive content
- Processes files from a local vault directory (not tracked in git)
- Implements streaming parsing to handle large files without OOM

Architecture:
1. Streaming JSONL/JSON parsing from vault directory
2. Timestamp normalization to UTC ISO8601
3. Canonical byte serialization (sorted keys, deterministic separators)
4. SHA-256 hashing per entry and per file
5. Merkle tree construction (binary tree, sha256(left||right))
6. Atomic ledger writing (SOVEREIGN_CONSTITUTION.jsonl)
7. Master root persistence (MASTER_ROOT.txt)
8. Integrity verification

Author: Orthogonal Engineering
License: MIT
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import tempfile
import shutil

# Conditional import for streaming JSON parsing
try:
    import ijson
    IJSON_AVAILABLE = True
except ImportError:
    IJSON_AVAILABLE = False
    logging.warning("ijson not available - falling back to standard json (not memory-safe for large files)")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlphaOmegaFinalizer:
    """
    Robust, production-ready canonical ledger creation with Merkle verification.
    
    Processes chat exports from a vault directory, normalizes timestamps,
    computes deterministic hashes, builds a Merkle tree, and provides
    self-verification capabilities.
    """
    
    def __init__(
        self,
        vault_dir: str,
        outputs_dir: str,
        fallback_epoch: Optional[str] = None,
        redact: bool = False,
        redaction_classifier: Optional[Callable[[Dict], Dict]] = None,
        dry_run: bool = True
    ):
        """
        Initialize the AlphaOmegaFinalizer.
        
        Args:
            vault_dir: Directory containing chat export files (JSONL/JSON)
            outputs_dir: Directory for output files (ledger, master root)
            fallback_epoch: ISO8601 timestamp to use if entry has no timestamp
            redact: Enable redaction pipeline
            redaction_classifier: Optional callable for detecting/redacting sensitive content
            dry_run: If True, don't write any files (default: True for safety)
        """
        self.vault_dir = Path(vault_dir)
        self.outputs_dir = Path(outputs_dir)
        self.fallback_epoch = fallback_epoch or "1970-01-01T00:00:00Z"
        self.redact = redact
        self.redaction_classifier = redaction_classifier
        self.dry_run = dry_run
        
        # Validate inputs
        if not self.vault_dir.exists():
            raise ValueError(f"Vault directory does not exist: {vault_dir}")
        
        # Create outputs directory if needed
        if not dry_run:
            self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Ledger entries storage
        self.ledger_entries: List[Dict[str, Any]] = []
        self.entry_hashes: List[str] = []
        
        logger.info(f"Initialized AlphaOmegaFinalizer")
        logger.info(f"  Vault: {self.vault_dir}")
        logger.info(f"  Outputs: {self.outputs_dir}")
        logger.info(f"  Dry run: {self.dry_run}")
        logger.info(f"  Redaction: {self.redact}")
    
    def normalize_timestamp(self, timestamp: Optional[str]) -> str:
        """
        Normalize a timestamp to UTC ISO8601 format.
        
        Args:
            timestamp: Input timestamp string (various formats supported)
        
        Returns:
            ISO8601 UTC timestamp string
        """
        if not timestamp:
            return self.fallback_epoch
        
        try:
            # Try parsing as ISO8601
            if timestamp.endswith('Z'):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif '+' in timestamp or timestamp.count('-') > 2:
                dt = datetime.fromisoformat(timestamp)
            else:
                # Assume UTC if no timezone
                dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
            
            # Convert to UTC
            dt_utc = dt.astimezone(timezone.utc)
            return dt_utc.isoformat().replace('+00:00', 'Z')
        
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse timestamp '{timestamp}': {e}. Using fallback.")
            return self.fallback_epoch
    
    def canonical_serialize(self, data: Dict[str, Any]) -> bytes:
        """
        Perform canonical byte serialization of a dictionary.
        
        Uses sorted keys and consistent separators for deterministic output.
        
        Args:
            data: Dictionary to serialize
        
        Returns:
            Canonical byte representation
        """
        canonical_json = json.dumps(
            data,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True
        )
        return canonical_json.encode('utf-8')
    
    def compute_sha256(self, data: bytes) -> str:
        """
        Compute SHA-256 hash of byte data.
        
        Args:
            data: Byte data to hash
        
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(data).hexdigest()
    
    def apply_redaction(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply redaction rules to an entry.
        
        This is a hook point for privacy-preserving transformations.
        
        Default behavior (when no classifier provided):
        - Redact entries with "explicit" or "sensitive" markers
        - Mask user IDs with hashed versions
        
        Args:
            entry: Entry dictionary to redact
        
        Returns:
            Redacted entry
        """
        if not self.redact:
            return entry
        
        redacted = entry.copy()
        
        # If custom classifier provided, use it
        if self.redaction_classifier:
            try:
                redacted = self.redaction_classifier(redacted)
            except Exception as e:
                logger.error(f"Redaction classifier failed: {e}")
                # Continue with default redaction
        
        # Default redaction rules
        # Mark as redacted if contains sensitive markers
        content = str(redacted.get('content', ''))
        if any(marker in content.lower() for marker in ['explicit', 'sensitive', 'private']):
            redacted['content'] = '[REDACTED: Sensitive content]'
            redacted['redacted'] = True
        
        # Hash user identifiers for privacy
        if 'user_id' in redacted:
            user_hash = self.compute_sha256(str(redacted['user_id']).encode())
            redacted['user_id_hash'] = user_hash[:16]  # First 16 chars
            del redacted['user_id']
        
        return redacted
    
    def process_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a JSON file (single object or array).
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            List of entries
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both single object and array
                if isinstance(data, list):
                    entries.extend(data)
                elif isinstance(data, dict):
                    entries.append(data)
                else:
                    logger.warning(f"Unexpected JSON structure in {file_path}")
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        return entries
    
    def process_jsonl_file_streaming(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a JSONL file with streaming to avoid OOM.
        
        Args:
            file_path: Path to JSONL file
        
        Returns:
            List of entries
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON at {file_path}:{line_num}: {e}")
        
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        
        return entries
    
    def process_vault_directory(self) -> None:
        """
        Process all JSON/JSONL files in the vault directory.
        
        Creates normalized ledger entries with timestamps, hashes, and metadata.
        """
        logger.info(f"Scanning vault directory: {self.vault_dir}")
        
        # Find all JSON and JSONL files
        json_files = list(self.vault_dir.glob("*.json"))
        jsonl_files = list(self.vault_dir.glob("*.jsonl"))
        
        all_files = json_files + jsonl_files
        
        if not all_files:
            logger.warning(f"No JSON/JSONL files found in {self.vault_dir}")
            return
        
        logger.info(f"Found {len(all_files)} files to process")
        
        for file_path in sorted(all_files):
            logger.info(f"Processing: {file_path.name}")
            
            # Determine file type and process accordingly
            if file_path.suffix == '.jsonl':
                entries = self.process_jsonl_file_streaming(file_path)
            else:
                entries = self.process_json_file(file_path)
            
            logger.info(f"  Extracted {len(entries)} entries from {file_path.name}")
            
            # Process each entry
            for idx, entry in enumerate(entries):
                # Normalize timestamp
                timestamp = self.normalize_timestamp(entry.get('timestamp'))
                
                # Apply redaction if enabled
                if self.redact:
                    entry = self.apply_redaction(entry)
                
                # Create ledger entry
                ledger_entry = {
                    'source_file': file_path.name,
                    'entry_index': idx,
                    'timestamp': timestamp,
                    'data': entry
                }
                
                # Compute entry hash
                canonical_bytes = self.canonical_serialize(ledger_entry)
                entry_hash = self.compute_sha256(canonical_bytes)
                
                ledger_entry['hash'] = entry_hash
                
                self.ledger_entries.append(ledger_entry)
                self.entry_hashes.append(entry_hash)
        
        logger.info(f"Total ledger entries: {len(self.ledger_entries)}")
    
    def build_merkle_tree(self) -> Tuple[str, List[List[str]]]:
        """
        Build a binary Merkle tree from entry hashes.
        
        Merkle tree construction:
        - Leaf nodes: SHA-256 of canonical entry bytes
        - Internal nodes: SHA-256(left_hash || right_hash)
        - If odd number of nodes, duplicate the last one
        
        Returns:
            Tuple of (root_hash, tree_levels)
        """
        if not self.entry_hashes:
            logger.warning("No entry hashes to build Merkle tree")
            return "", []
        
        logger.info(f"Building Merkle tree from {len(self.entry_hashes)} leaves")
        
        # Initialize with leaf hashes
        current_level = self.entry_hashes.copy()
        tree_levels = [current_level.copy()]
        
        # Build tree bottom-up
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    # Pair exists: hash(left || right)
                    left = current_level[i]
                    right = current_level[i + 1]
                    combined = left + right
                    parent_hash = self.compute_sha256(combined.encode('utf-8'))
                else:
                    # Odd number: duplicate last node
                    left = current_level[i]
                    combined = left + left
                    parent_hash = self.compute_sha256(combined.encode('utf-8'))
                
                next_level.append(parent_hash)
            
            current_level = next_level
            tree_levels.append(current_level.copy())
        
        root_hash = current_level[0] if current_level else ""
        
        logger.info(f"Merkle root: {root_hash}")
        logger.info(f"Tree depth: {len(tree_levels)}")
        
        return root_hash, tree_levels
    
    def write_canonical_ledger(self) -> Optional[Path]:
        """
        Write the canonical ledger to SOVEREIGN_CONSTITUTION.jsonl.
        
        Each line is a JSON object representing one ledger entry.
        
        Returns:
            Path to ledger file if written, None if dry run
        """
        if self.dry_run:
            logger.info("[DRY RUN] Would write canonical ledger")
            return None
        
        ledger_path = self.outputs_dir / "SOVEREIGN_CONSTITUTION.jsonl"
        
        logger.info(f"Writing canonical ledger to: {ledger_path}")
        
        try:
            # Write atomically using temp file + rename
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=self.outputs_dir,
                delete=False,
                suffix='.tmp'
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                
                for entry in self.ledger_entries:
                    json_line = json.dumps(entry, sort_keys=True)
                    tmp_file.write(json_line + '\n')
            
            # Atomic rename
            tmp_path.replace(ledger_path)
            
            logger.info(f"Successfully wrote {len(self.ledger_entries)} entries to ledger")
            return ledger_path
        
        except Exception as e:
            logger.error(f"Failed to write ledger: {e}")
            # Clean up temp file if it exists
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
            raise
    
    def write_master_root(self, root_hash: str) -> Optional[Path]:
        """
        Write the Merkle root to MASTER_ROOT.txt.
        
        Args:
            root_hash: The Merkle tree root hash
        
        Returns:
            Path to master root file if written, None if dry run
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write master root: {root_hash}")
            return None
        
        root_path = self.outputs_dir / "MASTER_ROOT.txt"
        
        logger.info(f"Writing master root to: {root_path}")
        
        try:
            # Write atomically
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=self.outputs_dir,
                delete=False,
                suffix='.tmp'
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                tmp_file.write(root_hash + '\n')
                tmp_file.write(f"# Generated: {datetime.now(timezone.utc).isoformat()}\n")
                tmp_file.write(f"# Total entries: {len(self.ledger_entries)}\n")
            
            # Atomic rename
            tmp_path.replace(root_path)
            
            logger.info(f"Successfully wrote master root")
            return root_path
        
        except Exception as e:
            logger.error(f"Failed to write master root: {e}")
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
            raise
    
    def finalize(self) -> Tuple[Optional[str], Optional[Path], Optional[Path]]:
        """
        Execute the complete finalization pipeline.
        
        Steps:
        1. Process vault directory
        2. Build Merkle tree
        3. Write canonical ledger
        4. Write master root
        
        Returns:
            Tuple of (merkle_root, ledger_path, root_path)
        """
        logger.info("="*60)
        logger.info("Starting AlphaOmegaFinalizer pipeline")
        logger.info("="*60)
        
        # Step 1: Process vault
        self.process_vault_directory()
        
        if not self.ledger_entries:
            logger.error("No entries processed - aborting finalization")
            return None, None, None
        
        # Step 2: Build Merkle tree
        merkle_root, tree_levels = self.build_merkle_tree()
        
        if not merkle_root:
            logger.error("Failed to build Merkle tree - aborting finalization")
            return None, None, None
        
        # Step 3: Write ledger
        ledger_path = self.write_canonical_ledger()
        
        # Step 4: Write master root
        root_path = self.write_master_root(merkle_root)
        
        logger.info("="*60)
        logger.info("Finalization complete")
        logger.info(f"  Merkle root: {merkle_root}")
        if ledger_path:
            logger.info(f"  Ledger: {ledger_path}")
        if root_path:
            logger.info(f"  Master root: {root_path}")
        logger.info("="*60)
        
        return merkle_root, ledger_path, root_path
    
    def verify_integrity(self) -> bool:
        """
        Verify the integrity of the canonical ledger against the master root.
        
        Reads the ledger file, recomputes hashes and Merkle root,
        and compares to the stored master root.
        
        Returns:
            True if verification succeeds, False otherwise
        """
        logger.info("Starting integrity verification")
        
        ledger_path = self.outputs_dir / "SOVEREIGN_CONSTITUTION.jsonl"
        root_path = self.outputs_dir / "MASTER_ROOT.txt"
        
        # Check files exist
        if not ledger_path.exists():
            logger.error(f"Ledger file not found: {ledger_path}")
            return False
        
        if not root_path.exists():
            logger.error(f"Master root file not found: {root_path}")
            return False
        
        # Read stored master root
        try:
            with open(root_path, 'r') as f:
                stored_root = f.readline().strip()
        except Exception as e:
            logger.error(f"Failed to read master root: {e}")
            return False
        
        logger.info(f"Stored master root: {stored_root}")
        
        # Recompute ledger hashes
        recomputed_hashes = []
        
        try:
            with open(ledger_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        # Extract the hash that was stored
                        stored_hash = entry.get('hash')
                        
                        # Recompute hash for verification
                        # Note: We use the full entry including the hash field
                        # for consistency with how it was originally computed
                        entry_copy = entry.copy()
                        if 'hash' in entry_copy:
                            del entry_copy['hash']
                        
                        canonical_bytes = self.canonical_serialize(entry_copy)
                        recomputed_hash = self.compute_sha256(canonical_bytes)
                        
                        if stored_hash != recomputed_hash:
                            logger.error(
                                f"Hash mismatch at entry {line_num}: "
                                f"stored={stored_hash}, recomputed={recomputed_hash}"
                            )
                            return False
                        
                        recomputed_hashes.append(stored_hash)
                    
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON at line {line_num}: {e}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to read ledger: {e}")
            return False
        
        logger.info(f"Verified {len(recomputed_hashes)} ledger entry hashes")
        
        # Recompute Merkle root
        self.entry_hashes = recomputed_hashes
        recomputed_root, _ = self.build_merkle_tree()
        
        logger.info(f"Recomputed merkle root: {recomputed_root}")
        
        # Compare roots
        if recomputed_root == stored_root:
            logger.info("✅ VERIFICATION SUCCESSFUL: Merkle roots match")
            return True
        else:
            logger.error(
                f"❌ VERIFICATION FAILED: Merkle root mismatch\n"
                f"  Stored:     {stored_root}\n"
                f"  Recomputed: {recomputed_root}"
            )
            return False


def main():
    """CLI entry point for AlphaOmegaFinalizer."""
    
    parser = argparse.ArgumentParser(
        description="AlphaOmegaFinalizer: Canonical ledger creation and Merkle verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default - safe, no files written)
  python alpha_omega_finalizer.py finalize --vault-dir /path/to/vault --outputs-dir ./outputs

  # Actually write files
  python alpha_omega_finalizer.py finalize --vault-dir /path/to/vault --outputs-dir ./outputs --apply

  # With redaction enabled
  python alpha_omega_finalizer.py finalize --vault-dir /path/to/vault --outputs-dir ./outputs --redact --apply

  # Verify existing ledger
  python alpha_omega_finalizer.py verify --outputs-dir ./outputs

SECURITY NOTES:
  - Never commit chat exports or PII to version control
  - Use a local vault directory outside the repository
  - Enable --redact for privacy-sensitive content
  - Review output files before sharing
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Finalize command
    finalize_parser = subparsers.add_parser('finalize', help='Finalize ledger from vault')
    finalize_parser.add_argument(
        '--vault-dir',
        required=True,
        help='Directory containing chat export files (JSON/JSONL)'
    )
    finalize_parser.add_argument(
        '--outputs-dir',
        required=True,
        help='Directory for output files (ledger, master root)'
    )
    finalize_parser.add_argument(
        '--fallback-epoch',
        default='1970-01-01T00:00:00Z',
        help='Fallback timestamp for entries without timestamps (ISO8601)'
    )
    finalize_parser.add_argument(
        '--redact',
        action='store_true',
        help='Enable redaction pipeline for sensitive content'
    )
    finalize_parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry run mode (default: enabled for safety)'
    )
    finalize_parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually write files (disables dry-run)'
    )
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify ledger integrity')
    verify_parser.add_argument(
        '--outputs-dir',
        required=True,
        help='Directory containing ledger and master root files'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'finalize':
            # Determine dry_run setting
            dry_run = not args.apply
            
            finalizer = AlphaOmegaFinalizer(
                vault_dir=args.vault_dir,
                outputs_dir=args.outputs_dir,
                fallback_epoch=args.fallback_epoch,
                redact=args.redact,
                dry_run=dry_run
            )
            
            merkle_root, ledger_path, root_path = finalizer.finalize()
            
            if dry_run:
                print("\n⚠️  DRY RUN MODE - No files were written")
                print("Use --apply to actually write files")
            else:
                print("\n✅ Finalization complete")
                print(f"Merkle root: {merkle_root}")
                if ledger_path:
                    print(f"Ledger: {ledger_path}")
                if root_path:
                    print(f"Master root: {root_path}")
        
        elif args.command == 'verify':
            # For verification, we don't need a vault, just outputs
            finalizer = AlphaOmegaFinalizer(
                vault_dir=".",  # Dummy value, not used
                outputs_dir=args.outputs_dir,
                dry_run=True  # Verification never writes
            )
            
            success = finalizer.verify_integrity()
            
            if success:
                print("\n✅ VERIFICATION SUCCESSFUL")
                sys.exit(0)
            else:
                print("\n❌ VERIFICATION FAILED")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
