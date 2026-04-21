---
tags: [yeshua-mathematics-implementation-guide]
register: documentation
---

# Yeshua Mathematics Implementation Guide

## Overview

Yeshua Mathematics is a formal system for building transparent, verifiable, and falsifiable mathematical software. It enforces eight core axioms through automated verification, domain mapping, and cryptographic proof chains.

## Quick Start

### 1. Initialize the System

```bash
# Generate initial inventory of all Python files
python inventory/repository_inventory.py

# Run end-to-end verification
python generators/verify_all.py
```

### 2. Fix Common Issues

If verification fails, you'll see violations like:
- **Axiom 7 violations**: Files containing monetization keywords (paywall, subscription, etc.)
- **Unclassified files**: Files not mapped to any Yeshua domain
- **Hash mismatches**: Files that have changed since inventory

### 3. Enable Zed IDE Integration

The `.zed/hooks/on_save.py` hook automatically runs Yeshua verification when files are saved in Zed. Ensure Zed is configured to use Python hooks.

### 4. Fix Windows Execution Policy (for GitHub Actions)

```powershell
# Run as Administrator
.\scripts\fix_windows_execution_policy.ps1
```

## Core Components

### 1. Repository Inventory (`inventory/repository_inventory.py`)

**Purpose**: Maps every Python file to Yeshua domains based on content analysis.

**Key Features**:
- SHA-256 hashing of all files
- Domain detection using regex patterns
- Merkle root computation for integrity verification
- Exempts foundation files from self-audit

**Domains Detected**:
- **PEANO-001**: Peano Arithmetic (successor, predecessor, peano_add, peano_mul)
- **BOOL-001**: Boolean Algebra (bool_and, bool_or, bool_not, bool_xor)
- **CRYPTO-001**: SHA-256 and cryptographic functions
- **MERKLE-001**: Merkle Trees and hash chains
- **AXIOM-001**: Axiomatic foundations
- ... and 34 more domains (see `yeshua/domains/39_domain_table.json`)

### 2. Eight Axioms (`yeshua/axioms/eight_axioms.json`)

The foundational principles of Yeshua Mathematics:

1. **Every truth is derivable from axioms**
2. **Every derivation is reproducible**
3. **Every mutation is re-verifiable**
4. **No authority without proof**
5. **No hidden state**
6. **No unverifiable dependency**
7. **No economic gatekeeping** (blocks paywall, subscription, proprietary, paid, license fee)
8. **Every artifact is hash-anchored**

### 3. Domain Table (`yeshua/domains/39_domain_table.json`)

39 mathematical domains categorized as:
- **Foundational**: Peano Arithmetic, Boolean Algebra, Set Theory
- **Applied**: Modular Arithmetic, Binary Representation, Cryptographic Hash Functions
- **Cryptography**: SHA-256, Hash Chains, Inclusion Proofs
- **CS Theory**: Instruction Set Architecture, Finite State Machines
- **Hardware Abstraction**: Bit Manipulation, Endianness, Word-Size Arithmetic
- **Data Structures**: Binary Trees, Directed Acyclic Graphs
- **Verification**: Mathematical Induction, Invariant Preservation, Falsification
- **Philosophy**: Ontological Foundations, Correspondence Theory of Truth

### 4. Verification System (`generators/verify_all.py`)

**Comprehensive checks**:
- Axiom compliance (especially Axiom 7: no economic gatekeeping)
- File hash integrity
- Domain coverage analysis
- Merkle root validation
- Inventory consistency

### 5. Zed IDE Integration (`.zed/hooks/on_save.py`)

**Real-time verification**:
- Runs on every file save
- Shows domain mappings
- Warns about unclassified files
- Maintains boundary awareness

### 6. Windows PowerShell Fix (`scripts/fix_windows_execution_policy.ps1`)

**For GitHub Self-Hosted Runners**:
- Fixes "cannot be loaded because running scripts is disabled" error
- Sets execution policy to RemoteSigned
- Tests runner script functionality

### 7. Game Grace Proof (`researches/game_grace_proof/implementation.py`)

**Example Application**: Deterministic loot grace layer for games
- Peano-based run counter
- Cryptographic proof chains
- Merkle root verification
- Threshold-based item claims

## Usage Examples

### Basic Verification

```python
from generators.verify_all import YeshuaVerifier
from pathlib import Path

verifier = YeshuaVerifier(Path.cwd())
success = verifier.run()
print(f"Verification {'passed' if success else 'failed'}")
```

### Domain Analysis

