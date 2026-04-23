#!/usr/bin/env python3
"""
falsifies_if: refactored domain still contains bare assert or AssertionError.

tools/refactor_assertions.py — Batch refactor AssertionError domains to ProofObject

Converts domains using assert/AssertionError pattern to ProofObject returns.
Pattern: assert X → if not X: return False, ProofObject(...)

Usage:
    python tools/refactor_assertions.py --dry-run   # Preview changes
    python tools/refactor_assertions.py              # Apply changes
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

REPO_ROOT = Path(__file__).parent.parent


def find_assertion_domains() -> List[Tuple[Path, int]]:
    """Find all domains using AssertionError/assert pattern."""
    domains = []
    domains_dir = REPO_ROOT / "src" / "domains"
    
    for d in domains_dir.iterdir():
        if not d.is_dir() or not d.name.startswith("d_"):
            continue
        inv_file = d / "invariants.py"
        if not inv_file.exists():
            continue
        
        content = inv_file.read_text()
        has_assert = "AssertionError" in content or re.search(r'\bassert\s+', content)
        has_proof = "ProofObject" in content
        
        if has_assert and not has_proof:
            lines = len(content.split("\n"))
            domains.append((inv_file, lines))
    
    return sorted(domains, key=lambda x: x[1])


def refactor_file(filepath: Path, dry_run: bool = False) -> Dict:
    """Refactor a single invariants.py file."""
    content = filepath.read_text()
    original_content = content
    
    changes = {
        "file": str(filepath),
        "assertions_replaced": 0,
        "imports_added": [],
        "functions_converted": 0,
    }
    
    # Check if already has ProofObject
    if "ProofObject" in content and "from axioms.logic import ProofObject" in content:
        return {**changes, "skipped": "Already has ProofObject"}
    
    # Add imports if missing
    if "from typing import Tuple" not in content:
        # Add after existing imports
        import_lines = list(re.finditer(r'^(from .+ import .+|import .+)$', content, re.MULTILINE))
        if import_lines:
            last_import = import_lines[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + "\nfrom typing import Tuple" + content[insert_pos:]
            changes["imports_added"].append("from typing import Tuple")
    
    if "from axioms.logic import ProofObject" not in content:
        # Find a good place to add
        if "from axioms" in content:
            # Add after existing axioms imports
            content = re.sub(
                r'(from axioms\.\S+ import [^\n]+)',
                r'\1\nfrom axioms.logic import ProofObject',
                content
            )
        else:
            # Add after first import block
            lines = content.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    import_idx = i + 1
            lines.insert(import_idx, "from axioms.logic import ProofObject")
            content = "\n".join(lines)
        changes["imports_added"].append("from axioms.logic import ProofObject")
    
    # Replace simple assert statements
    # Pattern: assert condition
    assert_pattern = r'^(\s+)assert\s+(.+?)(?:\s*#.*)?$'
    
    def replace_assert(match):
        indent = match.group(1)
        condition = match.group(2).strip()
        changes["assertions_replaced"] += 1
        
        # Generate a proof conclusion from the condition
        if len(condition) > 50:
            conclusion = f"Assertion failed: {condition[:47]}..."
        else:
            conclusion = f"Assertion failed: {condition}"
        
        return f'''{indent}if not ({condition}):
{indent}    return False, ProofObject(
{indent}        rule="assertion_check",
{indent}        premises=[f"Condition: {repr(condition)[:80]}"],
{indent}        conclusion="{conclusion}"
{indent}    )'''
    
    content = re.sub(assert_pattern, replace_assert, content, flags=re.MULTILINE)
    
    # Handle assert not pattern
    assert_not_pattern = r'^(\s+)assert\s+not\s+(.+?)(?:\s*#.*)?$'
    
    def replace_assert_not(match):
        indent = match.group(1)
        condition = match.group(2).strip()
        changes["assertions_replaced"] += 1
        
        return f'''{indent}if {condition}:
{indent}    return False, ProofObject(
{indent}        rule="assertion_check",
{indent}        premises=["Condition should be false"],
{indent}        conclusion="VIOLATION: Expected false condition was true"
{indent}    )'''
    
    content = re.sub(assert_not_pattern, replace_assert_not, content, flags=re.MULTILINE)
    
    # Update function return type annotations
    # Pattern: def check_*() -> bool:
    content = re.sub(
        r'(def check_\w+\([^)]*\))\s*->\s*bool:',
        r'\1 -> Tuple[bool, ProofObject]:',
        content
    )
    
    # Update return True statements to include ProofObject
    # Only in check_* functions
    return_pattern = r'^(\s+)return\s+True\s*$'
    
    def replace_return_true(match):
        indent = match.group(1)
        return f'''{indent}return True, ProofObject(
{indent}    rule="check_passed",
{indent}    premises=["All assertions passed"],
{indent}    conclusion="Invariant check satisfied"
{indent})'''
    
    content = re.sub(return_pattern, replace_return_true, content, flags=re.MULTILINE)
    
    # Count functions
    changes["functions_converted"] = len(re.findall(r'def check_\w+', content))
    
    if content != original_content:
        if not dry_run:
            filepath.write_text(content)
            changes["written"] = True
        else:
            changes["would_write"] = True
    
    return changes


def main():
    parser = argparse.ArgumentParser(description="Refactor AssertionError domains to ProofObject")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    args = parser.parse_args()
    
    domains = find_assertion_domains()
    print(f"Found {len(domains)} domains using AssertionError/assert pattern:")
    for filepath, lines in domains:
        print(f"  {filepath.parent.name}: {lines} lines")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE — No changes will be made")
        print()
    
    results = []
    for filepath, lines in domains:
        print(f"Processing {filepath.parent.name}...", end=" ")
        result = refactor_file(filepath, dry_run=args.dry_run)
        
        if "skipped" in result:
            print(f"SKIPPED: {result['skipped']}")
        elif result.get("would_write") or result.get("written"):
            print(f"OK (replaced {result['assertions_replaced']} assertions)")
        else:
            print("NO CHANGES")
        
        results.append(result)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_assertions = sum(r.get("assertions_replaced", 0) for r in results)
    total_functions = sum(r.get("functions_converted", 0) for r in results)
    files_changed = sum(1 for r in results if r.get("would_write") or r.get("written"))
    
    print(f"Domains processed: {len(domains)}")
    print(f"Assertions replaced: {total_assertions}")
    print(f"Functions converted: {total_functions}")
    print(f"Files {'that would be' if args.dry_run else ''} changed: {files_changed}")
    
    if args.dry_run:
        print()
        print("Run without --dry-run to apply changes.")
        return 0
    
    print()
    print("Changes applied successfully!")
    print("Next steps:")
    print("1. Spot-check 3 random domains")
    print("2. Run: python automation/pr49_guard.py")
    print("3. Update DOMAIN_INVARIANT_STATUS.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
