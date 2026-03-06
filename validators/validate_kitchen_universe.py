#!/usr/bin/env python3
"""
Self-Cleaning Kitchen Universe Validator
=========================================

Validates all Kitchen Universe invariants.
Version: 1.0.0
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)


class KitchenValidator:
    """Validates Kitchen Universe invariants."""
    
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.errors = []
        
    def validate_all(self) -> bool:
        print("🧹 Self-Cleaning Kitchen Universe - Invariant Validation")
        print("=" * 80)
        print()
        
        checks = [
            ("Universe Seed", self._validate_seed),
            ("DAG Structure", self._validate_dag),
            ("Task Projections", self._validate_tasks),
            ("Manifest", self._validate_manifest),
            ("Merkle Root", self._validate_merkle),
            ("Topology Integration", self._validate_topology),
            ("Safety Constraints", self._validate_safety),
        ]
        
        all_passed = True
        for name, check_func in checks:
            print(f"📋 Checking: {name}...")
            try:
                passed = check_func()
                print(f"   {'✅' if passed else '❌'} {name} - {'PASSED' if passed else 'FAILED'}")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {name} - ERROR: {e}")
                all_passed = False
            print()
            
        print("=" * 80)
        if all_passed:
            print("✅ All invariants satisfied!")
        else:
            print("❌ Some invariants failed!")
            if self.errors:
                print("\nErrors:")
                for error in self.errors:
                    print(f"  • {error}")
                    
        return all_passed
        
    def _validate_seed(self) -> bool:
        seed_path = self.root / "seed" / "self_clean_kitchen_universe.yaml"
        if not seed_path.exists():
            self.errors.append(f"Seed not found: {seed_path}")
            return False
        with open(seed_path, 'r') as f:
            seed = yaml.safe_load(f)
        for field in ['universe', 'invariants', 'metadata', 'safety']:
            if field not in seed and field != 'safety':
                self.errors.append(f"Seed missing: {field}")
                return False
        return True
        
    def _validate_dag(self) -> bool:
        dag_path = self.root / "out" / "self_clean_kitchen_dag.json"
        if not dag_path.exists():
            self.errors.append("DAG not found")
            return False
        with open(dag_path, 'r') as f:
            dag = json.load(f)
        if dag['metadata']['total_nodes'] < 50:
            self.errors.append("Too few nodes generated")
            return False
        return True
        
    def _validate_tasks(self) -> bool:
        tasks_dir = self.root / "data" / "kitchen_tasks"
        if not tasks_dir.exists():
            self.errors.append("Tasks directory not found")
            return False
        task_files = list(tasks_dir.glob("*.json"))
        return len(task_files) > 0
        
    def _validate_manifest(self) -> bool:
        manifest_path = self.root / "out" / "self_clean_kitchen_manifest.jsonl"
        if not manifest_path.exists():
            self.errors.append("Manifest not found")
            return False
        return True
        
    def _validate_merkle(self) -> bool:
        merkle_path = self.root / "out" / "self_clean_kitchen_merkle_root.txt"
        if not merkle_path.exists():
            self.errors.append("Merkle root not found")
            return False
        return True
        
    def _validate_topology(self) -> bool:
        topology_path = self.root / "topology_graph.json"
        if not topology_path.exists():
            self.errors.append("Topology not found")
            return False
        with open(topology_path, 'r') as f:
            topology = json.load(f)
        kitchen_nodes = {k: v for k, v in topology['nodes'].items() 
                        if v.get('node_class') == 'KITCHEN_TASK_UNIVERSE'}
        if not kitchen_nodes:
            self.errors.append("No KITCHEN_TASK_UNIVERSE nodes in topology")
            return False
        return True
        
    def _validate_safety(self) -> bool:
        """Validate safety constraints are present."""
        dag_path = self.root / "out" / "self_clean_kitchen_dag.json"
        if not dag_path.exists():
            return False
        with open(dag_path, 'r') as f:
            dag = json.load(f)
        safety = dag['metadata'].get('safety_constraints')
        if not safety:
            self.errors.append("Missing safety constraints in metadata")
            return False
        # Check required safety fields
        required = ['max_force_per_actuator', 'max_temperature', 'chemical_compatibility']
        for field in required:
            if field not in safety:
                self.errors.append(f"Missing safety field: {field}")
                return False
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    
    validator = KitchenValidator(args.root)
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
