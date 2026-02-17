#!/usr/bin/env python3
"""
Repository Manifest Generator
Produces deterministic manifests for city-scale verification systems.

This module generates comprehensive manifests containing:
- File-level metadata: path, size, mtime, SHA256 hash
- Folder-level aggregates: file_count, total_bytes, artifact_flags, folder_hash
- Deterministic ordering: lexicographically sorted by path

Manifests are persisted at documentation/sha256_manifests/manifest-<commit>.json
"""

import hashlib
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class RepositoryManifestGenerator:
    """Generates deterministic manifests for repository verification."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize the manifest generator.
        
        Args:
            repo_path: Path to the git repository root
        """
        self.repo_path = Path(repo_path).resolve()
        self.manifest_dir = self.repo_path / "documentation" / "sha256_manifests"
        
    def _get_git_commit(self) -> str:
        """Get current HEAD commit SHA.
        
        Returns:
            The current commit SHA (short form)
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get git commit: {e}")
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file contents.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal SHA256 hash string
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for memory efficiency
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (OSError, IOError) as e:
            # Return empty hash for unreadable files
            return ""
    
    def _should_exclude(self, path: Path) -> bool:
        """Determine if a path should be excluded from manifest.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be excluded
        """
        # Exclude .git directory
        if '.git' in path.parts:
            return True
        
        # Exclude node_modules
        if 'node_modules' in path.parts:
            return True
        
        # Exclude __pycache__
        if '__pycache__' in path.parts:
            return True
        
        # Exclude .pyc files
        if path.suffix == '.pyc':
            return True
        
        return False
    
    def _get_artifact_flags(self, folder_path: Path) -> List[str]:
        """Determine artifact flags for a folder.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            List of artifact type flags
        """
        flags = []
        folder_name = folder_path.name.lower()
        
        # Check for various artifact types
        if 'manifest' in folder_name or 'sha256' in folder_name:
            flags.append('manifest')
        if 'audit' in folder_name:
            flags.append('audit')
        if 'backup' in folder_name:
            flags.append('backup')
        if 'merkle' in folder_name:
            flags.append('merkle')
        if 'test' in folder_name:
            flags.append('test')
        if 'doc' in folder_name or folder_name == 'documentation':
            flags.append('documentation')
        if 'automation' in folder_name:
            flags.append('automation')
        
        return flags
    
    def generate_manifest(self) -> Dict[str, Any]:
        """Generate complete repository manifest.
        
        Returns:
            Dictionary containing the manifest data
        """
        commit_sha = self._get_git_commit()
        
        # Initialize manifest structure
        manifest = {
            "manifest_version": "1.0.0",
            "commit": commit_sha,
            "generated_at": datetime.now().astimezone().isoformat(),
            "repository_root": str(self.repo_path),
            "files": [],
            "folders": {}
        }
        
        # Collect file metadata
        file_entries = []
        folder_stats = defaultdict(lambda: {
            'files': [],
            'file_count': 0,
            'total_bytes': 0,
            'artifact_flags': []
        })
        
        # Walk the repository
        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Skip excluded directories
            if self._should_exclude(root_path):
                dirs.clear()  # Don't descend into excluded directories
                continue
            
            # Filter out excluded subdirectories
            dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d)]
            
            # Process files in this directory
            for filename in files:
                file_path = root_path / filename
                
                # Skip excluded files
                if self._should_exclude(file_path):
                    continue
                
                # Get file stats
                try:
                    stat = file_path.stat()
                    rel_path = file_path.relative_to(self.repo_path)
                    
                    # Compute file hash
                    file_hash = self._compute_file_hash(file_path)
                    
                    # Create file entry
                    file_entry = {
                        "path": str(rel_path),
                        "size": stat.st_size,
                        "mtime": int(stat.st_mtime),
                        "sha256": file_hash
                    }
                    
                    file_entries.append(file_entry)
                    
                    # Update folder stats
                    folder_key = str(root_path.relative_to(self.repo_path)) if root_path != self.repo_path else "."
                    folder_stats[folder_key]['files'].append(file_hash)
                    folder_stats[folder_key]['file_count'] += 1
                    folder_stats[folder_key]['total_bytes'] += stat.st_size
                    
                except (OSError, IOError) as e:
                    # Skip files we can't read
                    continue
        
        # Sort files lexicographically by path for determinism
        file_entries.sort(key=lambda x: x['path'])
        manifest['files'] = file_entries
        
        # Compute folder aggregates
        for folder_path, stats in sorted(folder_stats.items()):
            # Compute folder hash from sorted file hashes
            sorted_hashes = sorted(stats['files'])
            folder_hash_input = ''.join(sorted_hashes).encode('utf-8')
            folder_hash = hashlib.sha256(folder_hash_input).hexdigest()
            
            # Get artifact flags
            full_folder_path = self.repo_path / folder_path if folder_path != "." else self.repo_path
            artifact_flags = self._get_artifact_flags(full_folder_path)
            
            manifest['folders'][folder_path] = {
                'file_count': stats['file_count'],
                'total_bytes': stats['total_bytes'],
                'artifact_flags': artifact_flags,
                'folder_hash': folder_hash
            }
        
        # Add summary statistics
        manifest['summary'] = {
            'total_files': len(file_entries),
            'total_folders': len(folder_stats),
            'total_bytes': sum(f['size'] for f in file_entries),
            'manifest_hash': self._compute_manifest_hash(manifest)
        }
        
        return manifest
    
    def _compute_manifest_hash(self, manifest: Dict[str, Any]) -> str:
        """Compute hash of the manifest itself.
        
        Args:
            manifest: The manifest dictionary (without the hash)
            
        Returns:
            SHA256 hash of the manifest content
        """
        # Create a copy without the summary section to avoid circular dependency
        manifest_copy = manifest.copy()
        if 'summary' in manifest_copy:
            summary = manifest_copy['summary'].copy()
            if 'manifest_hash' in summary:
                del summary['manifest_hash']
            manifest_copy['summary'] = summary
        
        # Compute hash of JSON representation
        json_str = json.dumps(manifest_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def save_manifest(self, manifest: Dict[str, Any], commit: Optional[str] = None) -> Path:
        """Save manifest to disk.
        
        Args:
            manifest: The manifest dictionary
            commit: Optional commit SHA (defaults to manifest['commit'])
            
        Returns:
            Path to the saved manifest file
        """
        # Ensure manifest directory exists
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine output filename
        if commit is None:
            commit = manifest.get('commit', 'unknown')
        
        output_path = self.manifest_dir / f"manifest-{commit}.json"
        
        # Write manifest with deterministic formatting
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        
        return output_path
    
    def load_manifest(self, commit: str) -> Optional[Dict[str, Any]]:
        """Load a manifest for a specific commit.
        
        Args:
            commit: The commit SHA
            
        Returns:
            The manifest dictionary, or None if not found
        """
        manifest_path = self.manifest_dir / f"manifest-{commit}.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except (OSError, IOError, json.JSONDecodeError) as e:
            return None
    
    def get_or_create_manifest(self, commit: Optional[str] = None) -> Dict[str, Any]:
        """Get existing manifest or create new one.
        
        Args:
            commit: Optional commit SHA (defaults to HEAD)
            
        Returns:
            The manifest dictionary
        """
        if commit is None:
            commit = self._get_git_commit()
        
        # Try to load existing manifest
        manifest = self.load_manifest(commit)
        
        if manifest is not None:
            return manifest
        
        # Generate and save new manifest
        manifest = self.generate_manifest()
        self.save_manifest(manifest, commit)
        
        return manifest


def main():
    """CLI entry point for manifest generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate deterministic repository manifest"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)"
    )
    parser.add_argument(
        "--output",
        help="Output path (default: documentation/sha256_manifests/manifest-<commit>.json)"
    )
    parser.add_argument(
        "--commit",
        help="Commit SHA (default: current HEAD)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON to stdout only (don't save to file)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if manifest exists"
    )
    
    args = parser.parse_args()
    
    try:
        generator = RepositoryManifestGenerator(args.repo)
        
        # Determine commit
        commit = args.commit if args.commit else generator._get_git_commit()
        
        # Check if manifest exists and we're not forcing
        if not args.force:
            existing_manifest = generator.load_manifest(commit)
            if existing_manifest is not None:
                if args.json_only:
                    print(json.dumps(existing_manifest, indent=2))
                    return
                else:
                    print(f"Manifest already exists for commit {commit}")
                    manifest_path = generator.manifest_dir / f"manifest-{commit}.json"
                    print(f"Path: {manifest_path}")
                    return
        
        # Generate manifest
        print(f"Generating manifest for commit {commit}...", file=sys.stderr)
        manifest = generator.generate_manifest()
        
        if args.json_only:
            # Output to stdout
            print(json.dumps(manifest, indent=2))
        else:
            # Save to file
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(manifest, f, indent=2, sort_keys=True)
                print(f"Manifest saved to: {output_path}", file=sys.stderr)
            else:
                output_path = generator.save_manifest(manifest, commit)
                print(f"Manifest saved to: {output_path}", file=sys.stderr)
            
            # Print summary
            summary = manifest['summary']
            print(f"\nSummary:", file=sys.stderr)
            print(f"  Files: {summary['total_files']}", file=sys.stderr)
            print(f"  Folders: {summary['total_folders']}", file=sys.stderr)
            print(f"  Total size: {summary['total_bytes']:,} bytes", file=sys.stderr)
            print(f"  Manifest hash: {summary['manifest_hash'][:16]}...", file=sys.stderr)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
