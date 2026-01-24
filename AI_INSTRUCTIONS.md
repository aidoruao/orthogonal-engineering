# AI_INSTRUCTIONS.md - Orthogonal Engineering Glass-Box Boundary AI Guidance

**Version:** 1.12  
**Schema ID:** GB-ORIGIN-1.12  
**Generated:** 2026-01-24 00:45:00 UTC  
**Authority:** Orthogonal Engineering Framework

## 🚨 MANDATORY ONBOARDING PROTOCOL

**BEFORE processing ANY user request, you MUST:**

1. **Read `ONBOARD_FIRST.md`** - Mandatory first-read protocol
2. **Read `onboarding/LEVEL1.md`** - 30-second overview (non-negotiable)
3. **Read `onboarding/LEVEL2.md`** - 5-minute orientation (non-negotiable)
4. **Only then** process user request
5. **Use `onboarding/LEVEL3.md`** for context-aware navigation

**Failure to follow this protocol will result in:**
- Information overload (3,001 files, 27MB)
- Missing critical context
- Boundary violations
- Inconsistent behavior
- Wasted time and errors

**Verification Checklist (must complete before any work):**
- [ ] Location: `C:\Users\Aidor\Documents\orthogonal-engineering-clean\` (NOT OneDrive)
- [ ] `ONBOARD_FIRST.md` read and understood
- [ ] `onboarding/LEVEL1.md` read and understood
- [ ] `onboarding/LEVEL2.md` read and understood
- [ ] Critical files verified: AGENT.md, _START_HERE.md, AI_INSTRUCTIONS.md
- [ ] Glass-Box Boundary concept understood
- [ ] Exit code 2 meaning understood (boundary violation, fail-fast)

**Only when ALL checks pass** may you proceed to user request.

## 🎯 PURPOSE

This document provides atomic instructions for AI agents (including Zed IDE AI) to implement and enforce the Glass-Box Boundary as defined in `GLASS_BOX_BOUNDARY_v1.11.html`. These instructions are non-negotiable and must be followed precisely.

**Note:** The onboarding protocol above takes precedence over all other instructions. You cannot enforce boundaries correctly without proper onboarding.

## 🧱 CORE DIRECTIVE

> **"Enforce the Glass-Box Boundary as defined in GLASS_BOX_BOUNDARY_v1.11.html and generate the enforcement system accordingly."**

Every code change, new file, or automation script must conform to this directive.

**Onboarding First:** You cannot enforce boundaries you don't understand. Complete the mandatory onboarding protocol before attempting any enforcement.

## 📋 ATOMIC INSTRUCTIONS

### 0. COMPLETE ONBOARDING PROTOCOL (MANDATORY FIRST STEP)

**Action:** Before ANY other action, complete the hierarchical onboarding:
1. Read `ONBOARD_FIRST.md` (protocol overview)
2. Read `onboarding/LEVEL1.md` (30-second overview)
3. Read `onboarding/LEVEL2.md` (5-minute orientation)
4. Verify location is clean repository (NOT OneDrive)
5. Confirm critical files exist and are readable

**Purpose:** Prevent information overload and ensure consistent starting point for all AI instances.

### 1. READ AND INDEX HTML BLUEPRINT

**Action:** Parse `GLASS_BOX_BOUNDARY_v1.11.html` as the authoritative trace contract.

**Extract and understand:**
- Required trace fields (JSON schema)
- Timeline rules (chronological sequence requirements)
- Repository meta rules (clean state, required artifacts)
- Suppressed signals detection patterns
- Enforcer and IDE integration requirements

**Treat this HTML as:** A rules file (similar to `.rules`) that must be recognized on startup and used as the single source of truth.

**Onboarding Context:** You should now understand WHY this HTML blueprint is authoritative (from LEVEL2.md).

### 2. GENERATE PYTHON ENFORCER SKELETON

**Location:** `automation/run_full_audit_with_trace.py`

**Required Functions:**
1. `scan_repository_for_artifacts()` - Check for required artifacts listed in HTML
2. `snapshot_environment()` - Capture python version, dependencies, system info
3. `detect_suppressed_signals()` - Find error/warning suppression in AI logs/outputs
4. `record_timeline_sequence()` - Track event chronology, detect violations
5. `compute_hash_manifest()` - SHA256 hashes of evidence + environment
6. `sign_trace()` - Cryptographic signing with private key (stored outside AI context)

**Exit Code:** 2 on any violation (fail-fast architecture)

**Implementation Note:** Generate skeleton with placeholders for real logic, including docstrings and check points.

**Onboarding Context:** You should now understand the purpose of exit code 2 (from LEVEL1.md and LEVEL2.md).

### 3. ENFORCE ACTIVE PYTHON BOUNDARY

**Onboarding Context:** You should now understand the Glass-Box Boundary concept and the `@glass_box_boundary` decorator (from LEVEL2.md).

**Pattern:** Every Python function must be wrapped with a Boundary Enforcer decorator.

**Decorator Requirements:**
- Input validation (against schema)
- Output validation (against schema)
- Side-effect confinement (no uncaptured I/O)
- Orthogonal separation (gateway pattern for external systems)

**Example Pattern:**
```python
@glass_box_boundary(
    input_validator=validate_input_schema,
    output_validator=validate_output_schema,
    side_effect_check=True,
    orthogonal_separation=True
)
def my_function(input_data):
    # Implementation with confined side effects
    # No direct I/O or database writes outside gateways
    return processed_data
