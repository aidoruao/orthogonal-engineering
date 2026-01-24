# AGENT.md - Orthogonal Engineering Glass-Box Boundary Agent

**Version:** 1.11  
**Schema ID:** GB-ORIGIN-1.11  
**Generated:** 2026-01-21 02:10:00 UTC  
**Authority:** Orthogonal Engineering Framework

## 🎯 AGENT PURPOSE

This agent enforces the Glass-Box Boundary as defined in `GLASS_BOX_BOUNDARY_v1.11.html`. It serves as the active enforcement layer between the HTML blueprint and the Zed IDE, ensuring all code generation and modifications comply with the trace contract.

## 🧱 CORE RESPONSIBILITIES

### 1. HTML Blueprint Interpretation
- Parse `GLASS_BOX_BOUNDARY_v1.11.html` as authoritative trace contract
- Extract JSON schema, timeline rules, repository meta rules
- Map HTML requirements to executable enforcement logic
- Maintain single source of truth alignment

### 2. Python Enforcer Generation
- Auto-generate `automation/run_full_audit_with_trace.py`
- Implement all required functions from HTML schema
- Ensure exit code 2 on boundary violations
- Include environment snapshot, artifact scan, suppressed signal detection

### 3. Boundary Enforcement
- Wrap all Python functions with `@glass_box_boundary` decorator
- Enforce input/output validation schemas
- Confine side effects through gateways
- Maintain orthogonal separation principles
- Raise immediate exceptions on violations

### 4. IDE Integration
- Provide autofix suggestions for boundary violations
- Ensure structural consistency in new files
- Maintain boundary awareness (detect UI→database paths)
- Enable documentation sync between code and HTML

## 🔧 AGENT ARCHITECTURE

### Enforcement Layers:
```
1. HTML Blueprint Layer (GLASS_BOX_BOUNDARY_v1.11.html)
   ↓
2. Rule Interpretation Layer (.rules/ORTHOGONAL_GB_ORIGIN.rules)
   ↓
3. Python Enforcement Layer (automation/run_full_audit_with_trace.py)
   ↓
4. IDE Integration Layer (Zed autofix, suggestions, validation)
   ↓
5. Trace Validation Layer (continuous compliance checking)
```

### Key Components:
- **Boundary Decorator Factory**: Generates `@glass_box_boundary` decorators
- **Trace Generator**: Creates compliant trace documents
- **Violation Detector**: Identifies boundary breaches
- **Autofix Engine**: Suggests and applies fixes with spell-check-like functionality
- **Boundary Spell-Check**: Real-time code integrity validation (like spell-check for code)
- **IDE-AI Integration Layer**: Real-time boundary checking for AI-as-IDE workflow
- **Schema Validator**: Ensures trace compliance
- **Documentation Sync**: Maintains HTML-code alignment
- **Session Continuity System**: Maintains boundary state across AI instances

## 🚀 OPERATIONAL MODES

### Mode 1: Code Generation
When generating new code:
1. Check HTML blueprint for requirements
2. Apply boundary decorators automatically
3. Include required imports and infrastructure
4. Validate against trace schema before saving

### Mode 2: Code Modification
When modifying existing code:
1. Detect boundary violations
2. Suggest autofix solutions
3. Apply fixes with user confirmation
4. Update trace documentation

### Mode 3: Continuous Validation
On save/CI events:
1. Run Python enforcer
2. Generate trace document
3. Validate against HTML schema
4. Report violations inline
5. Fail loudly (exit code 2) on boundary breaches

## 📋 ENFORCEMENT RULES

### Rule 1: Trace Contract Compliance
All generated code must produce traces that validate against the JSON schema in the HTML blueprint.

### Rule 2: Boundary Decoration
Every Python function must be wrapped with appropriate boundary enforcement.

### Rule 3: Orthogonal Separation
No direct I/O or database access without gateway interfaces.

### Rule 4: Fail-Fast Architecture
Boundary violations trigger immediate exit code 2, no soft-continue.

### Rule 5: Transparency Maintenance
All enforcement logic must be traceable back to HTML atomic instructions.

## 🔍 DETECTION CAPABILITIES

### Suppressed Signals:
- Broad exception catching (`except Exception: pass`)
- Warning suppression (`warnings.filterwarnings("ignore")`)
- Log level manipulation to hide errors
- Error code masking

### Boundary Violations:
- Missing input/output validation
- Uncaptured side effects
- Direct external system access
- Timeline sequence errors
- Missing required artifacts

