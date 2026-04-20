---
tags: [docs, auto-refactor-guidelines]
register: documentation
---

# Automated Refactoring Guidelines for AI Agents

## Purpose

This document provides **step-by-step guidance** for automated agents performing mass refactors safely within the Orthogonal Engineering framework. These guidelines ensure reproducibility, auditability, and safety throughout the refactoring process.

---

## Core Principles

1. **Deterministic Canonicalization**: Every transformation must be reproducible
2. **Merkle-Verified Integrity**: All changes tracked with cryptographic proofs
3. **Dry-Run First**: Never modify production code without validation
4. **Human Review Gates**: Critical changes require explicit human approval
5. **Incremental Progress**: Large refactors executed in small, testable batches
6. **Full Audit Trail**: Every action logged in JSONL format
7. **Fail-Safe Rollback**: Always maintain ability to revert changes

---

## Step-by-Step Refactoring Process

### Phase 1: Discovery & Analysis

#### Step 1.1: Collect Audit Logs

```bash
# Gather all relevant JSONL logs
find . -name "*.jsonl" -type f > log_inventory.txt

# Aggregate logs for analysis
cat $(cat log_inventory.txt) > aggregated_logs.jsonl
```

**Requirements:**
- Logs must be complete and uncorrupted
- Timestamp ordering must be preserved
- No duplicate entries

#### Step 1.2: Pattern Discovery

```python
# Use log_analysis_example.py as template
import json

patterns = {}
for line in open('aggregated_logs.jsonl'):
    entry = json.loads(line)
    # Extract parameter change patterns
    # Compute correlations
    # Identify recurring transformations
```

**Discovery Criteria:**
- Correlation coefficient ≥ 0.85 for parameter relationships
- Pattern appears in ≥10 independent instances
- Statistical significance p-value < 0.01

#### Step 1.3: Generate Transformation Candidates

For each discovered pattern:
1. Define transformation rule in formal syntax
2. Specify preconditions and postconditions
3. Identify affected files and functions
4. Estimate impact scope (files, lines, functions)
5. Classify risk level (low/medium/high)

**Output:** Transformation specification document in JSON

```json
{
  "transformation_id": "T001_mass_to_inertia_adjustment",
  "pattern": "fMass_to_fDriveInertia",
  "rule": "fDriveInertia = fMass * 1.2",
  "correlation": 0.94,
  "instances_found": 47,
  "risk_level": "medium",
  "affected_files": 12,
  "estimated_changes": 47
}
```

---

### Phase 2: Validation & Dry-Run

#### Step 2.1: Create Isolated Test Environment

```bash
# Create temporary branch for dry-run
git checkout -b dryrun/T001_$(date +%Y%m%d_%H%M%S)

# Create isolated working directory
mkdir -p /tmp/refactor_dryrun/T001
cp -r <affected_files> /tmp/refactor_dryrun/T001/
```

**Isolation Requirements:**
- No network access during dry-run
- No modification of source repository
- All outputs written to /tmp

#### Step 2.2: Apply Transformation to Small Subset

```python
# Select representative sample (10% of total, minimum 5 files)
sample_size = max(5, int(0.1 * total_affected_files))
sample_files = random.sample(affected_files, sample_size)

# Apply transformation
for file in sample_files:
    apply_transformation(file, transformation_rule)
    compute_merkle_root(file)
```

**Validation Checks:**
- Syntax validity (AST parsing succeeds)
- No unintended changes to unrelated code
- Formatting preserved (unless reformatting is part of transformation)
- Comments and docstrings preserved

#### Step 2.3: Generate Diffs and Merkle Roots

```bash
# For each modified file
for file in sample_files:
    # Generate unified diff
    diff -u original/$file modified/$file > diffs/$file.diff
    
    # Compute before/after Merkle roots
    sha256sum original/$file >> merkle_manifest_before.txt
    sha256sum modified/$file >> merkle_manifest_after.txt
done

# Compute overall Merkle root for transformation
python compute_merkle_tree.py merkle_manifest_after.txt > transformation_merkle_root.txt
```

**Required Artifacts:**
- Individual file diffs
- Before/after Merkle manifests
- Transformation-level Merkle root
- Inclusion proofs for each changed file

#### Step 2.4: Inclusion Proof Generation

