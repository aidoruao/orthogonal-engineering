#!/usr/bin/env python3
"""
Food Cart Universe Validator
=============================

Validates all Food Cart Universe invariants.

Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import List

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)


class FoodCartValidator:
    """Validates all Food Cart Universe invariants."""
    
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.errors: List[str] = []
        
    def validate_all(self) -> bool:
        print("🔍 Food Cart Universe - Invariant Validation")
        print("=" * 80)
        print()
        
        checks = [
            ("Universe Seed", self._validate_seed),
            ("DAG Structure", self._validate_dag),
            ("Dish Projections", self._validate_dish_projections),
            ("Manifest", self._validate_manifest),
            ("Merkle Root", self._validate_merkle_root),
            ("Topology Integration", self._validate_topology),
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
        seed_path = self.root / "seed" / "food_cart_universe.yaml"
        if not seed_path.exists():
            self.errors.append(f"Seed file not found: {seed_path}")
            return False
        with open(seed_path, 'r') as f:
            seed = yaml.safe_load(f)
        for field in ['universe', 'invariants', 'metadata']:
            if field not in seed:
                self.errors.append(f"Seed missing: {field}")
                return False
        return True
        
    def _validate_dag(self) -> bool:
        dag_path = self.root / "out" / "food_cart_dag.json"
        if not dag_path.exists():
            self.errors.append(f"DAG not found: {dag_path}")
            return False
        return True
        
    def _validate_dish_projections(self) -> bool:
        dishes_dir = self.root / "data" / "dishes"
        if not dishes_dir.exists():
            self.errors.append(f"Dishes directory not found")
            return False
        dish_files = list(dishes_dir.glob("*.json"))
        return len(dish_files) > 0
        
    def _validate_manifest(self) -> bool:
        manifest_path = self.root / "out" / "food_cart_manifest.jsonl"
        if not manifest_path.exists():
            self.errors.append(f"Manifest not found")
            return False
        return True
        
    def _validate_merkle_root(self) -> bool:
        merkle_path = self.root / "out" / "food_cart_merkle_root.txt"
        if not merkle_path.exists():
            self.errors.append(f"Merkle root not found")
            return False
        return True
        
    def _validate_topology(self) -> bool:
        topology_path = self.root / "topology_graph.json"
        if not topology_path.exists():
            self.errors.append(f"Topology not found")
            return False
        with open(topology_path, 'r') as f:
            topology = json.load(f)
        food_nodes = {k: v for k, v in topology['nodes'].items() 
                      if v.get('node_class') == 'FOOD_DISH_UNIVERSE'}
        if not food_nodes:
            self.errors.append("No FOOD_DISH_UNIVERSE nodes in topology")
            return False
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    
    validator = FoodCartValidator(args.root)
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
