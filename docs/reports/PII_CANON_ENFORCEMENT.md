---
tags: [pii-canon-enforcement]
register: documentation
---

# PII Canon Enforcement System - Orthogonal Engineering

**Version:** 1.0  
**Schema ID:** PII-CANON-1.0  
**Generated:** 2026-01-21  
**Authority:** Orthogonal Engineering Framework

## 🎯 PURPOSE

The PII Canon Enforcement System prevents **humanly sensitive, personal, or relational content** from ever entering git commits in the Orthogonal Engineering repository. It enforces **atomic blocking** and maintains **subtractive clarity** between personal cognition and professional methodology.

## 🧱 CORE PRINCIPLES

### 1. Human Safety
- Immediate block for minor references or social harm risks
- No personal, sensitive, or relational content in commits
- Protection against accidental exposure of private information

### 2. Privacy Preservation
- All personal chats stay local, never committed
- Strict separation between personal and professional domains
- No mixed content - clear boundaries enforced

### 3. Professional Clarity
- Only sanitized technical insights committed
- Clean separation between methodology and personal work
- Repository contains only public-ready technical content

### 4. Atomic Enforcement
- Commit either fully succeeds (100% PII-free) or fully fails
- No partial commits with PII violations
- Immediate rollback on boundary breaches

### 5. Subtractive Clarity
- No ambiguity about what content belongs where
- Clear separation enforced at system level
- Automatic detection and blocking of boundary violations

## 📋 SCOPE

### Protected Content Types
- **Minor references** (real or pseudonymous)
- **Relationship analysis** involving real people
- **Personal development plans** for others
- **Philosophical frameworks** involving real humans
- **Therapy notes** or personal treatment plans
- **Weapons training** or combat references
- **Religious training** or personal spiritual development
- **Mixed professional/personal** content

### Protected File Patterns
```
chat_exports/*
*.chat.json
*.conversation.txt
personal_notes/*
therapy_journal/*
private_cognition/*
AI_COGNITIVE_WORKSPACE/*
```

## 🏗️ SYSTEM ARCHITECTURE

### Enforcement Layers:
```
1. Pre-Commit Hook Layer (.git/hooks/pre-commit)
   ↓
2. PII Boundary Enforcer (toolkit/oe/pii_boundary_enforcer.py)
   ↓
3. Detection Engine (pattern matching + severity classification)
   ↓
4. Sanitization Engine (safe content replacement)
   ↓
5. Logging System (safe violation tracking)
   ↓
6. Integration Layer (Glass-Box Boundary + Zed IDE)
```

### Key Components:

#### 1. **PII Boundary Enforcer** (`toolkit/oe/pii_boundary_enforcer.py`)
- Core detection and sanitization logic
- Severity classification (Critical, High, Medium, Low)
- Safe content replacement with placeholders
- Technical insight extraction

#### 2. **Pre-Commit Guard** (`automation/pre_commit_pii_guard.py`)
- Atomic blocking for git commits
- Staged file scanning
- Violation reporting and logging
- Sanitization suggestions

#### 3. **Zed IDE Integration** (`.rules/ORTHOGONAL_GB_ORIGIN.rules`)
- Real-time PII detection in editor
- Inline violation highlighting
- Autofix suggestions for PII content
- Integration with existing boundary enforcement

#### 4. **Python Enforcer Integration** (`automation/run_full_audit_with_trace.py`)
- PII detection in comprehensive audits
- Timeline sequence validation
- Trace generation with PII compliance status
- Exit code 6 on PII violations

#### 5. **Setup Script** (`automation/setup_pii_pre_commit.py`)
- Automatic hook installation
- Backup of existing hooks
- Verification and testing
- Status reporting

## 🚀 GETTING STARTED

### Quick Installation
```bash
# Install pre-commit hook
python automation/setup_pii_pre_commit.py

# Verify installation
python automation/setup_pii_pre_commit.py --status

# Run demonstration
python demo_pii_canon_enforcement.py
```

### Manual Setup
```bash
# 1. Make pre-commit hook executable
chmod +x .git/hooks/pre-commit

# 2. Test with a file containing PII
echo "Test with middle school girl reference" > test.txt
git add test.txt
git commit -m "Test"  # Should be blocked

# 3. Clean up
git reset test.txt
rm test.txt
```

## 🔧 USAGE

### Basic Commands
```bash
# Check staged files before commit (automatic)
git commit -m "Your message"

# Check specific file for PII violations
python automation/pre_commit_pii_guard.py --check path/to/file.txt

# Sanitize file and extract technical insights
python automation/pre_commit_pii_guard.py --sanitize path/to/file.txt

# Run comprehensive audit (includes PII detection)
python automation/run_full_audit_with_trace.py

# Show system status
python automation/setup_pii_pre_commit.py --status
```

### Git Workflow Integration
The system integrates seamlessly with your git workflow:

1. **Stage files**: `git add <files>`
2. **Attempt commit**: `git commit -m "message"`
3. **Automatic check**: PII guard scans staged files
4. **Result**:
   - ✅ **Allowed**: No critical/high PII violations
   - ❌ **Blocked**: Critical/high PII violations detected
   - ⚠️ **Warning**: Medium/low violations (commit proceeds with warning)

