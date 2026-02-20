#!/usr/bin/env python3
"""
Repository inventory for PR #29 conformance audit.
Maps every file to Yeshua Mathematics domain.
Author: Orthogonal Engineering
PR: #29
Version: 1.0.0
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Set

# Foundation files exempt from self-audit
EXEMPT_FILES = {
    "mathematical_core.py",
    "test_peano_axioms.py", 
    "test_boolean_algebra.py",
    "repository_inventory.py",
    "test_repository_compliance.py",
}

def inventory_repository(repo_root: Path) -> Dict[str, List[str]]:
    """Categorize all Python files by Yeshua Mathematics domain."""
    inventory = {
        "PEANO-001": [],      # Uses successor/predecessor
        "BOOL-001": [],       # Uses Boolean algebra
        "INT-001": [],        # Uses integer arithmetic (must be emulated)
        "RING-001": [],       # Uses ring operations
        "TENSOR-001": [],     # Generates tensors
        "POLY-001": [],       # Uses polynomial activation
        "FRACTAL-001": [],    # Uses fractal expansion
        "TOPO-001": [],       # Uses topological collapse
        "CRYPTO-001": [],     # Uses cryptographic hashing
        "PROP-001": [],       # Uses propositional logic tests
        "CONSTRUCT-001": [],  # Uses constructive proofs
        "LAMBDA-001": [],     # Uses UVM/lambda calculus
        "unclassified": [],    # Requires manual review
        "exempt": [],         # Foundation files
    }
    
    for py_file in repo_root.rglob("*.py"):
        rel_path = str(py_file.relative_to(repo_root))
        
        # Skip exempt files
        if any(exempt in rel_path for exempt in EXEMPT_FILES):
            inventory["exempt"].append(rel_path)
            continue
        
        content = py_file.read_text()
        
        # PEANO-001: successor/predecessor
        if re.search(r'\bsuccessor\(|\bpredecessor\(', content):
            inventory["PEANO-001"].append(rel_path)
        
        # BOOL-001: Boolean algebra
        elif re.search(r'\bbool_and\(|\bbool_or\(|\bbool_not\(', content):
            inventory["BOOL-001"].append(rel_path)
        
        # INT-001: Integer arithmetic (check for raw ops)
        elif _has_raw_arithmetic(content):
            inventory["INT-001"].append(rel_path)
        
        # TENSOR-001: tensor generation
        elif "generate_tensor" in content:
            inventory["TENSOR-001"].append(rel_path)
        
        # POLY-001: polynomial activation
        elif "polynomial_activation" in content:
            inventory["POLY-001"].append(rel_path)
        
        # FRACTAL-001: fractal expansion
        elif "fractal_expand" in content:
            inventory["FRACTAL-001"].append(rel_path)
        
        # TOPO-001: topological collapse
        elif "topological_collapse" in content:
            inventory["TOPO-001"].append(rel_path)
        
        # CRYPTO-001: cryptographic hashing
        elif "sha256" in content or "hashlib" in content:
            inventory["CRYPTO-001"].append(rel_path)
        
        # LAMBDA-001: UVM/lambda calculus
        elif "UVM" in content or "execute(" in content:
            inventory["LAMBDA-001"].append(rel_path)
        
        # PROP-001/CONSTRUCT-001: test files with falsifiable structure
        elif rel_path.startswith("tests/") and "test_" in rel_path:
            inventory["PROP-001"].append(rel_path)
            inventory["CONSTRUCT-001"].append(rel_path)
        
        else:
            inventory["unclassified"].append(rel_path)
    
    return inventory

def _has_raw_arithmetic(content: str) -> bool:
    """Check for raw arithmetic operators outside comments/strings."""
    # Remove comments
    lines = content.split("\n")
    for line in lines:
        code = line.split("#")[0]
        # Check for operators not in string literals
        if '"' not in code and "'" not in code:
            if re.search(r'(?<!\w)[+\-*](?!\w)', code):
                return True
    return False

def main():
    """Generate inventory and save to JSON."""
    repo_root = Path(__file__).parent.parent
    inventory = inventory_repository(repo_root)
    
    output_path = repo_root / "ontology" / "pr29_file_inventory.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
    
    print(f"Inventory complete: {sum(len(v) for v in inventory.values())} files categorized")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
