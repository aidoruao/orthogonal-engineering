# Automated Refactoring Guidelines for Autonomous Agents

**Safety Notice:** This document provides step-by-step guidance for automated agents to propose and validate mass refactors safely. All operations are DRY-RUN ONLY. No automatic merges, pushes, or network calls are permitted. Human approval is required for all changes.

## Overview

This guide provides concrete, actionable steps for an automated agent (IDE AI, CI/CD bot, code analysis tool) to safely propose, validate, and assist with mass refactors in the Orthogonal Engineering framework.

## Core Principles

1. **Deterministic Canonicalization**: All transformations must be reproducible
2. **Merkle Root Verification**: State integrity verified at each step
3. **Dry-Run First**: All changes tested in isolation before proposal
4. **Human-in-the-Loop**: No automatic merges without explicit approval
5. **Incremental Application**: Changes applied in small, reviewable batches
6. **Full Audit Trail**: Every operation logged for future analysis

## Step-by-Step Workflow

### Phase 1: Pattern Detection and Analysis

#### Step 1.1: Ingest Audit Logs

**Purpose**: Load and parse JSONL audit logs from deterministic pipeline

**Commands**:
```bash
# Read hello_world_handling_pipeline.jsonl
cat hello_world_handling_pipeline.jsonl | jq -c '.'

# Read handling_verification_pipeline.jsonl  
cat handling_verification_pipeline.jsonl | jq -c '.'
```

**Expected Output**: Stream of JSON objects representing pipeline steps

**Validation**: Verify JSONL is well-formed (each line is valid JSON)

#### Step 1.2: Analyze Parameter Change Patterns

**Purpose**: Identify recurring parameter co-variations

**Process**:
```python
# DRY-RUN ONLY - No file modifications
import json
from collections import defaultdict

def analyze_parameter_patterns(jsonl_path):
    """Analyze JSONL logs for parameter change patterns (read-only)."""
    param_changes = defaultdict(list)
    
    with open(jsonl_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('step') == 'transformation':
                param = entry.get('input_param')
                context = entry.get('context')
                param_changes[context].append(param)
    
    # Find co-occurring parameters
    covariation = defaultdict(int)
    for context, params in param_changes.items():
        for i, p1 in enumerate(params):
            for p2 in params[i+1:]:
                pair = tuple(sorted([p1, p2]))
                covariation[pair] += 1
    
    return covariation

# Example usage (read-only)
patterns = analyze_parameter_patterns('hello_world_handling_pipeline.jsonl')
print(f"Detected patterns: {patterns}")
```

**Output**: Dictionary of parameter pairs and occurrence counts

**Safety Check**: Verify script only reads files, does not write anything

#### Step 1.3: Generate Candidate Transformations

**Purpose**: Create potential refactor proposals based on detected patterns

**Process**:
```python
# DRY-RUN ONLY - Output to /tmp, not repository
def generate_candidate_transformations(patterns, threshold=10):
    """Generate refactor candidates (output to /tmp only)."""
    candidates = []
    
    for (param1, param2), count in patterns.items():
        if count >= threshold:
            candidates.append({
                'type': 'parameter_covariation',
                'params': [param1, param2],
                'occurrences': count,
                'confidence': count / sum(patterns.values()),
                'suggested_action': f'Review all changes to {param1} and ensure {param2} is also updated'
            })
    
    # Write to /tmp, NOT to repository
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', dir='/tmp') as f:
        json.dump(candidates, f, indent=2)
        print(f"Candidates written to: {f.name}")
        return f.name

# Example usage
candidate_file = generate_candidate_transformations(patterns)
```

**Output**: JSON file in /tmp containing candidate transformations

**Safety Check**: Verify output written to /tmp only, not to repository

### Phase 2: Dry-Run Validation

#### Step 2.1: Create Isolated Test Branch

**Purpose**: Validate transformations without affecting main codebase

**Commands**:
```bash
# Create test branch (local only, no push)
git checkout -b refactor/test-$(date +%s)

# Verify we're on test branch
git branch --show-current
```

**Safety Check**: Verify branch name contains "test" or "refactor"

#### Step 2.2: Apply Candidate Transformations

**Purpose**: Apply proposed changes to test branch

**Commands**:
```bash
# Example: Apply transformation via sed (DRY-RUN FIRST)
# Dry-run: show what would change
sed -n 's/old_pattern/new_pattern/p' target_file.py

# If dry-run looks correct, apply to test branch
sed -i 's/old_pattern/new_pattern/' target_file.py
```

