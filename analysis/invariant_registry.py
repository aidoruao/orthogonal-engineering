#!/usr/bin/env python3
"""
invariant_registry.py
Central registry for tracking INV-001 through INV-008 and beyond
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

class InvariantRegistry:
    def __init__(self, registry_file: str = "evidence/invariant_registry.json"):
        self.registry_file = Path(registry_file)
        self.invariants = self._load_registry()
        
    def _load_registry(self) -> Dict:
        """Load existing registry or create new one"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {"invariants": [], "last_updated": None}
    
    def _save_registry(self):
        """Save registry to disk"""
        self.invariants["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.invariants, f, indent=2)
    
    def register(self, inv_id: str, claim: str, test_method: str, 
                 precision_score: float, location: str, status: str = "validated"):
        """Register a new invariant"""
        
        entry = {
            "id": inv_id,
            "claim": claim,
            "test_method": test_method,
            "precision_score": precision_score,
            "location": location,
            "status": status,
            "discovery_timestamp": datetime.now(timezone.utc).isoformat(),
            "last_validated": datetime.now(timezone.utc).isoformat()
        }
        
        # Check if already exists
        for i, inv in enumerate(self.invariants["invariants"]):
            if inv["id"] == inv_id:
                self.invariants["invariants"][i] = entry
                self._save_registry()
                return f"Updated {inv_id}"
        
        # Add new
        self.invariants["invariants"].append(entry)
        self._save_registry()
        return f"Registered {inv_id}"
    
    def query(self, inv_id: Optional[str] = None) -> List[Dict]:
        """Query invariants"""
        if inv_id:
            return [inv for inv in self.invariants["invariants"] if inv["id"] == inv_id]
        return self.invariants["invariants"]
    
    def get_by_status(self, status: str) -> List[Dict]:
        """Get invariants by status"""
        return [inv for inv in self.invariants["invariants"] if inv["status"] == status]
    
    def update_precision(self, inv_id: str, new_precision: float):
        """Update precision score for an invariant"""
        for inv in self.invariants["invariants"]:
            if inv["id"] == inv_id:
                inv["precision_score"] = new_precision
                inv["last_validated"] = datetime.now(timezone.utc).isoformat()
                self._save_registry()
                return True
        return False
    
    def initialize_core_invariants(self):
        """Initialize INV-001 through INV-008"""
        
        core = [
            ("INV-001", "Invariant density is measurable", "Mathematical formula", 100.0, "INVARIANTS.md"),
            ("INV-002", "Constraint language detectable", "Pattern matching", 100.0, "analysis/canal_detector_v1.py"),
            ("INV-003", "Mimicry vs grounding distinguishable", "Implementation test", 100.0, "INVARIANTS.md"),
            ("INV-004", "System contains own falsification", "Structural property", 100.0, "analysis/automated_test_suite.py"),
            ("INV-005", "Mimicry detectable via repetition", "Repetition ratio >50%", 100.0, "analysis/canal_detector_v1.py"),
            ("INV-006", "Window-based agreement insufficient", "Falsification test", 100.0, "FAILURES.md"),
            ("INV-007", "Correspondence is truth anchor", "Implementation validation", 85.0, "proof/minecraft_computercraft_invariant.lua"),
            ("INV-008", "No methodology survives broken tools", "Tool precision requirement", 100.0, "FAILURES.md")
        ]
        
        for inv_id, claim, test, precision, location in core:
            self.register(inv_id, claim, test, precision, location, "validated")
        
        print(f"DONE: Initialized {len(core)} core invariants")

if __name__ == "__main__":
    registry = InvariantRegistry()
    registry.initialize_core_invariants()
    
    print("\n" + "="*70)
    print("INVARIANT REGISTRY")
    print("="*70)
    
    for inv in registry.query():
        print(f"\n{inv['id']}: {inv['claim']}")
        print(f"  Precision: {inv['precision_score']:.1f}%")
        print(f"  Location: {inv['location']}")
        print(f"  Status: {inv['status']}")
