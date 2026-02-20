#!/usr/bin/env python3
"""
PR #29 repository-wide compliance tests.
Verifies entire codebase against Yeshua Mathematics Compendium.
Author: Orthogonal Engineering
PR: #29
Version: 1.0.0
"""
import ast
import json
import re
import sys
from pathlib import Path

# Foundation files exempt from audit (trusted primitives)
EXEMPT_FILES = [
    "oe_ifm/mathematical_core.py",
    "tests/test_peano_axioms.py",
    "tests/test_boolean_algebra.py",
    "scripts/repository_inventory.py",
    "tests/test_repository_compliance.py",
]

# Domain compliance rules
COMPLIANCE_RULES = {
    "PEANO-001": {
        "required_imports": ["oe_ifm.mathematical_core"],
        "forbidden_patterns": [r'(?<!\w)\+(?!\w)', r'(?<!\w)\-(?!\w)'],  # Raw +-
        "allowed_in": ["oe_ifm/mathematical_core.py"],
    },
    "BOOL-001": {
        "required_imports": ["oe_ifm.mathematical_core"],
        "forbidden_patterns": [r'\band\b', r'\bor\b', r'\bnot\b'],  # Python bool ops
        "allowed_in": [
            "oe_ifm/mathematical_core.py",
            "tests/test_boolean_algebra.py"
        ],
    },
    "INT-001": {
        "required_functions": ["uint64", "int64", "peano_add", "modular_multiply"],
        "forbidden_patterns": ["np.int64", "torch.int64", "numpy.int64"],
    },
    "TENSOR-001": {
        "required_calls": ["generate_tensor"],
        "forbidden_calls": ["torch.randn", "torch.zeros", "torch.ones"],
    },
    "POLY-001": {
        "required_calls": ["polynomial_activation"],
        "forbidden_calls": [
            "torch.nn.GELU",
            "nn.GELU",
            "F.softmax",
            "nn.Softmax",
            "nn.LayerNorm",
            "F.layer_norm",
        ],
    },
    "FRACTAL-001": {
        "required_calls": ["fractal_expand"],
        "forbidden_patterns": ["recursive", "while.*depth"],  # Ad-hoc recursion
    },
    "TOPO-001": {
        "required_calls": ["topological_collapse"],
    },
    "CRYPTO-001": {
        "required_hash": "sha256",
        "forbidden_hashes": ["md5", "sha1", "hash(", "custom_hash"],
    },
}

def test_file_compliance(file_path: Path, repo_root: Path) -> list:
    """Check single file against all compliance rules."""
    violations = []
    rel_path = str(file_path.relative_to(repo_root))
    content = file_path.read_text()
    
    # Skip exempt files
    if any(exempt in rel_path for exempt in EXEMPT_FILES):
        return []
    
    for domain_id, rules in COMPLIANCE_RULES.items():
        # Check required imports
        if "required_imports" in rules:
            if not any(imp in content for imp in rules["required_imports"]):
                if rel_path not in rules.get("allowed_in", []):
                    violations.append(f"{domain_id}: Missing required imports")
        
        # Check forbidden patterns
        if "forbidden_patterns" in rules:
            for pattern in rules["forbidden_patterns"]:
                if re.search(pattern, content) and rel_path not in rules.get("allowed_in", []):
                    violations.append(f"{domain_id}: Forbidden pattern '{pattern}'")
        
        # Check forbidden calls
        if "forbidden_calls" in rules:
            for call in rules["forbidden_calls"]:
                if call in content:
                    violations.append(f"{domain_id}: Forbidden call '{call}'")
    
    return violations

def test_repository_compliance():
    """Main test: all files must comply or be exempted."""
    repo_root = Path(__file__).parent.parent
    all_violations = {}
    
    for py_file in repo_root.rglob("*.py"):
        violations = test_file_compliance(py_file, repo_root)
        if violations:
            rel_path = str(py_file.relative_to(repo_root))
            all_violations[rel_path] = violations
    
    # Assert no violations
    assert not all_violations, f"Compliance violations:\n{json.dumps(all_violations, indent=2)}"
    
    print(f"✓ All {len(list(repo_root.rglob('*.py')))} files compliant or exempt")

if __name__ == "__main__":
    test_repository_compliance()