**Safety Check**: 
- Always run dry-run (no `-i` flag) first
- Review diff before committing: `git diff`
- Verify only expected files changed

#### Step 2.3: Compute Merkle Root (Before)

**Purpose**: Capture baseline state for reproducibility verification

**Commands**:
```bash
# Compute hash of all tracked files (deterministic order)
git ls-files | sort | xargs sha256sum | sha256sum | awk '{print $1}' > /tmp/merkle_root_before.txt

# Display baseline Merkle root
cat /tmp/merkle_root_before.txt
```

**Output**: SHA-256 hash representing entire codebase state

**Safety Check**: Store in /tmp, not repository

#### Step 2.4: Run Unit Tests

**Purpose**: Verify transformations don't break functionality

**Commands**:
```bash
# Run existing test suite (if available)
pytest tests/ || echo "Tests not available or failed"

# Run build (if applicable)
make build || echo "Build not available or failed"

# Run linters (if applicable)
pylint src/ || echo "Linter not available or failed"
```

**Expected Output**: All tests pass, build succeeds, linters happy

**Failure Handling**: If tests fail, document failures and rollback:
```bash
git checkout -- .
git checkout main
git branch -D refactor/test-*
```

#### Step 2.5: Compute Merkle Root (After)

**Purpose**: Verify only expected files changed

**Commands**:
```bash
# Compute hash after transformations
git ls-files | sort | xargs sha256sum | sha256sum | awk '{print $1}' > /tmp/merkle_root_after.txt

# Compare before/after
echo "Before: $(cat /tmp/merkle_root_before.txt)"
echo "After:  $(cat /tmp/merkle_root_after.txt)"

# Show diff
git diff --stat main
```

**Validation**: 
- Merkle roots should differ (changes were made)
- Diff should match expected transformation scope
- No unexpected files modified

#### Step 2.6: Generate Reproducibility Report

**Purpose**: Document exact transformation steps for audit trail

**Process**:
```bash
# Create reproducibility report in /tmp
cat > /tmp/refactor_reproducibility_report.json <<EOF
{
  "transformation_id": "$(date +%s)",
  "merkle_root_before": "$(cat /tmp/merkle_root_before.txt)",
  "merkle_root_after": "$(cat /tmp/merkle_root_after.txt)",
  "files_changed": $(git diff --name-only main | jq -R -s -c 'split("\n")[:-1]'),
  "test_status": "$(pytest tests/ > /dev/null 2>&1 && echo 'passed' || echo 'failed')",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

cat /tmp/refactor_reproducibility_report.json
```

**Output**: JSON report in /tmp documenting transformation

**Safety Check**: Report written to /tmp only

### Phase 3: Human Review and Approval

#### Step 3.1: Create Review Patch

**Purpose**: Generate reviewable artifact for human inspection

**Commands**:
```bash
# Create patch file in /tmp
git diff main > /tmp/refactor_proposal.patch

# Display patch summary
echo "Patch summary:"
git diff --stat main

# Show first 50 lines of patch
head -50 /tmp/refactor_proposal.patch
```

**Output**: Patch file showing exact changes

**Safety Check**: Patch written to /tmp only

#### Step 3.2: Generate Review Checklist

**Purpose**: Provide structured review criteria for human approver

**Template**:
```markdown
# Refactor Review Checklist

## Transformation Details
- [ ] Transformation ID: <generated_id>
- [ ] Pattern detected: <parameter_covariation | other>
- [ ] Files affected: <count>
- [ ] Lines changed: <count>

## Validation Results
- [ ] Unit tests: PASSED / FAILED
- [ ] Build: SUCCESS / FAILED  
- [ ] Linters: PASSED / FAILED
- [ ] Merkle root before: <hash>
- [ ] Merkle root after: <hash>

## Safety Checks
- [ ] Only expected files modified
- [ ] No secrets or credentials in diff
- [ ] No network calls introduced
- [ ] No auto-merge logic added
- [ ] All changes are deterministic

## Review Decision
- [ ] APPROVED - Apply transformation
- [ ] REJECTED - Do not apply, provide feedback
- [ ] NEEDS_CHANGES - Revise and resubmit

Reviewer: _______________
Date: _______________
```

**Output**: Markdown checklist in /tmp

**Usage**: Human reviewer fills out checklist before approval

#### Step 3.3: Await Human Approval

**Purpose**: Require explicit sign-off before applying changes