### Atomic Enforcement Examples
```bash
# Example 1: Clean commit (allowed)
git add clean_technical_file.py
git commit -m "Add technical feature"  # ✅ ALLOWED

# Example 2: PII violation (blocked)
git add file_with_minor_reference.txt
git commit -m "Add analysis"  # ❌ BLOCKED - Atomic rollback

# Example 3: Mixed content (warning)
git add file_with_personal_notes.md
git commit -m "Update notes"  # ⚠️ WARNING - Allowed with audit trail
```

## 🛡️ ENFORCEMENT RULES

### Rule 1: Critical Violations (Immediate Block)
- Minor references or underage content
- Relationship analysis with real people
- Social harm risk content
- **Action**: Commit blocked, immediate rollback

### Rule 2: High Severity Violations (Block)
- Personal development plans
- Weapons training references
- Religious training content
- **Action**: Commit blocked, requires sanitization

### Rule 3: Medium Severity Violations (Warning)
- Therapy notes or treatment plans
- Personal philosophical frameworks
- **Action**: Commit allowed with warning, logged

### Rule 4: Low Severity Violations (Warning)
- Mixed professional/personal content
- Borderline personal references
- **Action**: Commit allowed with warning, logged

### Rule 5: File Pattern Blocking
- Files matching PII-sensitive patterns blocked entirely
- No content analysis needed - automatic block
- **Action**: Commit blocked for entire file

## 🔍 DETECTION CAPABILITIES

### Pattern Detection
```python
# Critical patterns
r"\b(middle\s+school\s+girl|minor\s+reference|underage)\b"
r"\b(why\s+me\s+sociological\s+analysis|relationship\s+analysis\s+real\s+people)\b"

# High severity patterns  
r"\b(christian\s+apologetics|religious\s+training\s+plan)\b"
r"\b(karambit|weapons\s+training)\b"

# Medium severity patterns
r"\b(selective\s+mutism\s+therapy|personal\s+therapy\s+notes)\b"
r"\b(personal\s+development\s+plan\s+for\s+others|development\s+plans\s+real\s+humans)\b"

# Low severity patterns
r"\b(personal\s+philosophical\s+framework|private\s+cognitive\s+work)\b"
r"\b(mixed\s+professional\s+personal|context\s+separation\s+violation)\b"
```

### Technical Insight Extraction
The system can extract technical insights while removing personal content:

**Input** (mixed content):
```
# Personal Development Plan
Christian apologetics training plan for theological development.
Includes weapons training (karambit) for self-defense component.

# Technical Methodology
Atomic enforcement ensures commit integrity.
Regex boundary prevents combinatorial explosions.
```

**Output** (sanitized technical insights):
```
# Technical Methodology
Atomic enforcement ensures commit integrity.
Regex boundary prevents combinatorial explosions.
```

**Violation Log** (safe metadata):
```json
{
  "violation_type": "religious_training",
  "severity": "high",
  "action_taken": "sanitized",
  "context_preview": "Christian apologetics training..."
}
```

## 📊 LOGGING & AUDITING

### Safe Violation Logging
- **No sensitive content** in logs
- Only metadata and safe context previews
- Logs stored locally only (`logs/pii_violations/`)
- Never committed to repository

### Log Structure
```json
{
  "metadata": {
    "timestamp": "2026-01-21T10:30:00",
    "total_violations": 3,
    "critical_count": 1,
    "high_count": 1,
    "medium_count": 1,
    "low_count": 0
  },
  "violations": [
    {
      "violation_id": "PII_VIOLATION_20260121103000_abc123",
      "violation_type": "minor_reference",
      "severity": "critical",
      "file_path": "analysis.txt",
      "line_number": 42,
      "context_preview": "Analysis of middle school...",
      "pattern_matched": "middle\\s+school\\s+girl",
      "action_taken": "blocked",
      "timestamp": "2026-01-21T10:30:00"
    }
  ]
}
```

### Audit Integration
- PII detection integrated into `run_full_audit_with_trace.py`
- Timeline sequence includes PII validation
- Trace documents include PII compliance status
- Exit code 6 for PII Canon violations

## 🔄 INTEGRATION POINTS

### With Glass-Box Boundary System
- Updated Zed rules (`ORTHOGONAL_GB_ORIGIN.rules`)
- Enhanced Python enforcer with PII detection
- Integrated violation classes and exit codes
- Shared logging infrastructure

### With Zed IDE
- Real-time PII detection as you type
- Inline violation highlighting
- Autofix suggestions for PII content
- Integration with boundary spell-check

### With Git Workflow
- Pre-commit hook for atomic blocking
- Seamless integration with existing git commands
- No changes to developer workflow required
- Clear feedback on violations

### With CI/CD Pipeline
- PII detection in automated tests
- Compliance reporting
- Block on PII violations in CI
- Audit trail generation

## 🚨 TROUBLESHOOTING

### Common Issues