```python
def generate_inclusion_proofs(merkle_tree, changed_files):
    """Generate cryptographic proof that each file is in the manifest."""
    proofs = {}
    for file in changed_files:
        # Get sibling hashes along path to root
        proof_path = merkle_tree.get_proof_path(file)
        proofs[file] = {
            "file_hash": merkle_tree.get_leaf_hash(file),
            "proof": proof_path,
            "merkle_root": merkle_tree.root_hash
        }
    return proofs

# Verify proofs
for file, proof in proofs.items():
    assert verify_inclusion_proof(proof), f"Invalid proof for {file}"
```

---

### Phase 3: Testing & Reproducibility

#### Step 3.1: Run Unit Tests on Dry-Run Changes

```bash
# Run full test suite on modified sample
cd /tmp/refactor_dryrun/T001
python -m pytest tests/ --verbose --tb=short

# Capture test results
python -m pytest tests/ --junitxml=test_results.xml
```

**Pass Criteria:**
- All existing tests must pass
- No new test failures introduced
- Test coverage maintained or improved
- No performance regressions >5%

#### Step 3.2: Reproducibility Verification

```bash
# Re-run transformation from same inputs
rm -rf /tmp/refactor_dryrun/T001_verify
mkdir -p /tmp/refactor_dryrun/T001_verify
cp -r <affected_files> /tmp/refactor_dryrun/T001_verify/

# Apply same transformation
python apply_transformation.py \
    --transformation T001 \
    --input /tmp/refactor_dryrun/T001_verify \
    --output /tmp/refactor_dryrun/T001_verify_output

# Verify bit-for-bit identical output
diff -r /tmp/refactor_dryrun/T001 /tmp/refactor_dryrun/T001_verify_output
if [ $? -eq 0 ]; then
    echo "✅ Reproducibility verified: bit-for-bit identical"
else
    echo "❌ Reproducibility FAILED: outputs differ"
    exit 1
fi
```

**Reproducibility Requirements:**
- Identical transformation outputs from identical inputs
- Merkle roots must match exactly
- Timestamps excluded from comparison (logged separately)

#### Step 3.3: Generate Audit Log Entry

```python
import json
import datetime

audit_entry = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "transformation_id": "T001",
    "phase": "dry_run_validation",
    "status": "success",
    "files_modified": len(sample_files),
    "tests_passed": test_results["passed"],
    "tests_failed": test_results["failed"],
    "merkle_root_before": merkle_before,
    "merkle_root_after": merkle_after,
    "reproducibility": "verified",
    "actor": "autonomous_refactor_agent_v1.0",
    "review_required": True
}

# Append to audit log (JSONL format)
with open('refactor_audit.jsonl', 'a') as f:
    f.write(json.dumps(audit_entry) + '\n')
```

---

### Phase 4: Staging & Approval

#### Step 4.1: Create Patch Branch

```bash
# Create branch for actual changes (not dry-run)
git checkout -b feature/T001_mass_to_inertia_adjustment

# Document the transformation
cat > TRANSFORMATION_T001.md << EOF
# Transformation T001: Mass to Inertia Adjustment

## Summary
Auto-adjust fDriveInertia when fMass changes based on discovered correlation (r=0.94)

## Scope
- Files affected: 12
- Changes: 47 instances
- Risk level: Medium

## Validation Results
- Dry-run: ✅ Success
- Tests: ✅ All passed
- Reproducibility: ✅ Verified

## Review Required
This transformation requires human review before merge.
EOF
```

#### Step 4.2: Generate Review Package

```bash
# Create comprehensive review package
mkdir -p review_package/T001
cp diffs/*.diff review_package/T001/
cp test_results.xml review_package/T001/
cp merkle_manifest_*.txt review_package/T001/
cp refactor_audit.jsonl review_package/T001/
cp TRANSFORMATION_T001.md review_package/T001/

# Generate summary report
python generate_review_summary.py \
    --transformation T001 \
    --output review_package/T001/REVIEW_SUMMARY.md
```

**Review Package Contents:**
- Transformation specification
- All file diffs
- Test results
- Merkle manifests and proofs
- Audit log entries
- Statistical analysis of pattern
- Rollback plan

#### Step 4.3: Submit for Human Review

```python
def request_human_review(transformation_id, review_package):
    """Submit transformation for human approval."""
    
    # Create GitHub issue or PR with review request
    review_request = {
        "title": f"[AUTO-REFACTOR] Review Request: {transformation_id}",
        "type": "human_review_required",
        "transformation_id": transformation_id,
        "risk_level": transformation["risk_level"],
        "scope": {
            "files": transformation["affected_files"],
            "changes": transformation["estimated_changes"]
        },
        "validation_status": "dry_run_passed",
        "review_package_path": f"review_package/{transformation_id}/",
        "approval_required_by": datetime.datetime.now() + datetime.timedelta(days=2)
    }
    
    # Wait for approval
    return await_approval(review_request)
```