**Process**:
```bash
# Human reviews:
# 1. Patch file: /tmp/refactor_proposal.patch
# 2. Reproducibility report: /tmp/refactor_reproducibility_report.json
# 3. Review checklist

# Human provides decision:
# - APPROVED: Proceed to Phase 4
# - REJECTED: Rollback and exit
# - NEEDS_CHANGES: Return to Phase 1 with feedback
```

**Safety Gate**: Script pauses here until human input received

**Minimal Approval Policy**:
```yaml
approval_policy:
  required_reviewers: 1
  required_checks:
    - unit_tests_passed
    - build_succeeded
    - no_unexpected_files
    - merkle_roots_differ
  override_allowed: false
  emergency_rollback: true
```

### Phase 4: Incremental Application (If Approved)

#### Step 4.1: Create Patch Branch

**Purpose**: Apply changes on a feature branch, not directly to main

**Commands**:
```bash
# Create feature branch from main
git checkout main
git checkout -b feature/refactor-$(date +%s)

# Apply patch
git apply /tmp/refactor_proposal.patch

# Commit with descriptive message
git add -A
git commit -m "Apply automated refactor: <pattern_name>

Transformation ID: <id>
Merkle root before: <hash>
Merkle root after: <hash>
Files changed: <count>
Tests: PASSED"
```

**Safety Check**: Never push without explicit human command

#### Step 4.2: Final Verification

**Purpose**: Verify transformations still work after rebasing on latest main

**Commands**:
```bash
# Ensure main is up-to-date (local only, no fetch)
git checkout main
git log -1

# Rebase feature branch (resolve conflicts if any)
git checkout feature/refactor-*
git rebase main

# Re-run tests
pytest tests/

# Re-compute Merkle root
git ls-files | sort | xargs sha256sum | sha256sum | awk '{print $1}' > /tmp/merkle_root_final.txt
```

**Expected Output**: Tests pass, Merkle root matches expectations

#### Step 4.3: Human-Controlled Merge

**Purpose**: Human performs actual merge to main

**Process**:
```bash
# Human reviews final state
git diff main

# Human decides to merge (manual command)
git checkout main
git merge --no-ff feature/refactor-*

# Human verifies merge
git log -1
```

**Safety Check**: Agent does NOT execute merge. Human must type command manually.

## Example Commands Reference

### Dry-Run Validation
```bash
# Show what sed would change (dry-run)
sed -n 's/old/new/p' file.py

# Show what git would commit (dry-run)
git diff --cached

# Show what patch would apply (dry-run)
git apply --check /tmp/patch.diff
```

### Rollback Commands
```bash
# Discard all uncommitted changes
git checkout -- .

# Delete test branch
git branch -D refactor/test-*

# Return to main
git checkout main
```

### Audit Trail Commands
```bash
# Log all operations to JSONL (append-only)
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"operation\":\"refactor_proposed\",\"status\":\"pending_review\"}" >> /tmp/refactor_audit.jsonl
```

## Safety Constraints Summary

1. **No Auto-Merge**: Agents propose, humans approve
2. **No Auto-Push**: All changes remain local until human pushes
3. **No Network Calls**: All operations local and deterministic
4. **No Repository Writes (Until Approved)**: Dry-run outputs to /tmp
5. **Full Rollback**: Any step can be undone completely

## Error Handling

### Test Failures
```bash
if ! pytest tests/; then
    echo "Tests failed. Rolling back."
    git checkout -- .
    exit 1
fi
```

### Unexpected File Changes
```bash
EXPECTED_FILES="src/main.py src/utils.py"
ACTUAL_FILES=$(git diff --name-only main)

if [ "$ACTUAL_FILES" != "$EXPECTED_FILES" ]; then
    echo "Unexpected files changed. Rolling back."
    git checkout -- .
    exit 1
fi
```

### Merkle Root Mismatch
```bash
if [ "$(cat /tmp/merkle_root_before.txt)" == "$(cat /tmp/merkle_root_after.txt)" ]; then
    echo "No changes detected. Aborting."
    exit 1
fi
```

## Conclusion

Following these guidelines ensures that automated refactoring remains:
- **Safe**: Human approval required at all critical steps
- **Auditable**: Full trail of transformations logged
- **Reproducible**: Merkle roots verify deterministic outcomes
- **Reversible**: Any step can be undone

Autonomous agents enhance developer productivity while maintaining strict safety and control standards. The human remains in charge of all merges and deployments.