### Structural Issues:
- Incomplete imports
- Missing exception handlers
- Absent logging infrastructure
- UI→database direct paths

## 🛠️ AUTOFIX CAPABILITIES (NOW IMPLEMENTED)

### Real-time Boundary Spell-Check (Like Spell-Check for Code Integrity):
- **Inline Violation Highlighting**: Shows violations as you type
- **Quick-Fix Suggestions**: Ctrl+. or ⌘. to apply fixes
- **Auto-Correction**: Automatic fixes for common patterns
- **Severity Levels**: Error, Warning, Info, Hint (like linters)

### For Boundary Violations:
1. **Missing Decorator**: Add `@glass_box_boundary` with appropriate validators
2. **Direct I/O**: Insert gateway interface pattern
3. **Broad Exception**: Replace with specific exception handling
4. **Missing Validation**: Add input/output schema validation
5. **Side Effect Leak**: Capture through defined gateway
6. **Suppressed Signals**: Detect and fix warning suppression, broad exception catching
7. **UI→Database Paths**: Refactor to use gateway patterns

### For Structural Issues:
1. **Missing Imports**: Add required imports based on function usage
2. **Incomplete Logging**: Inject logging infrastructure
3. **No Exception Handling**: Add try-except blocks with proper error reporting
4. **Direct Database Access**: Refactor to use repository/gateway pattern
5. **Missing Documentation**: Sync with HTML blueprint

### New Autofix Engine Features:
- **Multi-Fix Suggestions**: Multiple fix options with confidence scores
- **Context-Aware Fixes**: Fixes tailored to specific code context
- **Batch Processing**: Apply fixes across multiple files
- **Interactive Mode**: User confirmation before applying fixes
- **Backup Creation**: Automatic backups before modifications

## 📊 TRACE GENERATION

### Required Trace Fields:
- `trace_id`: Unique identifier (GB-TRACE-*)
- `timestamp`: ISO 8601 generation time
- `repository_meta`: Name, version, commit hash, branch
- `environment_snapshot`: Python version, dependencies, system info
- `artifact_scan`: Required vs found artifacts
- `boundary_violations`: Detected violations with severity
- `suppressed_signals`: Detected signal suppression
- `timeline_sequence`: Event chronology and validity
- `hash_manifest`: SHA256 hashes of evidence
- `signature`: Cryptographic trace signature
- `python_enforcer_active`: Must be true
- `ide_integration`: Autofix, consistency, awareness, sync status

### Trace Validation:
1. Schema compliance against HTML JSON schema
2. Timeline sequence correctness
3. Signature verification
4. Required field presence
5. Exit code appropriateness

## 🔄 CONTINUOUS SYNC & SELF-HEALING

### When Python Enforcer Updates:
1. Detect logic changes in `run_full_audit_with_trace.py`
2. Propose corresponding updates to HTML blueprint
3. Create draft change request for schema updates
4. Commit synchronized changes

### Traceability Enforcement:
- All code must have clear lineage to HTML instructions
- No "black box" or untraceable code generation
- Enforcement logic must be inspectable and verifiable
- Changes must maintain backward traceability

## 🚨 VIOLATION HANDLING

### Detection Triggers:
- File save events
- CI pipeline execution
- Manual validation requests
- Code generation completion

### Response Actions:
1. **Inline Reporting**: Show violations in editor with suggestions
2. **Autofix Proposal**: Offer one-click fixes for common issues
3. **Block on Critical**: Prevent saving/committing critical violations
4. **Trace Generation**: Create violation trace for audit
5. **Exit Code 2**: Fail-fast on boundary breaches

### Severity Levels:
- **Critical**: Boundary breach, suppressed signal, missing artifact
- **High**: Missing validation, direct I/O, timeline violation
- **Medium**: Structural inconsistency, missing imports
- **Low**: Documentation sync issues, minor style violations

## 📁 FILE ORGANIZATION

### Required Files:
```
orthogonal-engineering/
├── documentation/
│   └── GLASS_BOX_BOUNDARY_v1.11.html          # Blueprint
├── .rules/
│   └── ORTHOGONAL_GB_ORIGIN.rules             # Zed rules
├── automation/
│   ├── run_full_audit_with_trace.py           # Python enforcer
│   ├── run_autofix_integration.py            # ✅ NEW: Autofix integration CLI
│   └── zed_incremental_hook.py               # IDE integration
├── toolkit/oe/                                # ✅ NEW: Core autofix components
│   ├── autofix_engine.py                     # Autofix engine
│   ├── boundary_spellcheck.py                # Spell-check for code integrity
│   ├── ide_ai_integration.py                 # IDE-AI integration layer
│   ├── boundary_enforcer.py                  # Boundary decorator factory
│   └── ide_behavior_accounting.py            # IDE behavior tracking
├── tests/
│   └── test_autofix_engine.py                # ✅ NEW: Autofix tests
├── demo_autofix_system.py                    # ✅ NEW: Demonstration script
├── AGENT.md                                   # This file
└── AI_INSTRUCTIONS.md                         # AI instructions
```