**Approval Criteria:**
- Medium risk: Senior developer approval
- High risk: Security team + architect approval
- Low risk: Automated approval after 24h if tests pass

---

### Phase 5: Execution & Monitoring

#### Step 5.1: Execute Transformation (if approved)

```bash
# Apply transformation to full set of affected files
python apply_transformation.py \
    --transformation T001 \
    --input <repository_root> \
    --mode production \
    --log refactor_production.jsonl

# Verify all changes
git diff --stat
git diff > T001_full_diff.patch
```

#### Step 5.2: Incremental Testing & Commits

For large refactors (>20 files), use batched approach:

```python
# Split files into batches of 10-20
batch_size = 15
file_batches = [affected_files[i:i+batch_size] 
                for i in range(0, len(affected_files), batch_size)]

for batch_num, batch in enumerate(file_batches):
    print(f"Processing batch {batch_num+1}/{len(file_batches)}")
    
    # Apply transformation to batch
    for file in batch:
        apply_transformation(file, transformation_rule)
    
    # Run tests on current state
    run_tests()
    
    # Commit batch if tests pass
    git_add(batch)
    git_commit(f"refactor(T001): Batch {batch_num+1}/{len(file_batches)}")
    
    # Compute checkpoint
    checkpoint_merkle = compute_merkle_root(repository)
    save_checkpoint(batch_num, checkpoint_merkle)
```

**Checkpoint Requirements:**
- Save Merkle root after each batch
- Enable rollback to any batch
- Log checkpoint in audit trail

#### Step 5.3: Final Validation

```bash
# Run full test suite on completed transformation
python -m pytest tests/ --verbose --cov

# Verify no unintended changes
git diff --name-only origin/main | grep -v <expected_files> && echo "ERROR: Unexpected files changed" || echo "OK"

# Compute final Merkle root
python compute_merkle_tree.py <repository_root> > final_merkle_root.txt

# Generate completion report
python generate_completion_report.py --transformation T001
```

---

### Phase 6: Documentation & Closure

#### Step 6.1: Update Documentation

```bash
# Update CHANGELOG
cat >> CHANGELOG.md << EOF
## [Unreleased]

### Changed (Automated Refactor T001)
- Adjusted fDriveInertia calculation to maintain consistent ratio with fMass (r=0.94)
- Affected 47 instances across 12 files
- Validated through dry-run and full test suite

EOF

# Update relevant documentation
# (if transformation changes public APIs or behavior)
```

#### Step 6.2: Generate Final Audit Entry

```python
final_audit = {
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "transformation_id": "T001",
    "phase": "completion",
    "status": "success",
    "files_modified": len(affected_files),
    "total_changes": total_changes,
    "batches_executed": len(file_batches),
    "tests_passed": final_test_results["passed"],
    "merkle_root_final": final_merkle_root,
    "human_approved_by": reviewer_username,
    "human_approved_at": approval_timestamp,
    "execution_time_seconds": execution_duration,
    "actor": "autonomous_refactor_agent_v1.0",
    "signed_by": agent_signature
}

with open('refactor_audit.jsonl', 'a') as f:
    f.write(json.dumps(final_audit) + '\n')
```

#### Step 6.3: Create Signed Patch

```bash
# Generate patch file
git format-patch origin/main --stdout > T001_signed.patch

# Sign patch with agent's cryptographic identity
gpg --detach-sign --armor T001_signed.patch

# Verify signature
gpg --verify T001_signed.patch.asc T001_signed.patch
```

---

## Rollback Procedures

### Immediate Rollback (During Execution)

```bash
# If any batch fails validation
git reset --hard <last_checkpoint_commit>

# Log rollback event
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"rollback","transformation":"T001","reason":"batch_validation_failed"}' >> refactor_audit.jsonl
```

### Post-Merge Rollback

```bash
# Revert entire transformation
git revert <merge_commit> --no-commit
git commit -m "Revert T001: [reason for rollback]"

# Verify rollback
git diff <pre_transformation_commit> HEAD | wc -l  # Should be 0

# Update audit log
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","event":"post_merge_rollback","transformation":"T001","reason":"production_issue_detected"}' >> refactor_audit.jsonl
```

---

## Safety Checklist

Before executing any automated refactor, verify:

