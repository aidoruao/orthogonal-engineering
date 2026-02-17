#!/usr/bin/env python3
"""
Verification & Integrity Checker - PR #20 Deterministic Expansion Tool

SHA-256 hashing of every file, DAG cross-check, topological validation,
and cross-domain verification.
"""

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class VerificationChecker:
    """Comprehensive verification and integrity checking system."""
    
    SUPPORTED_DOMAINS = {
        'python': ['.py'],
        'javascript': ['.js'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'c': ['.c', '.h'],
        'cpp': ['.cpp', '.hpp', '.cc', '.hh'],
        'go': ['.go'],
    }
    
    def __init__(self, verification_log: str = 'verification_report.json'):
        """Initialize verification checker."""
        self.verification_log = Path(verification_log)
        self.results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'files_verified': 0,
            'hashes_computed': 0,
            'errors': [],
            'warnings': [],
            'cross_domain_checks': [],
        }
    
    def compute_file_hash(self, filepath: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, 'rb') as f:
                # Read in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.results['errors'].append({
                'file': str(filepath),
                'error': f"Hash computation failed: {str(e)}",
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
            return ""
    
    def verify_file_hash(self, filepath: Path, expected_hash: str) -> bool:
        """Verify file hash matches expected value."""
        actual_hash = self.compute_file_hash(filepath)
        
        if not actual_hash:
            return False
        
        matches = actual_hash == expected_hash
        
        if not matches:
            self.results['errors'].append({
                'file': str(filepath),
                'error': 'Hash mismatch',
                'expected': expected_hash,
                'actual': actual_hash,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
        
        return matches
    
    def verify_shard_manifest(self, manifest_path: Path) -> Dict:
        """Verify all files in a shard manifest."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            self.results['errors'].append({
                'manifest': str(manifest_path),
                'error': f"Failed to load manifest: {str(e)}",
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
            return {'verified': False, 'files_checked': 0, 'files_passed': 0}
        
        shard_dir = manifest_path.parent
        files_checked = 0
        files_passed = 0
        
        for file_info in manifest.get('files', []):
            files_checked += 1
            filepath = shard_dir / file_info['path']
            expected_hash = file_info.get('hash', '')
            
            if not filepath.exists():
                self.results['errors'].append({
                    'file': str(filepath),
                    'error': 'File not found',
                    'manifest': str(manifest_path),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })
                continue
            
            if self.verify_file_hash(filepath, expected_hash):
                files_passed += 1
                self.results['hashes_computed'] += 1
        
        self.results['files_verified'] += files_checked
        
        return {
            'verified': files_checked == files_passed,
            'files_checked': files_checked,
            'files_passed': files_passed,
            'shard_id': manifest.get('shard_id', 'unknown'),
        }
    
    def verify_dag_integrity(self, dag_manager) -> Dict:
        """Verify DAG integrity (acyclic, complete)."""
        is_valid, cycle = dag_manager.validate_acyclic()
        
        result = {
            'is_acyclic': is_valid,
            'cycle': cycle,
            'node_count': len(dag_manager.nodes),
            'edge_count': sum(len(v) for v in dag_manager.edges.values()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        
        if not is_valid:
            self.results['errors'].append({
                'dag_error': 'Cycle detected',
                'cycle_path': cycle,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
        
        return result
    
    def verify_cross_domain_references(self, shard_dir: Path) -> Dict:
        """Verify cross-domain references and dependencies."""
        domain_files = defaultdict(list)
        
        # Categorize files by domain
        for domain, extensions in self.SUPPORTED_DOMAINS.items():
            for ext in extensions:
                for filepath in shard_dir.rglob(f'*{ext}'):
                    domain_files[domain].append(filepath)
        
        cross_refs = []
        
        # Check for cross-domain imports/references
        for domain, files in domain_files.items():
            for filepath in files:
                refs = self._extract_references(filepath, domain)
                if refs:
                    cross_refs.append({
                        'file': str(filepath.relative_to(shard_dir)),
                        'domain': domain,
                        'references': refs,
                    })
        
        result = {
            'domains_found': list(domain_files.keys()),
            'files_per_domain': {d: len(f) for d, f in domain_files.items()},
            'cross_references': cross_refs,
            'cross_ref_count': len(cross_refs),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        
        self.results['cross_domain_checks'].append(result)
        return result
    
    def _extract_references(self, filepath: Path, domain: str) -> List[str]:
        """Extract import/include references from a file."""
        refs = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if domain == 'python':
                # Simple Python import extraction
                import re
                imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_.]+)', content, re.MULTILINE)
                refs.extend(imports)
            
            elif domain in ['javascript', 'typescript']:
                # Simple JS/TS import extraction
                import re
                imports = re.findall(r'(?:import|require)\s*\(?["\']([^"\']+)["\']', content)
                refs.extend(imports)
            
            elif domain == 'java':
                # Simple Java import extraction
                import re
                imports = re.findall(r'^import\s+([a-zA-Z0-9_.]+);', content, re.MULTILINE)
                refs.extend(imports)
            
            elif domain in ['c', 'cpp']:
                # Simple C/C++ include extraction
                import re
                includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
                refs.extend(includes)
            
            elif domain == 'go':
                # Simple Go import extraction
                import re
                imports = re.findall(r'import\s+(?:\([\s\S]*?\)|"([^"]+)")', content)
                refs.extend([i for i in imports if i])
        
        except Exception as e:
            self.results['warnings'].append({
                'file': str(filepath),
                'warning': f"Reference extraction failed: {str(e)}",
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
        
        return refs
    
    def verify_loc_counts(self, manifest_path: Path) -> Dict:
        """Verify LOC counts match manifest claims."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            return {'verified': False, 'error': str(e)}
        
        shard_dir = manifest_path.parent
        total_claimed_loc = manifest.get('actual_loc', 0)
        total_actual_loc = 0
        mismatches = []
        
        for file_info in manifest.get('files', []):
            filepath = shard_dir / file_info['path']
            claimed_loc = file_info.get('loc', 0)
            
            if not filepath.exists():
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    actual_loc = len(f.readlines())
                
                total_actual_loc += actual_loc
                
                if actual_loc != claimed_loc:
                    mismatches.append({
                        'file': str(filepath.relative_to(shard_dir)),
                        'claimed': claimed_loc,
                        'actual': actual_loc,
                        'diff': actual_loc - claimed_loc,
                    })
            except Exception as e:
                self.results['warnings'].append({
                    'file': str(filepath),
                    'warning': f"LOC count failed: {str(e)}",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                })
        
        result = {
            'claimed_total_loc': total_claimed_loc,
            'actual_total_loc': total_actual_loc,
            'loc_verified': total_claimed_loc == total_actual_loc,
            'mismatches': mismatches,
            'mismatch_count': len(mismatches),
        }
        
        if not result['loc_verified']:
            self.results['warnings'].append({
                'manifest': str(manifest_path),
                'warning': 'Total LOC mismatch',
                'claimed': total_claimed_loc,
                'actual': total_actual_loc,
                'diff': total_actual_loc - total_claimed_loc,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
        
        return result
    
    def generate_verification_report(self) -> Dict:
        """Generate comprehensive verification report."""
        report = {
            **self.results,
            'summary': {
                'total_files_verified': self.results['files_verified'],
                'total_hashes_computed': self.results['hashes_computed'],
                'total_errors': len(self.results['errors']),
                'total_warnings': len(self.results['warnings']),
                'verification_passed': len(self.results['errors']) == 0,
            },
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }
        
        return report
    
    def save_report(self, output_file: Optional[str] = None) -> None:
        """Save verification report to JSON file."""
        if output_file is None:
            output_file = self.verification_log
        
        report = self.generate_verification_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    
    def verify_all_shards(self, shards_dir: Path) -> List[Dict]:
        """Verify all shards in a directory."""
        results = []
        
        for manifest_path in shards_dir.glob('*/manifest.json'):
            print(f"Verifying shard: {manifest_path.parent.name}")
            
            # Verify manifest integrity
            manifest_result = self.verify_shard_manifest(manifest_path)
            
            # Verify LOC counts
            loc_result = self.verify_loc_counts(manifest_path)
            
            # Verify cross-domain references
            cross_domain_result = self.verify_cross_domain_references(manifest_path.parent)
            
            results.append({
                'shard_id': manifest_path.parent.name,
                'manifest_verification': manifest_result,
                'loc_verification': loc_result,
                'cross_domain_verification': cross_domain_result,
            })
        
        return results


def main():
    """Main function for testing verification checker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify shard integrity and hashes')
    parser.add_argument('--shards-dir', type=str, required=True, help='Directory containing shards')
    parser.add_argument('--output', type=str, default='verification_report.json', help='Output report file')
    parser.add_argument('--dag-file', type=str, help='DAG manifest file to verify')
    
    args = parser.parse_args()
    
    checker = VerificationChecker(verification_log=args.output)
    
    print("Starting verification...")
    shards_dir = Path(args.shards_dir)
    
    # Verify all shards
    shard_results = checker.verify_all_shards(shards_dir)
    
    # Verify DAG if provided
    if args.dag_file:
        from dag_manager import DAGManager
        dag = DAGManager(args.dag_file)
        dag_result = checker.verify_dag_integrity(dag)
        print(f"\nDAG verification: {'PASSED' if dag_result['is_acyclic'] else 'FAILED'}")
    
    # Generate and save report
    checker.save_report(args.output)
    
    # Print summary
    report = checker.generate_verification_report()
    summary = report['summary']
    
    print(f"\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Files verified: {summary['total_files_verified']}")
    print(f"Hashes computed: {summary['total_hashes_computed']}")
    print(f"Errors: {summary['total_errors']}")
    print(f"Warnings: {summary['total_warnings']}")
    print(f"Status: {'PASSED ✓' if summary['verification_passed'] else 'FAILED ✗'}")
    print(f"{'='*60}")
    print(f"\nFull report saved to: {args.output}")


if __name__ == '__main__':
    main()
