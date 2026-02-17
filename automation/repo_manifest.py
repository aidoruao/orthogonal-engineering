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
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict


class RepositoryManifestGenerator:
    """Generates deterministic manifests for repository verification."""
    
    # Supported file extensions for dependency extraction
    DEPENDENCY_EXTRACTABLE_EXTENSIONS = [
        '.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.h', '.hpp', 
        '.cs', '.rb', '.php', '.tsx', '.jsx'
    ]
    
    def __init__(self, repo_path: str = ".", repo_name: Optional[str] = None):
        """Initialize the manifest generator.
        
        Args:
            repo_path: Path to the git repository root
            repo_name: Optional repository name (for multi-repo manifests)
        """
        self.repo_path = Path(repo_path).resolve()
        self.repo_name = repo_name or self.repo_path.name
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
        except OSError as e:
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
    
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract import/include dependencies from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of dependency references (module names, file includes, etc.)
        """
        dependencies = []
        
        try:
            # Only process text files with known extensions
            if file_path.suffix not in self.DEPENDENCY_EXTRACTABLE_EXTENSIONS:
                return dependencies
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Python imports
            if file_path.suffix == '.py':
                # import module, from module import ...
                python_imports = re.findall(r'^\s*(?:from\s+([a-zA-Z0-9_.]+)|import\s+([a-zA-Z0-9_., ]+))', content, re.MULTILINE)
                for match in python_imports:
                    for group in match:
                        if group:
                            # Split comma-separated imports
                            for dep in group.split(','):
                                dep = dep.strip().split()[0]  # Take first word (handle "as" aliases)
                                if dep and not dep.startswith('.'):
                                    dependencies.append(dep)
            
            # JavaScript/TypeScript imports
            elif file_path.suffix in ['.js', '.ts', '.tsx', '.jsx']:
                # import ... from "module", require("module")
                js_imports = re.findall(r'(?:import\s+.*?\s+from\s+["\']([^"\']+)["\']|require\(["\']([^"\']+)["\']\))', content)
                for match in js_imports:
                    for group in match:
                        if group and not group.startswith('.'):
                            dependencies.append(group)
            
            # Go imports
            elif file_path.suffix == '.go':
                # import "package" or import ( "package1" "package2" )
                go_imports = re.findall(r'import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)")', content)
                for match in go_imports:
                    for group in match:
                        if group:
                            for dep in re.findall(r'"([^"]+)"', group):
                                dependencies.append(dep)
            
            # C/C++ includes
            elif file_path.suffix in ['.c', '.cpp', '.h', '.hpp']:
                # #include <header> or #include "header"
                c_includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
                dependencies.extend(c_includes)
            
            # Java imports
            elif file_path.suffix == '.java':
                # import package.Class
                java_imports = re.findall(r'import\s+([a-zA-Z0-9_.]+);', content)
                dependencies.extend(java_imports)
            
            # C# using
            elif file_path.suffix == '.cs':
                # using Namespace
                cs_usings = re.findall(r'using\s+([a-zA-Z0-9_.]+);', content)
                dependencies.extend(cs_usings)
            
        except (OSError, UnicodeDecodeError):
            # Return empty list for files we can't read
            pass
        
        # Remove duplicates and sort for determinism
        return sorted(list(set(dependencies)))
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of lines in the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (OSError, UnicodeDecodeError):
            return 0
    
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
            "manifest_version": "2.0.0",  # Updated version for multi-repo support
            "commit": commit_sha,
            "generated_at": datetime.now().astimezone().isoformat(),
            "repository_root": str(self.repo_path),
            "repository_name": self.repo_name,
            "files": [],
            "folders": {}
        }
        
        # Collect file metadata
        file_entries = []
        folder_stats = defaultdict(lambda: {
            'files': [],
            'file_count': 0,
            'total_bytes': 0,
            'artifact_flags': [],
            'dependency_hashes': []  # Track dependency hashes for folder-level aggregation
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
                    
                    # Extract dependencies and count lines
                    dependencies = self._extract_dependencies(file_path)
                    line_count = self._count_lines(file_path)
                    
                    # Compute dependency hash
                    dep_hash = ""
                    if dependencies:
                        dep_str = ''.join(sorted(dependencies))
                        dep_hash = hashlib.sha256(dep_str.encode('utf-8')).hexdigest()
                    
                    # Create file entry
                    file_entry = {
                        "path": str(rel_path),
                        "size": stat.st_size,
                        "mtime": int(stat.st_mtime),
                        "sha256": file_hash,
                        "line_count": line_count,
                        "dependencies": dependencies,
                        "dependency_hash": dep_hash
                    }
                    
                    file_entries.append(file_entry)
                    
                    # Update folder stats
                    folder_key = str(root_path.relative_to(self.repo_path)) if root_path != self.repo_path else "."
                    folder_stats[folder_key]['files'].append(file_hash)
                    folder_stats[folder_key]['file_count'] += 1
                    folder_stats[folder_key]['total_bytes'] += stat.st_size
                    if dep_hash:
                        folder_stats[folder_key]['dependency_hashes'].append(dep_hash)
                    
                except OSError as e:
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
            
            # Compute dependency hash from sorted dependency hashes
            dependency_hash = ""
            if stats['dependency_hashes']:
                sorted_dep_hashes = sorted(stats['dependency_hashes'])
                dep_hash_input = ''.join(sorted_dep_hashes).encode('utf-8')
                dependency_hash = hashlib.sha256(dep_hash_input).hexdigest()
            
            # Get artifact flags
            full_folder_path = self.repo_path / folder_path if folder_path != "." else self.repo_path
            artifact_flags = self._get_artifact_flags(full_folder_path)
            
            manifest['folders'][folder_path] = {
                'file_count': stats['file_count'],
                'total_bytes': stats['total_bytes'],
                'artifact_flags': artifact_flags,
                'folder_hash': folder_hash,
                'dependency_hash': dependency_hash
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
        except (OSError, json.JSONDecodeError) as e:
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


def generate_multi_repo_manifest(repo_list: List[Dict[str, str]], output_path: Optional[Path] = None) -> Dict[str, Any]:
    """Generate a multi-repository manifest.
    
    Args:
        repo_list: List of dictionaries with 'name' and 'path' keys
        output_path: Optional path to save the manifest
        
    Returns:
        Dictionary containing the multi-repo manifest
    """
    multi_manifest = {
        "manifest_version": "2.0.0",
        "type": "multi-repo",
        "generated_at": datetime.now().astimezone().isoformat(),
        "repositories": {},
        "global_summary": {
            "total_repos": len(repo_list),
            "total_files": 0,
            "total_folders": 0,
            "total_bytes": 0,
            "total_dependencies": 0
        }
    }
    
    for repo_info in repo_list:
        repo_name = repo_info['name']
        repo_path = repo_info['path']
        
        print(f"Generating manifest for {repo_name}...", file=sys.stderr)
        generator = RepositoryManifestGenerator(repo_path, repo_name=repo_name)
        manifest = generator.generate_manifest()
        
        # Store repo manifest
        multi_manifest['repositories'][repo_name] = manifest
        
        # Update global summary
        if 'summary' in manifest:
            multi_manifest['global_summary']['total_files'] += manifest['summary'].get('total_files', 0)
            multi_manifest['global_summary']['total_folders'] += manifest['summary'].get('total_folders', 0)
            multi_manifest['global_summary']['total_bytes'] += manifest['summary'].get('total_bytes', 0)
        
        # Count total unique dependencies across all files
        unique_deps = set()
        for file_entry in manifest.get('files', []):
            unique_deps.update(file_entry.get('dependencies', []))
        multi_manifest['global_summary']['total_dependencies'] += len(unique_deps)
    
    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(multi_manifest, f, indent=2, sort_keys=True)
        print(f"Multi-repo manifest saved to: {output_path}", file=sys.stderr)
    
    return multi_manifest


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
        "--repo-list",
        help="Path to JSON file containing list of repositories for multi-repo manifest"
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
        # Handle multi-repo manifest generation
        if args.repo_list:
            # Load repo list from JSON file
            with open(args.repo_list, 'r') as f:
                repo_list = json.load(f)
            
            # Generate multi-repo manifest
            output_path = Path(args.output) if args.output else None
            multi_manifest = generate_multi_repo_manifest(repo_list, output_path)
            
            if args.json_only:
                print(json.dumps(multi_manifest, indent=2))
            else:
                # Print summary
                summary = multi_manifest['global_summary']
                print(f"\nMulti-Repo Summary:", file=sys.stderr)
                print(f"  Repositories: {summary['total_repos']}", file=sys.stderr)
                print(f"  Total files: {summary['total_files']}", file=sys.stderr)
                print(f"  Total folders: {summary['total_folders']}", file=sys.stderr)
                print(f"  Total size: {summary['total_bytes']:,} bytes", file=sys.stderr)
                print(f"  Total dependencies: {summary['total_dependencies']}", file=sys.stderr)
            return
        
        # Handle single-repo manifest generation
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
