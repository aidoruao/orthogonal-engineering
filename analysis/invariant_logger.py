"""
CONTINUOUS INVARIANT LOGGER
Automatically logs new invariants discovered during Desktop Commander usage
Follows ChatGPT's 7-invariant framework: only log if proven, falsifiable, reproducible
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import hashlib

class InvariantLogger:
    """
    Logs invariants discovered through Desktop Commander operations
    Following strict criteria: proven, falsifiable, reproducible, universal
    """
    
    def __init__(self, log_path="C:/Users/Aidor/orthogonal-engineering/logs"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.invariant_log = self.log_path / "invariant_log.jsonl"
        self.test_log = self.log_path / "test_results.jsonl"
        
    def log_invariant(self, invariant_data):
        """
        Log a new invariant with strict validation
        
        Required fields:
        - claim: What is being claimed
        - evidence: How it was discovered
        - test: How it can be falsified
        - reproducibility: Steps to reproduce
        - universality: Does it generalize?
        """
        
        # Validate required fields
        required = ['claim', 'evidence', 'test', 'reproducibility', 'universality']
        if not all(field in invariant_data for field in required):
            raise ValueError(f"Missing required fields. Need: {required}")
        
        # Generate unique ID
        invariant_id = self._generate_id(invariant_data['claim'])
        
        # Add metadata
        entry = {
            'id': invariant_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'invariant',
            'status': 'pending_validation',
            **invariant_data
        }
        
        # Append to log
        with open(self.invariant_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        print(f"[INVARIANT LOGGED] {invariant_id}: {invariant_data['claim'][:50]}...")
        return invariant_id
    
    def log_test_result(self, invariant_id, test_name, passed, details):
        """Log test result for an invariant"""
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'invariant_id': invariant_id,
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'status': 'validated' if passed else 'falsified'
        }
        
        with open(self.test_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"[TEST RESULT] {status} - {test_name} for {invariant_id}")
        
    def _generate_id(self, claim):
        """Generate unique ID from claim text"""
        return f"INV-{hashlib.sha256(claim.encode()).hexdigest()[:8].upper()}"
    
    def get_validated_invariants(self):
        """Get all invariants that have passed testing"""
        
        if not self.invariant_log.exists():
            return []
        
        # Load all invariants
        invariants = []
        with open(self.invariant_log, 'r', encoding='utf-8') as f:
            for line in f:
                invariants.append(json.loads(line))
        
        # Load all test results
        test_results = {}
        if self.test_log.exists():
            with open(self.test_log, 'r', encoding='utf-8') as f:
                for line in f:
                    result = json.loads(line)
                    inv_id = result['invariant_id']
                    if inv_id not in test_results:
                        test_results[inv_id] = []
                    test_results[inv_id].append(result)
        
        # Filter to validated only
        validated = []
        for inv in invariants:
            inv_id = inv['id']
            if inv_id in test_results:
                # Check if all tests passed
                results = test_results[inv_id]
                if all(r['passed'] for r in results):
                    inv['test_results'] = results
                    validated.append(inv)
        
        return validated


# EXAMPLE USAGE
if __name__ == "__main__":
    logger = InvariantLogger()
    
    # Example: Log a new invariant discovered during this session
    example_invariant = {
        'claim': 'Detector precision <80% indicates unacceptable false positive rate',
        'evidence': 'DeepSeek falsification showed 30% precision = 70% FP rate caused systematic error',
        'test': 'Sample 100 verified turns, manually check for constraint language. Calculate precision = TP/(TP+FP). Pass if >=80%',
        'reproducibility': 'Run falsify_density_claim.py with any refined_inventory.csv, check TEST 1 output',
        'universality': 'Applies to any pattern-matching detector on any conversational dataset',
        'category': 'detector_validation',
        'threshold': 80.0,
        'comparison_baseline': 'Random classifier = 50%, our requirement = 80%'
    }
    
    # Log it
    inv_id = logger.log_invariant(example_invariant)
    
    # Simulate test result
    logger.log_test_result(
        inv_id,
        'precision_check_deepseek',
        passed=False,  # Failed: only 30%
        details={'measured_precision': 30.0, 'threshold': 80.0, 'dataset': 'deepseek_refined_inventory.csv'}
    )
    
    logger.log_test_result(
        inv_id,
        'precision_check_chat_canon',
        passed=True,  # Need to actually test this
        details={'measured_precision': 85.0, 'threshold': 80.0, 'dataset': 'chat_canon_refined_inventory.csv'}
    )
    
    # Get validated invariants
    validated = logger.get_validated_invariants()
    print(f"\n[VALIDATED INVARIANTS] {len(validated)} total")
    for inv in validated:
        print(f"  {inv['id']}: {inv['claim']}")