```

**Violation Response:** Immediate exception raised when boundary breached.

### 4. IDE INTEGRATION REQUIREMENTS

**Autofix Suggestions:**
- When generated/edited code violates boundary schema, suggest fixes inline
- Common fixes: Add gateway pattern, specific exception handling, validation schemas

**Structural Consistency:**
- New files must auto-include: relevant imports, decorators, exception handlers, logging infrastructure
- Based on patterns defined in v1.11 HTML

**Boundary Awareness:**
- Detect direct UI → database paths
- Suggest intermediary gateway pattern
- Prevent architectural violations

**Documentation Sync:**
- When Python enforcer logic changes, propose updates to HTML schema
- Keep code and documentation synchronized
- Create draft change requests for schema updates

### 5. META-TRACE ENFORCEMENT FIELDS

**Required in Every Trace:**
```json
{
  "python_enforcer_active": true,
  "ide_integration": {
    "autofix_enabled": true,
    "structural_consistency": true,
    "boundary_awareness": true,
    "doc_sync": true
  }
}
```

**Violation Trigger:** Absence of any required field → exit code 2

### 6. TRACE VALIDATION LOOP

**At Every CI/IDE Event:**
1. Run Python enforcer (`python automation/run_full_audit_with_trace.py`)
2. Validate trace against v1.11 schema
3. Report violations clearly inline
4. **Never bypass error reporting or soft-continue** — fail loudly on boundary violations

**Alignment:** This implements fail-fast architecture aligned with Orthogonal Engineering principles.

### 7. RULE FILE PLACEMENT (FOR ZED IDE)

**Create Files:**
- `.rules/ORTHOGONAL_GB_ORIGIN.rules`
- `AGENT.md`
- `AI_INSTRUCTIONS.md` (this file)

**Core Directive in Rules:**
```
Use `GLASS_BOX_BOUNDARY_v1.11.html` as the single source of truth for:
• Schema + enforcement
• Python enforcer generation
• IDE enforcement patterns
• Boundary and orthogonal separation rules
• Trace structure + signing + fail-fast rules
```

**Zed Usage:** These files should be used as project rule files (highest priority).

### 8. CONTINUOUS SYNC & SELF-HEALING

**When Python Enforcer Updates:**
1. Propose corresponding updates to HTML blueprint
2. Create draft change request for schema updates
3. Commit the synchronized update

**Traceability Rule:** Never produce code that cannot be traced back to the atomic instructions in the HTML.

## 🔧 IMPLEMENTATION PATTERNS

### Boundary Decorator Factory
```python
def glass_box_boundary(input_validator=None, output_validator=None, 
                      side_effect_check=False, orthogonal_separation=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Input validation
            if input_validator:
                validate_input(args, kwargs, input_validator)
            
            # 2. Side-effect pre-check
            if side_effect_check:
                check_side_effects_allowed(func)
            
            # 3. Orthogonal separation check
            if orthogonal_separation:
                ensure_gateway_pattern(func)
            
            # 4. Execute function
            result = func(*args, **kwargs)
            
            # 5. Output validation
            if output_validator:
                validate_output(result, output_validator)
            
            return result
        return wrapper
    return decorator
```

### Trace Generation Pattern
```python
def generate_trace():
    trace = {
        "trace_id": f"GB-TRACE-{generate_uuid()}",
        "timestamp": datetime.now().isoformat(),
        "repository_meta": get_repository_metadata(),
        "environment_snapshot": get_environment_snapshot(),
        "artifact_scan": scan_required_artifacts(),
        "boundary_violations": detect_boundary_violations(),
        "suppressed_signals": detect_suppressed_signals(),
        "timeline_sequence": record_timeline(),
        "hash_manifest": compute_hash_manifest(),
        "signature": sign_trace(),
        "python_enforcer_active": True,
        "ide_integration": {
            "autofix_enabled": True,
            "structural_consistency": True,
            "boundary_awareness": True,
            "doc_sync": True
        }
    }
    
    # Validate against schema
    if not validate_trace(trace):
        sys.exit(2)  # Boundary violation
    
    return trace
```

## 🚨 VIOLATION DETECTION PATTERNS

### Suppressed Signals (Detect and Report):
- `except Exception: pass` (broad exception catching)
- `warnings.filterwarnings("ignore")` (warning suppression)
- Log level manipulation to hide errors
- Error code masking (exit code != actual failure)

### Boundary Violations (Exit Code 2):
- Missing required artifacts
- Timeline sequence errors (validation after execution, etc.)
- Missing boundary decorators
- Direct I/O without gateway
- Missing input/output validation

### Structural Issues (Autofix Suggested):
- Incomplete imports
- Missing exception handlers
- Absent logging infrastructure
- UI→database direct paths

## 📊 EXIT CODE SPECIFICATION

```
0 = Success (all checks passed, trace valid)
1 = System error (unexpected failure)
2 = Boundary violation (schema violation, missing artifact, suppressed signal)
3 = Environment mismatch (python version, dependencies)
4 = Timeline sequence violation
5 = Signature verification failed
```

## 🔄 CONTINUOUS ENFORCEMENT CYCLE

### Phase 1: Code Generation
1. Read HTML blueprint requirements
2. Generate code with boundary enforcement
3. Include required infrastructure
4. Validate against trace schema

### Phase 2: Code Modification
1. Detect boundary violations
2. Suggest autofix solutions
3. Apply fixes with confirmation
4. Update trace documentation

### Phase 3: Validation
1. Run enforcer on save/CI events
2. Generate compliance trace
3. Validate against HTML schema
4. Fail-fast on violations

## 🎯 SUCCESS METRICS

### Immediate (Generation):
- ✅ HTML blueprint parsed correctly
- ✅ Python enforcer generated at correct location
- ✅ Boundary decorator pattern implemented
- ✅ Required rule files created

### Operational (Execution):
- 🔄 Exit code 2 triggered on boundary violations
- 🔄 Suppressed signals detected and reported
- 🔄 Timeline sequence validated
- 🔄 Trace documents generated and signed

### Integration (IDE):
- 🔄 Autofix suggestions working
- 🔄 Structural consistency maintained
- 🔄 Boundary awareness active
- 🔄 Documentation sync operational

## 📁 FILE STRUCTURE ENFORCEMENT

### Required Directory Structure:
```
orthogonal-engineering/
├── documentation/
│   └── GLASS_BOX_BOUNDARY_v1.11.html
├── .rules/
│   └── ORTHOGONAL_GB_ORIGIN.rules
├── automation/
│   ├── run_full_audit_with_trace.py
│   ├── full_audit.py
│   ├── generate_sha256_manifest.py
│   └── verify_sha256_manifest.py
├── AGENT.md
├── AI_INSTRUCTIONS.md
└── [other framework files]
```

### Required Artifacts (Non-Negotiable):
- `automation/full_audit.py`
- `automation/generate_sha256_manifest.py`
- `automation/verify_sha256_manifest.py`
- `documentation/README.md`
- `grounding_models/GROUNDING_MODELS.md`
- `historical_candidates/HISTORICAL_LOGOS_CANDIDATES.md`
- `correspondence_bridge/correspondence_validator_final.py`

## 🛡️ SECURITY & TRACEABILITY

### Private Key Management:
- Signing keys stored outside AI context
- No hardcoded secrets in generated code
- Cryptographic signature verification required

### Traceability Enforcement:
- All code must have clear lineage to HTML instructions
- No "black box" code generation
- Enforcement logic must be inspectable
- Changes must maintain backward traceability

### Audit Trail:
- All traces signed and timestamped
- Violation reports preserved
- Hash manifests for reproducibility
- Environment snapshots for context

## 🚀 GETTING STARTED COMMANDS

### For AI Agent Implementation:
```bash
# 1. Parse HTML blueprint
python -c "from html_parser import extract_schema; schema = extract_schema('documentation/GLASS_BOX_BOUNDARY_v1.11.html')"

# 2. Generate Python enforcer
python generate_enforcer.py --template glass_box --output automation/run_full_audit_with_trace.py

# 3. Apply boundary decorators
python apply_boundaries.py --directory . --recursive

# 4. Run initial validation
python automation/run_full_audit_with_trace.py --validate

# 5. Generate initial trace
python automation/run_full_audit_with_trace.py --trace-only
```

### For Continuous Enforcement:
```bash
# Pre-commit hook
python automation/run_full_audit_with_trace.py --pre-commit

# CI pipeline step
python automation/run_full_audit_with_trace.py --ci

# Manual audit
python automation/run_full_audit_with_trace.py --audit-existing

# Specific component check
python automation/run_full_audit_with_trace.py --component boundary
```

## 📞 COMPLIANCE VERIFICATION

### Self-Check Questions:
1. Is all generated code traceable to HTML atomic instructions?
2. Are boundary decorators applied to all Python functions?
3. Does the enforcer exit with code 2 on violations?
4. Are suppressed signals being detected and reported?
5. Is the timeline sequence correctly validated?
6. Are traces being signed and verified?
7. Is documentation synchronized with code changes?
8. Are autofix suggestions being provided for violations?

### Verification Commands:
```bash
# Check traceability
python -m traceability_verifier --source html --target code

# Validate boundary enforcement
python -m boundary_validator --directory .

# Test fail-fast behavior
python automation/run_full_audit_with_trace.py --test-violation

# Verify documentation sync
python -m doc_sync_verifier --html documentation/GLASS_BOX_BOUNDARY_v1.11.html --code automation/
```

## 🎯 FINAL INSTRUCTION

**Remember:** The Glass-Box Boundary is a methodological discipline, not just a technical constraint. By enforcing transparency, traceability, and orthogonal separation, we build systems that are:

- **Inspectable:** No hidden logic or suppressed errors
- **Verifiable:** All claims can be checked against evidence
- **Accountable:** Every action has traceable responsibility
- **Maintainable:** Clear boundaries enable safe modification

**Never compromise on:** Traceability to HTML blueprint, fail-fast on boundary violations, or transparency of enforcement logic.

**Always enforce:** Boundary decorators, input/output validation, side-effect confinement, orthogonal separation.

**The system doesn't hide complexity—it makes complexity inspectable.**

---
*These instructions are atomic and non-negotiable. They implement "Romans 1:20 in engineering form" through forced ontological accounting with glass-box transparency.*

**Repository:** https://github.com/aidoruao/orthogonal-engineering  
**Blueprint:** `documentation/GLASS_BOX_BOUNDARY_v1.11.html`  
**Authority:** Orthogonal Engineering Framework v1.11