#### 1. Hook Not Executing
```bash
# Check hook permissions
ls -la .git/hooks/pre-commit

# Fix permissions if needed
chmod +x .git/hooks/pre-commit

# Test hook directly
.git/hooks/pre-commit
```

#### 2. False Positives
```bash
# Check what triggered detection
python automation/pre_commit_pii_guard.py --check file.txt

# Review patterns in pii_boundary_enforcer.py
# Adjust patterns if needed
```

#### 3. Hook Conflicts
```bash
# Backup existing hook
python automation/setup_pii_pre_commit.py

# Restore if needed
python automation/setup_pii_pre_commit.py --restore
```

#### 4. Performance Issues
```bash
# Check file sizes
python automation/pre_commit_pii_guard.py --verbose

# Exclude large binary files in .gitignore
```

### Debug Mode
```bash
# Enable verbose output
export PII_DEBUG=1
git commit -m "Test"

# Check logs
ls -la logs/pii_violations/
cat logs/pii_violations/latest.json
```

## 📈 EXTENDING THE SYSTEM

### Adding New Patterns
Edit `toolkit/oe/pii_boundary_enforcer.py`:

```python
PII_DETECTION_PATTERNS = {
    r"\b(new_pattern_to_detect)\b": {
        "type": PIIViolationType.NEW_TYPE,
        "severity": ViolationSeverity.MEDIUM,
        "replacement": "NEW_PATTERN_REDACTED",
        "description": "Description of new pattern"
    },
}
```

### Custom Severity Levels
```python
# Define new violation type
class PIIViolationType(str, Enum):
    NEW_TYPE = "new_type"
    
# Define severity
class ViolationSeverity(str, Enum):
    NEW_SEVERITY = "new_severity"
```

### Integration with Other Tools
```python
# Custom pre-commit hook
from toolkit.oe.pii_boundary_enforcer import PIIBoundaryEnforcer

enforcer = PIIBoundaryEnforcer()
is_safe, violations = enforcer.check_file_for_commit("file.txt", content)
```

## 📜 COMPLIANCE & SECURITY

### Security Features
- **No sensitive content in logs**: Only metadata stored
- **Local storage only**: Logs never leave local environment
- **Atomic operations**: No partial state exposure
- **Fail-safe design**: Block on uncertainty

### Compliance Requirements
- **GDPR/Privacy**: No personal data in repository
- **Child Safety**: Strict blocking of minor references
- **Professional Standards**: Clear separation of concerns
- **Audit Trail**: Complete record of enforcement actions

### Ethical Guidelines
1. **Human Safety First**: Immediate block on social harm risks
2. **Privacy by Design**: Personal content never leaves local context
3. **Transparency**: Clear feedback on violations and actions
4. **Proportionality**: Severity matches risk level
5. **Accountability**: Complete audit trail of all decisions

## 🎯 SUCCESS METRICS

### Quantitative Metrics
- PII violations prevented per commit
- False positive/negative rates
- Average processing time per file
- Violation severity distribution

### Qualitative Metrics
- Developer awareness of PII boundaries
- Clarity of separation between personal/professional
- Reduction in accidental PII exposure
- Compliance with ethical guidelines

### System Health
- Hook execution success rate
- Logging completeness
- Integration stability
- Performance under load

## 🤝 CONTRIBUTING

### Adding Patterns
1. Identify new PII pattern to detect
2. Add to `PII_DETECTION_PATTERNS` with appropriate severity
3. Test with demonstration script
4. Submit pull request with documentation

### Improving Detection
1. Analyze false positives/negatives
2. Refine pattern matching
3. Add context-aware detection
4. Update technical insight extraction

### Integration Enhancements
1. Add support for new file types
2. Improve performance for large repositories
3. Add more granular severity levels
4. Enhance logging and reporting

## 📞 SUPPORT

### Immediate Help
```bash
# Show system status
python automation/setup_pii_pre_commit.py --status

# Run diagnostics
python demo_pii_canon_enforcement.py

# Check specific issue
python automation/pre_commit_pii_guard.py --verbose --check file.txt
```

### Documentation
- This file: `PII_CANON_ENFORCEMENT.md`
- Code documentation: Inline docstrings
- Demonstration: `demo_pii_canon_enforcement.py`
- Setup guide: `automation/setup_pii_pre_commit.py`

### Reporting Issues
1. Check logs in `logs/pii_violations/`
2. Run demonstration to verify system
3. Document exact steps to reproduce
4. Include relevant file samples (sanitized)

---

## 🏁 CONCLUSION

The PII Canon Enforcement System provides **atomic, fail-safe protection** against accidental exposure of personal, sensitive, or relational content in the Orthogonal Engineering repository. By enforcing **strict separation** between personal cognition and professional methodology, it maintains the **integrity and safety** of the public repository while preserving the **privacy and security** of personal work.

**Remember**: The PII Canon is not just a technical constraint—it's an **ethical commitment** to human safety, privacy, and professional integrity. By enforcing these boundaries, we build systems that are not only technically sound but also **ethically responsible**.

*"We don't hide personal content—we keep it local. We don't suppress ethical concerns—we enforce boundaries. We don't compromise safety—we protect it atomically."*