- [ ] Pattern discovered with statistical significance (p < 0.01)
- [ ] Dry-run completed successfully on sample (≥10% of files)
- [ ] All unit tests pass on dry-run changes
- [ ] Reproducibility verified (bit-for-bit identical outputs)
- [ ] Merkle roots computed for before/after states
- [ ] Inclusion proofs generated for all changed files
- [ ] Audit log entries created for all phases
- [ ] Human review obtained (if risk level requires)
- [ ] Rollback plan documented and tested
- [ ] Checkpoints created for large refactors (>20 files)
- [ ] No network calls or external dependencies during transformation
- [ ] All changes are non-destructive and reversible
- [ ] Transformation does not modify configuration or secrets

---

## Risk Classification

### Low Risk (Automated Approval After Tests)
- Whitespace/formatting changes
- Comment updates
- Variable/function renames (with no API changes)
- Documentation updates

### Medium Risk (Senior Developer Approval)
- Logic refactoring maintaining equivalent behavior
- Parameter adjustments based on discovered patterns
- Deprecation migrations (non-security critical)
- Test additions/modifications

### High Risk (Security + Architecture Approval)
- Security-critical pattern changes (input validation, etc.)
- API contract modifications
- Database schema changes
- Authentication/authorization logic
- Cryptographic operations

---

## Agent Responsibilities

An automated refactoring agent MUST:

1. **Never modify production code without dry-run validation**
2. **Always generate complete audit trails**
3. **Halt on any validation failure and request human intervention**
4. **Maintain reproducibility (deterministic transformations only)**
5. **Respect review gates (no bypassing approval requirements)**
6. **Provide rollback capability at all stages**
7. **Log all actions in JSONL format**
8. **Generate Merkle proofs for all transformations**
9. **Operate in isolated environment (no network, no side effects)**
10. **Request clarification when pattern confidence < threshold**

An automated refactoring agent MUST NOT:

1. **Auto-merge without human approval**
2. **Modify files outside declared scope**
3. **Skip testing phases**
4. **Make non-deterministic transformations**
5. **Access network or external systems during transformation**
6. **Modify configuration, secrets, or credentials**
7. **Execute destructive operations (file deletion, etc.)**
8. **Bypass security checks or validation**
9. **Suppress errors or warnings**
10. **Claim certainty when statistical confidence is low**

---

## Example Transformation Scripts

### Minimal Transformation Script Template

```python
#!/usr/bin/env python3
"""
Transformation T001: Mass to Inertia Adjustment
Auto-adjusts fDriveInertia when fMass changes.
"""

import json
import hashlib
import datetime
import sys
from pathlib import Path

def apply_transformation(file_path, rule):
    """Apply transformation rule to a single file."""
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Apply transformation (example: regex-based)
    # In production, use AST parsing for safety
    transformed = apply_rule(content, rule)
    
    # Verify syntax
    try:
        compile(transformed, file_path, 'exec')
    except SyntaxError as e:
        raise ValueError(f"Transformation produced invalid syntax: {e}")
    
    return transformed

def compute_file_hash(content):
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def log_transformation(file_path, hash_before, hash_after):
    """Log transformation to audit trail."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "file": str(file_path),
        "hash_before": hash_before,
        "hash_after": hash_after,
        "transformation": "T001",
        "actor": "auto_refactor_agent"
    }
    with open('refactor_audit.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

def main():
    # Dry-run mode: don't modify actual files
    dry_run = '--dry-run' in sys.argv
    
    # Get files to transform
    files = get_affected_files()
    
    for file_path in files:
        # Read original content
        with open(file_path, 'r') as f:
            original = f.read()
        hash_before = compute_file_hash(original)
        
        # Apply transformation
        transformed = apply_transformation(file_path, transformation_rule)
        hash_after = compute_file_hash(transformed)
        
        # Log transformation
        log_transformation(file_path, hash_before, hash_after)
        
        if not dry_run:
            # Write transformed content
            with open(file_path, 'w') as f:
                f.write(transformed)
            print(f"✅ Transformed: {file_path}")
        else:
            print(f"🔍 [DRY-RUN] Would transform: {file_path}")

if __name__ == '__main__':
    main()
```

---

## Conclusion

Following these guidelines ensures that automated refactoring maintains the same level of safety, auditability, and reproducibility as manual refactoring, while enabling AI agents to operate at scale on repetitive transformation tasks.

**Key Takeaway**: Autonomous evolution is not about removing humans from the loop, but about enabling AI agents to handle well-defined, statistically validated transformations under human oversight, freeing developers to focus on creative and architectural work.

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-16  
**Status**: Guidelines for Autonomous Refactoring Agents  
**Review Cycle**: Quarterly
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