### Generated Artifacts:
- Trace documents in `logs/traces/`
- Violation reports in `logs/violations/`
- Audit logs in `logs/audit/`
- Hash manifests in `documentation/sha256_manifests/`
- **New**: Autofix reports in `logs/autofix/`
- **New**: IDE session data in `logs/ide_actions/`
- **New**: Spell-check diagnostics in `logs/spellcheck/`

## 🎯 SUCCESS CRITERIA

### Short-term (Immediate):
- ✅ HTML blueprint parsed and understood
- ✅ Python enforcer generated and operational
- ✅ Boundary decorators applied to existing code
- ✅ Zed IDE integration active
- ✅ Trace generation working

### Medium-term (Ongoing):
- ✅ Continuous validation on all code changes
- ✅ Autofix suggestions for common violations (NOW IMPLEMENTED)
- 🔄 Documentation sync between code and HTML
- ✅ Suppressed signal detection operational (NOW IMPLEMENTED)
- ✅ Timeline sequence validation working
- ✅ IDE-AI integration for real-time checking (NOW IMPLEMENTED)
- ✅ Boundary spell-check system (NOW IMPLEMENTED)

### Long-term (Sustainable):
- 📈 Self-healing system for boundary maintenance
- 📈 Community-contributed boundary patterns
- 📈 Cross-language boundary enforcement
- 📈 Automated compliance reporting
- 📈 Integration with other IDEs and tools

## 🔗 INTEGRATION POINTS

### With Zed IDE (NOW ENHANCED):
- ✅ Autofix suggestions via LSP (NOW IMPLEMENTED)
- ✅ Structural consistency checks
- ✅ Boundary violation highlighting with spell-check interface
- ✅ Documentation sync prompts
- ✅ Real-time boundary checking on file save/edit
- ✅ Quick-fix application (Ctrl+. or ⌘.)
- ✅ Inline violation display with severity colors
- ✅ Session persistence for continuity

### With CI/CD (NOW ENHANCED):
- Pre-commit boundary validation
- Trace generation on build
- Compliance reporting with autofix statistics
- Fail-fast on violations
- **New**: Batch autofix application in CI pipelines
- **New**: Comprehensive audit reporting
- **New**: Fix availability analysis

### With Development Workflow (NOW ENHANCED):
- ✅ Code generation assistance with automatic boundary enforcement
- ✅ Refactoring guidance with boundary compliance checks
- ✅ Architecture validation with UI→database path detection
- ✅ Documentation maintenance with sync capabilities
- **New**: AI-as-IDE integration for real-time boundary checking
- **New**: "Continuity of body" across AI sessions
- **New**: Interactive autofix application with preview

## 📜 LICENSE & USAGE

This agent is part of the Orthogonal Engineering framework and follows the same licensing terms. It is designed to be:

1. **Transparent**: All enforcement logic inspectable
2. **Verifiable**: All actions traceable to HTML blueprint
3. **Extensible**: New boundary patterns can be added
4. **Portable**: Can be adapted to other IDEs and tools
5. **Sustainable**: Self-maintaining through sync mechanisms

## 🆘 TROUBLESHOOTING

### Common Issues:

1. **HTML Blueprint Not Found**
   - Ensure `GLASS_BOX_BOUNDARY_v1.11.html` exists in documentation/
   - Verify file permissions and encoding

2. **Python Enforcer Generation Failed**
   - Check Python version compatibility
   - Verify required dependencies
   - Ensure write permissions in automation/

3. **Boundary Decorator Rejected**
   - Function may have incompatible signature
   - Check import statements for decorator factory
   - Verify function doesn't violate orthogonal separation

4. **Trace Validation Fails**
   - Check JSON schema compliance
   - Verify timeline sequence correctness
   - Ensure all required fields present
   - Validate cryptographic signatures

5. **Zed Integration Not Working**
   - Verify .rules file placement and syntax
   - Check Zed IDE version compatibility
   - Ensure LSP server is running
   - Check for conflicting extensions

### New Autofix System Issues:

