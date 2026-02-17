#!/usr/bin/env python3
"""
Audit Trail Generator - PR #20 Deterministic Expansion Tool

Deterministic logging of every line added, modified, or removed.
Exportable to JSON/JSONL with human-readable format and timestamps.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


class AuditTrailGenerator:
    """Generates comprehensive audit trails for all operations."""
    
    def __init__(self, audit_file: str = 'audit_trail.jsonl', metadata: Optional[Dict] = None):
        """Initialize audit trail generator."""
        self.audit_file = Path(audit_file)
        self.metadata = metadata or {}
        self.entry_count = 0
        self.session_id = hashlib.sha256(
            datetime.now(timezone.utc).isoformat().encode()
        ).hexdigest()[:16]
        
        # Initialize audit file if it doesn't exist
        if not self.audit_file.exists():
            self.audit_file.parent.mkdir(parents=True, exist_ok=True)
            self.audit_file.touch()
    
    def log_entry(self, operation: str, details: Dict[str, Any], category: str = 'general') -> None:
        """Log a single audit trail entry."""
        entry = {
            'entry_id': self.entry_count,
            'session_id': self.session_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'operation': operation,
            'category': category,
            'details': details,
            'metadata': self.metadata,
        }
        
        # Compute entry hash for integrity
        entry_content = json.dumps(entry, sort_keys=True)
        entry['entry_hash'] = hashlib.sha256(entry_content.encode()).hexdigest()
        
        # Append to JSONL file
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        self.entry_count += 1
    
    def log_file_created(self, filepath: str, file_hash: str, loc: int, domain: str) -> None:
        """Log file creation event."""
        self.log_entry(
            operation='file_created',
            category='file_operation',
            details={
                'filepath': filepath,
                'file_hash': file_hash,
                'loc': loc,
                'domain': domain,
            }
        )
    
    def log_file_modified(self, filepath: str, old_hash: str, new_hash: str, 
                         loc_before: int, loc_after: int) -> None:
        """Log file modification event."""
        self.log_entry(
            operation='file_modified',
            category='file_operation',
            details={
                'filepath': filepath,
                'old_hash': old_hash,
                'new_hash': new_hash,
                'loc_before': loc_before,
                'loc_after': loc_after,
                'loc_delta': loc_after - loc_before,
            }
        )
    
    def log_file_deleted(self, filepath: str, file_hash: str, loc: int) -> None:
        """Log file deletion event."""
        self.log_entry(
            operation='file_deleted',
            category='file_operation',
            details={
                'filepath': filepath,
                'file_hash': file_hash,
                'loc': loc,
            }
        )
    
    def log_shard_created(self, shard_id: str, level: int, target_loc: int, 
                         actual_loc: int, domains: List[str]) -> None:
        """Log shard creation event."""
        self.log_entry(
            operation='shard_created',
            category='shard_operation',
            details={
                'shard_id': shard_id,
                'level': level,
                'target_loc': target_loc,
                'actual_loc': actual_loc,
                'loc_delta': actual_loc - target_loc,
                'domains': domains,
                'file_count': 0,  # Will be updated
            }
        )
    
    def log_shard_verified(self, shard_id: str, verification_result: Dict) -> None:
        """Log shard verification event."""
        self.log_entry(
            operation='shard_verified',
            category='verification',
            details={
                'shard_id': shard_id,
                'verification_result': verification_result,
            }
        )
    
    def log_dag_updated(self, node_id: str, node_type: str, dependencies: List[str]) -> None:
        """Log DAG update event."""
        self.log_entry(
            operation='dag_node_added',
            category='dag_operation',
            details={
                'node_id': node_id,
                'node_type': node_type,
                'dependencies': dependencies,
                'dependency_count': len(dependencies),
            }
        )
    
    def log_dag_validated(self, is_valid: bool, cycle: Optional[List[str]] = None) -> None:
        """Log DAG validation event."""
        self.log_entry(
            operation='dag_validated',
            category='verification',
            details={
                'is_valid': is_valid,
                'cycle': cycle,
            }
        )
    
    def log_verification_checkpoint(self, checkpoint_type: str, stats: Dict) -> None:
        """Log verification checkpoint event."""
        self.log_entry(
            operation='verification_checkpoint',
            category='checkpoint',
            details={
                'checkpoint_type': checkpoint_type,
                'stats': stats,
            }
        )
    
    def log_expansion_started(self, target_loc: int, current_loc: int, seed: int) -> None:
        """Log expansion start event."""
        self.log_entry(
            operation='expansion_started',
            category='expansion',
            details={
                'target_loc': target_loc,
                'current_loc': current_loc,
                'remaining_loc': target_loc - current_loc,
                'seed': seed,
            }
        )
    
    def log_expansion_completed(self, final_loc: int, target_loc: int, 
                               shards_created: int, duration_seconds: float) -> None:
        """Log expansion completion event."""
        self.log_entry(
            operation='expansion_completed',
            category='expansion',
            details={
                'final_loc': final_loc,
                'target_loc': target_loc,
                'loc_delta': final_loc - target_loc,
                'shards_created': shards_created,
                'duration_seconds': duration_seconds,
            }
        )
    
    def log_error(self, error_type: str, error_message: str, context: Dict) -> None:
        """Log error event."""
        self.log_entry(
            operation='error',
            category='error',
            details={
                'error_type': error_type,
                'error_message': error_message,
                'context': context,
            }
        )
    
    def get_stats(self) -> Dict:
        """Get audit trail statistics."""
        if not self.audit_file.exists():
            return {
                'total_entries': 0,
                'session_id': self.session_id,
            }
        
        entries_by_category = {}
        entries_by_operation = {}
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                category = entry.get('category', 'unknown')
                operation = entry.get('operation', 'unknown')
                
                entries_by_category[category] = entries_by_category.get(category, 0) + 1
                entries_by_operation[operation] = entries_by_operation.get(operation, 0) + 1
        
        return {
            'total_entries': self.entry_count,
            'session_id': self.session_id,
            'entries_by_category': entries_by_category,
            'entries_by_operation': entries_by_operation,
            'audit_file': str(self.audit_file),
        }
    
    def export_to_json(self, output_file: str) -> None:
        """Export audit trail to JSON array format."""
        entries = []
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2)
    
    def export_to_markdown(self, output_file: str) -> None:
        """Export audit trail to human-readable Markdown format."""
        entries = []
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('# Audit Trail Report\n\n')
            f.write(f'**Session ID:** {self.session_id}\n\n')
            f.write(f'**Total Entries:** {len(entries)}\n\n')
            f.write('---\n\n')
            
            for entry in entries:
                f.write(f'## Entry {entry["entry_id"]}\n\n')
                f.write(f'- **Timestamp:** {entry["timestamp"]}\n')
                f.write(f'- **Operation:** {entry["operation"]}\n')
                f.write(f'- **Category:** {entry["category"]}\n')
                f.write(f'- **Hash:** `{entry["entry_hash"][:16]}...`\n\n')
                f.write('**Details:**\n\n')
                f.write('```json\n')
                f.write(json.dumps(entry["details"], indent=2))
                f.write('\n```\n\n')
                f.write('---\n\n')
    
    def verify_integrity(self) -> Dict:
        """Verify audit trail integrity by checking entry hashes."""
        corrupted_entries = []
        total_entries = 0
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                total_entries += 1
                entry = json.loads(line)
                stored_hash = entry.get('entry_hash', '')
                
                # Recompute hash
                entry_copy = {k: v for k, v in entry.items() if k != 'entry_hash'}
                entry_content = json.dumps(entry_copy, sort_keys=True)
                computed_hash = hashlib.sha256(entry_content.encode()).hexdigest()
                
                if computed_hash != stored_hash:
                    corrupted_entries.append({
                        'line_number': line_num,
                        'entry_id': entry.get('entry_id', 'unknown'),
                        'stored_hash': stored_hash,
                        'computed_hash': computed_hash,
                    })
        
        return {
            'total_entries': total_entries,
            'corrupted_count': len(corrupted_entries),
            'is_intact': len(corrupted_entries) == 0,
            'corrupted_entries': corrupted_entries,
        }


def main():
    """Main function for testing audit trail generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage audit trail')
    parser.add_argument('--audit-file', type=str, default='audit_trail.jsonl', help='Audit trail file')
    parser.add_argument('--action', choices=['stats', 'verify', 'export-json', 'export-md'], 
                       default='stats', help='Action to perform')
    parser.add_argument('--output', type=str, help='Output file for export')
    
    args = parser.parse_args()
    
    audit = AuditTrailGenerator(audit_file=args.audit_file)
    
    if args.action == 'stats':
        stats = audit.get_stats()
        print("Audit Trail Statistics:")
        print(json.dumps(stats, indent=2))
    
    elif args.action == 'verify':
        result = audit.verify_integrity()
        print("Audit Trail Integrity Check:")
        if result['is_intact']:
            print("✓ All entries verified - audit trail is intact")
        else:
            print(f"✗ Found {result['corrupted_count']} corrupted entries")
            print(json.dumps(result['corrupted_entries'], indent=2))
    
    elif args.action == 'export-json':
        output_file = args.output or 'audit_trail.json'
        audit.export_to_json(output_file)
        print(f"Audit trail exported to {output_file}")
    
    elif args.action == 'export-md':
        output_file = args.output or 'audit_trail.md'
        audit.export_to_markdown(output_file)
        print(f"Audit trail exported to {output_file}")


if __name__ == '__main__':
    main()
