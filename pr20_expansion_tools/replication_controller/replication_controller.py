#!/usr/bin/env python3
"""
Replication Controller - PR #20 Deterministic Expansion Tool

Iterates shard creation until target LOC reached.
Splits or merges shards per threshold with deterministic parallel execution.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
sys.path.append(str(Path(__file__).parent.parent))

from shard_generator.shard_generator import ShardGenerator
from dag_manager.dag_manager import DAGManager
from verification.verification_checker import VerificationChecker
from audit_trail.audit_trail_generator import AuditTrailGenerator


class ReplicationController:
    """Controls shard replication and LOC expansion."""
    
    VERIFICATION_INTERVALS = {
        'dag_check': 10000,  # Every 10k LOC
        'full_audit': 50000,  # Every 50k LOC
        'cross_domain': 100000,  # Every 100k LOC
    }
    
    def __init__(self, target_loc: int, seed: int = 42, output_dir: str = './pr20_generated'):
        """Initialize replication controller."""
        self.target_loc = target_loc
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.generator = ShardGenerator(seed=seed, output_dir=str(self.output_dir))
        self.dag = DAGManager(dag_file=str(self.output_dir / 'dag_manifest.json'))
        self.verifier = VerificationChecker(verification_log=str(self.output_dir / 'verification_report.json'))
        self.audit = AuditTrailGenerator(audit_file=str(self.output_dir / 'audit_trail.jsonl'))
        
        self.current_loc = 0
        self.shards_created = []
        self.start_time = None
    
    def calculate_shard_plan(self) -> List[Dict]:
        """Calculate optimal shard generation plan."""
        remaining_loc = self.target_loc - self.current_loc
        plan = []
        
        # Use different shard levels efficiently
        shard_levels = ShardGenerator.SHARD_LEVELS
        
        # Start with largest shards
        for level in sorted(shard_levels.keys()):
            level_info = shard_levels[level]
            target_per_shard = level_info['target_loc']
            
            while remaining_loc >= target_per_shard:
                shard_id = f"shard-L{level}-{len(plan):05d}"
                plan.append({
                    'shard_id': shard_id,
                    'level': level,
                    'target_loc': target_per_shard,
                })
                remaining_loc -= target_per_shard
        
        return plan
    
    def create_shard_with_verification(self, shard_plan: Dict, domains: List[str]) -> Optional[Dict]:
        """Create a shard and verify it immediately."""
        shard_id = shard_plan['shard_id']
        level = shard_plan['level']
        
        print(f"Creating shard: {shard_id} (Level {level})")
        
        try:
            # Create shard
            shard_data = self.generator.create_shard(level, shard_id, domains)
            
            # Log to audit trail
            self.audit.log_shard_created(
                shard_id=shard_id,
                level=level,
                target_loc=shard_data['target_loc'],
                actual_loc=shard_data['actual_loc'],
                domains=domains
            )
            
            # Log each file creation
            for file_info in shard_data['files']:
                self.audit.log_file_created(
                    filepath=file_info['path'],
                    file_hash=file_info['hash'],
                    loc=file_info['loc'],
                    domain=file_info['domain']
                )
            
            # Add to DAG
            self.dag.add_shard(shard_id, shard_data)
            self.audit.log_dag_updated(shard_id, 'shard', [])
            
            # Verify shard
            manifest_path = self.output_dir / shard_id / 'manifest.json'
            verification_result = self.verifier.verify_shard_manifest(manifest_path)
            
            self.audit.log_shard_verified(shard_id, verification_result)
            
            if not verification_result['verified']:
                print(f"  ✗ Shard verification failed!")
                self.audit.log_error(
                    'shard_verification_failed',
                    f"Shard {shard_id} failed verification",
                    verification_result
                )
                return None
            
            print(f"  ✓ Shard created: {shard_data['actual_loc']} LOC")
            self.current_loc += shard_data['actual_loc']
            self.shards_created.append(shard_id)
            
            return shard_data
            
        except Exception as e:
            print(f"  ✗ Error creating shard: {str(e)}")
            self.audit.log_error(
                'shard_creation_failed',
                str(e),
                {'shard_id': shard_id, 'level': level}
            )
            return None
    
    def run_verification_checkpoint(self, checkpoint_type: str) -> bool:
        """Run verification checkpoint based on LOC milestones."""
        print(f"\n{'='*60}")
        print(f"VERIFICATION CHECKPOINT: {checkpoint_type}")
        print(f"{'='*60}")
        
        if checkpoint_type == 'dag_check':
            # Validate DAG
            is_valid, cycle = self.dag.validate_acyclic()
            self.audit.log_dag_validated(is_valid, cycle)
            
            if not is_valid:
                print(f"✗ DAG validation failed: cycle detected")
                print(f"  Cycle: {' -> '.join(cycle)}")
                return False
            
            print(f"✓ DAG is valid (acyclic)")
            return True
        
        elif checkpoint_type == 'full_audit':
            # Run full audit and hash verification
            shard_results = self.verifier.verify_all_shards(self.output_dir)
            
            failed_shards = [r for r in shard_results if not r['manifest_verification']['verified']]
            
            if failed_shards:
                print(f"✗ {len(failed_shards)} shards failed verification")
                return False
            
            print(f"✓ All {len(shard_results)} shards verified")
            return True
        
        elif checkpoint_type == 'cross_domain':
            # Verify cross-domain references
            for shard_id in self.shards_created:
                shard_dir = self.output_dir / shard_id
                self.verifier.verify_cross_domain_references(shard_dir)
            
            print(f"✓ Cross-domain verification complete")
            return True
        
        return True
    
    def expand_to_target(self, domains: List[str] = None, dry_run: bool = False) -> Dict:
        """Main expansion loop to reach target LOC."""
        if domains is None:
            domains = ['python', 'javascript', 'typescript', 'java', 'go']
        
        self.start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"PR #20 EXPANSION STARTED")
        print(f"{'='*60}")
        print(f"Target LOC: {self.target_loc:,}")
        print(f"Current LOC: {self.current_loc:,}")
        print(f"Remaining: {self.target_loc - self.current_loc:,}")
        print(f"Seed: {self.seed}")
        print(f"Domains: {', '.join(domains)}")
        print(f"Dry Run: {dry_run}")
        print(f"{'='*60}\n")
        
        # Log expansion start
        self.audit.log_expansion_started(self.target_loc, self.current_loc, self.seed)
        
        if dry_run:
            print("DRY RUN - No files will be created")
            shard_plan = self.calculate_shard_plan()
            print(f"\nPlanned shards: {len(shard_plan)}")
            for plan in shard_plan[:10]:  # Show first 10
                print(f"  - {plan['shard_id']}: Level {plan['level']}, {plan['target_loc']:,} LOC")
            if len(shard_plan) > 10:
                print(f"  ... and {len(shard_plan) - 10} more")
            return {'dry_run': True, 'planned_shards': len(shard_plan)}
        
        # Calculate shard plan
        shard_plan = self.calculate_shard_plan()
        print(f"Shard plan: {len(shard_plan)} shards\n")
        
        # Create shards
        last_checkpoint_loc = 0
        
        for i, plan in enumerate(shard_plan):
            # Check if we've exceeded target
            if self.current_loc >= self.target_loc:
                print(f"\n✓ Target LOC reached! Stopping expansion.")
                break
            
            # Create shard
            shard_data = self.create_shard_with_verification(plan, domains)
            
            if shard_data is None:
                print(f"✗ Failed to create shard, stopping expansion")
                break
            
            # Check for verification checkpoints
            for checkpoint_type, interval in self.VERIFICATION_INTERVALS.items():
                if self.current_loc - last_checkpoint_loc >= interval:
                    if not self.run_verification_checkpoint(checkpoint_type):
                        print(f"✗ Verification checkpoint failed, stopping expansion")
                        return self.finalize_expansion()
                    last_checkpoint_loc = self.current_loc
            
            # Progress update
            progress = (self.current_loc / self.target_loc) * 100
            print(f"Progress: {self.current_loc:,} / {self.target_loc:,} LOC ({progress:.1f}%)\n")
        
        return self.finalize_expansion()
    
    def finalize_expansion(self) -> Dict:
        """Finalize expansion and generate reports."""
        duration = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n{'='*60}")
        print(f"PR #20 EXPANSION COMPLETED")
        print(f"{'='*60}")
        print(f"Final LOC: {self.current_loc:,}")
        print(f"Target LOC: {self.target_loc:,}")
        print(f"Delta: {self.current_loc - self.target_loc:+,}")
        print(f"Shards created: {len(self.shards_created)}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"{'='*60}\n")
        
        # Log expansion completion
        self.audit.log_expansion_completed(
            final_loc=self.current_loc,
            target_loc=self.target_loc,
            shards_created=len(self.shards_created),
            duration_seconds=duration
        )
        
        # Save DAG
        self.dag.save()
        print(f"✓ DAG saved: {self.output_dir / 'dag_manifest.json'}")
        
        # Save verification report
        self.verifier.save_report()
        print(f"✓ Verification report saved: {self.output_dir / 'verification_report.json'}")
        
        # Export audit trail
        self.audit.export_to_json(str(self.output_dir / 'audit_trail.json'))
        self.audit.export_to_markdown(str(self.output_dir / 'audit_trail.md'))
        print(f"✓ Audit trail saved: {self.output_dir / 'audit_trail.*'}")
        
        # Generate summary
        summary = {
            'final_loc': self.current_loc,
            'target_loc': self.target_loc,
            'delta': self.current_loc - self.target_loc,
            'shards_created': len(self.shards_created),
            'duration_seconds': duration,
            'seed': self.seed,
            'output_dir': str(self.output_dir),
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }
        
        with open(self.output_dir / 'expansion_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary


def main():
    """Main function for running replication controller."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PR #20 Replication Controller')
    parser.add_argument('--target-loc', type=int, default=1000000000, help='Target lines of code')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for deterministic generation')
    parser.add_argument('--output-dir', type=str, default='./pr20_generated', help='Output directory')
    parser.add_argument('--domains', type=str, default='python,javascript,typescript,java,go', 
                       help='Comma-separated list of domains')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without creating files')
    
    args = parser.parse_args()
    
    domains = args.domains.split(',')
    
    controller = ReplicationController(
        target_loc=args.target_loc,
        seed=args.seed,
        output_dir=args.output_dir
    )
    
    result = controller.expand_to_target(domains=domains, dry_run=args.dry_run)
    
    print("\nExpansion complete!")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