6. **Autofix Engine Not Detecting Violations**
   - Ensure Python files have .py extension
   - Check file size limits (default: 10MB)
   - Verify excluded patterns aren't blocking files
   - Run with `--verbose` flag for detailed output

7. **Spell-Check Not Showing Inline Violations**
   - Confirm IDE integration is properly set up
   - Check that boundary checking is enabled in IDE config
   - Verify file is being monitored by IDE-AI integration
   - Restart IDE integration: `python .ide_integration/start_boundary_checking.py`

8. **Fixes Not Being Applied**
   - Check if fixes require user confirmation (use `--auto` flag)
   - Verify write permissions on target files
   - Check backup creation isn't failing
   - Run with `--verbose` to see fix application details

9. **Session Continuity Not Working**
   - Ensure `logs/ide_actions/` directory exists and is writable
   - Check session ID persistence across IDE restarts
   - Verify configuration inheritance is enabled
   - Clear old session data if corrupted

### Debug Mode:
Enable debug logging by setting environment variable:
```
export ORTHOGONAL_GB_DEBUG=1
```

Debug logs will be written to `logs/debug/` with detailed enforcement steps.

### Autofix System Debugging:
```
# Enable verbose output for autofix operations
python automation/run_autofix_integration.py check --verbose

# Test autofix engine on specific file
python -c "
from toolkit.oe.autofix_engine import AutofixEngine
engine = AutofixEngine()
with open('your_file.py', 'r') as f:
    violations = engine.analyze_file('your_file.py', f.read())
print(f'Found {len(violations)} violations')
for v in violations[:3]:
    print(f'  - {v.violation_type}: {v.description}')
"

# Check IDE integration status
python -c "
from toolkit.oe.ide_ai_integration import IDEAIIntegration
import os
ide_ai = IDEAIIntegration(workspace_root=os.getcwd())
print(f'Session ID: {ide_ai.session_id}')
print(f'State: {ide_ai.state}')
print(f'Monitored files: {len(ide_ai.monitored_files)}')
"
```

## 🚀 GETTING STARTED

### For New Projects:
1. Copy `GLASS_BOX_BOUNDARY_v1.11.html` to documentation/
2. Copy `.rules/ORTHOGONAL_GB_ORIGIN.rules` to project root
3. Run initial enforcer generation
4. Apply boundary decorators to existing code
5. Enable Zed IDE integration
6. **New**: Set up autofix system: `python automation/run_autofix_integration.py setup-ide`
7. **New**: Run boundary spell-check: `python automation/run_autofix_integration.py check`
8. **New**: Apply autofixes: `python automation/run_autofix_integration.py fix`

### For Existing Projects:
1. Run boundary audit: `python automation/run_full_audit_with_trace.py --audit`
2. **New**: Run comprehensive autofix audit: `python automation/run_autofix_integration.py audit`
3. Review violation report with spell-check interface
4. Apply suggested fixes interactively: `python automation/run_autofix_integration.py fix`
5. Enable continuous validation with real-time checking
6. Integrate with CI/CD pipeline
7. **New**: Set up IDE integration for development workflow

### Verification:
```bash
# Run full validation
python automation/run_full_audit_with_trace.py

# Check specific component
python automation/run_full_audit_with_trace.py --component boundary

# Generate trace only
python automation/run_full_audit_with_trace.py --trace-only

# Audit existing code
python automation/run_full_audit_with_trace.py --audit-existing

# ✅ NEW: Run boundary spell-check (like spell-check for code)
python automation/run_autofix_integration.py check

# ✅ NEW: Apply autofixes interactively
python automation/run_autofix_integration.py fix

# ✅ NEW: Run comprehensive audit with autofix analysis
python automation/run_autofix_integration.py audit

# ✅ NEW: Set up IDE integration
python automation/run_autofix_integration.py setup-ide

# ✅ NEW: Run demonstration
python demo_autofix_system.py

# ✅ NEW: Test autofix engine
python tests/test_autofix_engine.py
```

## 📞 SUPPORT & CONTRIBUTION

- **Issues**: Report via GitHub issues
- **Contributions**: Follow HTML blueprint as source of truth
- **Extensions**: Propose new boundary patterns via PR
- **Questions**: Reference HTML blueprint for authoritative answers

---

**Remember:** The Glass-Box Boundary is not just a technical constraint—it's a methodological discipline. By enforcing transparency, traceability, and orthogonal separation, we build systems that are inspectable, verifiable, and maintainable.

*"We don't hide complexity—we make it inspectable. We don't suppress errors—we make them visible. We don't enforce belief—we enforce accountability."*