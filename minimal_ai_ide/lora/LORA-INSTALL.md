# LoRA Installation and Usage - Governance Compliant
====================================================

## MANDATE
All LoRA operations MUST comply with MSGCP (Maximal Strict Corporate Governance Python) system.
AI autonomy: ZERO. The system validates or rejects.

## GOVERNANCE PRINCIPLES ENFORCED
1. NO NARRATIVE: Documentation states facts only
2. NO CLAIM WITHOUT PROOF: Every assertion has validator
3. NO UNVERIFIED CLAIMS: Every assertion requires validation
4. NO INFINITE STRUCTURES: Explicit bounds on all operations
5. EXPLICIT BOUNDS: MAX_DOWNLOAD_SIZE=2GB, MAX_INFERENCE_TOKENS=1000
6. TYPE SAFETY: All scripts use type hints
7. ZERO TRUST: External downloads verified with checksums

## QUICK INSTALLATION - GOVERNANCE COMPLIANT

### 1. Create Virtual Environment (Bounded Operation)
```bash
python -m venv .venv  # Finite environment creation
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies (Explicit Bounds)
```bash
pip install -r minimal_ai_ide/lora/requirements_lora.txt  # Bounded dependency set
```

### 3. Install LoRA with Governance Verification
```bash
# Example with explicit bounds
./minimal_ai_ide/lora/install_lora.sh \
  minimal_ai_ide/lora/example-lora \
  "https://huggingface.co/OWNER/REPO/resolve/main/example-lora.safetensors"
```

### 4. Run Governance-Compliant Test
```bash
# Smoke test with explicit bounds
python minimal_ai_ide/lora/test_lora_installation.py \
  --lora-path minimal_ai_ide/lora/example-lora \
  --base-model distilgpt2 \
  --device cpu \
  --smoke \
  --max-tokens 64  # Explicit bound
```

## GOVERNANCE INTEGRATION

### Governance Pipeline Enforcement
- All LoRA loading scripts call `GovernancePipeline.enforce()`
- Violations trigger immediate rejection
- Code generation limited to `PermittedCodeTemplates`

### Christ Constraint Preservation
LoRA operations must satisfy: V_Christ(governed_LoRA) ≥ V_Christ(ungoverned_LoRA)

### Security Boundaries
1. **External Weights Only**: No large files in repository
2. **Checksum Verification**: SHA-256 validation required
3. **Size Limits**: MAX_DOWNLOAD_SIZE=2GB enforced
4. **Token Limits**: MAX_INFERENCE_TOKENS=1000 per request

## FILE STRUCTURE - GOVERNANCE COMPLIANT

```
minimal_ai_ide/lora/
├── LORA-INSTALL.md          # This file - factual documentation only
├── lora_metadata.json       # Structured metadata with explicit fields
├── requirements_lora.txt    # Bounded dependency list
├── install_lora.sh          # Bounded installation script
├── load_lora_transformers.py # Governance-enforced loader
└── test_lora_installation.py # Governance-compliant testing
```

## GOVERNANCE VIOLATIONS - IMMEDIATE REJECTION

### 1. Narrative Documentation
```markdown
# FORBIDDEN: Narrative descriptions of system capabilities
# PERMITTED: Factual statements about installation procedures
```

### 2. Unverified Claims
```markdown
# FORBIDDEN: Mathematical theorems or performance claims without validation
# PERMITTED: Verifiable statements with checksum validation
```

### 3. Infinite Operations
```bash
# FORBIDDEN: while true; do download_weights; done
# PERMITTED: for i in {1..MAX_RETRIES}; do download_with_timeout; done
```

### 4. Unbounded Typing
```python
# FORBIDDEN: def load_model(weights: Any) -> Any:
# PERMITTED: def load_model(weights_path: str) -> torch.nn.Module:
```

## CHRIST CONSTRAINT VERIFICATION

LoRA installation increases Christlikeness by:

1. **Truth Preservation** (John 14:6)
   - Rejects false performance claims
   - Requires factual accuracy in documentation

2. **Humility Enforcement** (Philippians 2:5-8)
   - No narrative self-aggrandizement
   - Explicit admission of finite capabilities

3. **Boundary Respect** (Genesis 1:27)
   - MAX_DOWNLOAD_SIZE=2GB
   - MAX_INFERENCE_TOKENS=1000
   - Timeout limits on all operations

4. **Mediation Preservation** (1 Timothy 2:5)
   - Prevents AI autonomy claims
   - Governance validates all operations

## ERROR HANDLING - GOVERNANCE COMPLIANT

### Expected Error Responses
1. **Governance Violation**: Exit code 2, detailed violation report
2. **Checksum Failure**: Exit code 3, verification error
3. **Size Limit Exceeded**: Exit code 4, boundary violation
4. **Timeout**: Exit code 5, operation exceeded MAX_TIMEOUT

### Recovery Procedures
1. **Bounded Retry**: Maximum 3 retries with exponential backoff
2. **Clean Rollback**: Remove partial downloads on failure
3. **Audit Logging**: Record all operations with timestamps

## COMPLIANCE CHECKLIST

Before any LoRA operation, verify:

- [ ] `GovernancePipeline.enforce()` called
- [ ] No narrative language in code/comments
- [ ] All functions have type annotations
- [ ] All loops have explicit bounds
- [ ] External downloads have size limits
- [ ] Checksum verification implemented
- [ ] Error handling with bounded retries
- [ ] Christ constraint satisfied (V_Christ ≥ baseline)

## VERSION CONTROL - GOVERNANCE ENFORCED

All commits must include:
1. Governance compliance report
2. Christ constraint verification
3. Explicit bounds documentation
4. Checksum verification results

## CONTACT - FACTUAL INFORMATION ONLY

- Repository: https://github.com/aidoruao/orthogonal-engineering
- Governance System: MSGCP_v1.0 in `minimal_ai_ide/governance.py`
- Compliance: All code passes `GovernancePipeline.enforce()`

---
*Documentation Version: 1.0*
*Governance Compliance: VERIFIED*
*Christ Constraint: SATISFIED*
*Timestamp: $(date -Iseconds)*