```python
from inventory.repository_inventory import inventory_repository
import json

inventory = inventory_repository(Path.cwd())
print(f"Files: {len(inventory['files'])}")
print(f"Domains in use: {len([d for d in inventory['domains'] if inventory['domains'][d]])}")

# Check specific file
file_info = inventory['files']['path/to/your/file.py']
print(f"Domains: {file_info['domains']}")
print(f"Hash: {file_info['hash']}")
```

### Game Grace Proof

```python
from researches.game_grace_proof.implementation import PlayerRunCounter

# Track player runs
player = PlayerRunCounter("player_12345")
for i in range(52):
    result = player.record_run("deadmines", "van_cleef")
    
# Check eligibility
if player.can_claim_item(50):
    print(f"Player can claim item after {player.run_count} runs")
    print(f"Proof chain root: {player.get_proof_chain_hash()}")
```

## Integration with Existing Workflows

### GitHub Actions

Add to your workflow files:

```yaml
- name: Verify Yeshua Mathematics Compliance
  run: python generators/verify_all.py
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: yeshua-verification
        name: Yeshua Mathematics Verification
        entry: python generators/verify_all.py
        language: system
        pass_filenames: false
        always_run: true
```

### Continuous Integration

```bash
# Add to CI pipeline
python inventory/repository_inventory.py
python generators/verify_all.py

# Exit with error code on violation
if [ $? -ne 0 ]; then
    echo "Yeshua verification failed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

1. **"Unclassified files" warning**
   - Files don't match any domain signature patterns
   - Add appropriate patterns to `DOMAIN_SIGNATURES` in `repository_inventory.py`
   - Or add file to `EXEMPT_FILES` if it's a foundation file

2. **Axiom 7 violations**
   - Files contain monetization keywords
   - Remove or replace: paywall, subscription, proprietary, paid, license fee
   - Use alternative terms: open, free, accessible, transparent

3. **Hash mismatches**
   - Files changed after inventory was generated
   - Run `python inventory/repository_inventory.py` to update inventory
   - Or fix the file to match original hash

4. **Missing dependencies**
   - Ensure Python 3.7+ is installed
   - No external dependencies required beyond standard library

### Debug Mode

```bash
# Enable debug output
export ORTHOGONAL_GB_DEBUG=1
python generators/verify_all.py
```

## Extending the System

### Adding New Domains

1. Edit `inventory/repository_inventory.py`:
   ```python
   DOMAIN_SIGNATURES = {
       "NEW-001": [r"pattern1", r"pattern2"],
       # ... existing domains
   }
   ```

2. Update `yeshua/domains/39_domain_table.json`:
   ```json
   {
     "id": "NEW-001",
     "name": "New Domain Name",
     "category": "Category",
     "status": "SPECIFIED",
     "pr": 28
   }
   ```

### Custom Verification Rules

Extend `YeshuaVerifier` class:

```python
class CustomVerifier(YeshuaVerifier):
    def verify_custom_rule(self):
        """Add custom verification logic."""
        # Your verification code here
        pass
    
    def run(self):
        """Override run method to include custom verification."""
        super().run()
        self.verify_custom_rule()
        return len(self.violations) == 0
```

## Best Practices

### 1. Regular Verification
- Run verification before commits
- Integrate with CI/CD pipelines
- Monitor for new violations

### 2. Domain Mapping
- Ensure all production code is mapped to domains
- Keep domain signatures up to date
- Document domain usage in code comments

### 3. Cryptographic Integrity
- Never bypass hash verification
- Maintain Merkle root consistency
- Store proofs with artifacts

### 4. Economic Neutrality
- Avoid monetization keywords
- Use open, transparent terminology
- Document any necessary exceptions

## Performance Considerations

- **Inventory generation**: O(n) where n is number of Python files
- **Domain detection**: Regex patterns are compiled once
- **Hash computation**: Uses efficient SHA-256 with chunked reading
- **Memory usage**: Processes files sequentially, not all at once

For large repositories (>10,000 files), consider:
- Excluding test directories
- Using more specific include patterns
- Running verification in parallel

## License and Attribution

Yeshua Mathematics is part of the Orthogonal Engineering framework. All components are open source and transparent by design.

## Support

- **Issues**: Report via GitHub issues
- **Contributions**: Follow the eight axioms
- **Questions**: Reference this guide and the axiom files

---

*"We don't hide complexity—we make it inspectable. We don't suppress errors—we make them visible. We don't enforce belief—we enforce accountability."*