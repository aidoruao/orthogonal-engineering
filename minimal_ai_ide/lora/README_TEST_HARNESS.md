# LoRA Test Harness System

## Overview

The LoRA Test Harness System is a structured solution to prevent test script explosion while maintaining comprehensive validation for LoRA training processes. It implements stage-aware test generation, output limits, and feedback loops to ensure efficient and organized testing.

## Quick Start

### 1. Check Current Status
```bash
python lora/test_harness.py check-generation
```

### 2. Run Tests for Current Stage
```bash
python lora/test_harness.py run
```

### 3. Update Training Stage
```bash
python lora/test_harness.py update-stage --stage 1 --desc "Setup complete"
```

### 4. List All Test Cases
```bash
python lora/test_harness.py list
```

## System Architecture

### Core Components

1. **`system_status.json`** - Tracks LoRA training stages and test generation history
2. **`test_harness.py`** - Unified test harness for all validation (main entry point)
3. **`test_cases_registry.json`** - Registry of all test cases organized by stage
4. **`AI_TEST_GENERATION_INSTRUCTIONS.md`** - Guidelines for AI test generation
5. **`demo_test_harness_usage.py`** - Interactive demonstration of system features

### LoRA Training Stages

| Stage | Name | Test Generation | Purpose | Max Scripts | Max Lines |
|-------|------|-----------------|---------|-------------|-----------|
| 0 | Setup | ❌ NOT ALLOWED | Initial setup and configuration | 0 | 0 |
| 1 | Small Validation | ✅ ALLOWED | Validate setup before full training | 2 | 100 |
| 2 | Full LoRA Run | ❌ NOT ALLOWED | Execute full LoRA training | 0 | 0 |
| 3 | Post-Train Evaluation | ✅ ALLOWED | Validate trained model and governance | 3 | 150 |

## How It Works

### For AI Agents (IDE AIs)

1. **Check Permission First**: Always call `check-generation` before creating tests
2. **Use the Harness**: Add test cases to the harness instead of creating new scripts
3. **Respect Limits**: Stay within script and line count limits for each stage
4. **Update Status**: Record test results in the system status
5. **Preserve Constraints**: All tests must respect theological and governance constraints

### For Human Users

1. **Stage Management**: Update stages as training progresses
2. **Test Execution**: Run tests appropriate for each stage
3. **Monitoring**: Check test results and system status
4. **Maintenance**: Add/remove test cases as needed

## Test Case Management

### Adding a New Test Case

```python
from lora.test_harness import LoRATestHarness, TestCase

harness = LoRATestHarness()

new_test = TestCase(
    id="custom_test_1",
    name="Custom Model Validation",
    description="Validate specific model characteristics",
    stage=3,  # Post-training stage
    function_name="test_custom_validation",
    constraints=["LOGOS", "MODEL_INTEGRITY"],
    timeout_seconds=30,
    required=True
)

harness.add_test_case(new_test)
```

### Implementing Test Functions

Test functions must be implemented in the harness or imported modules:

```python
def test_custom_validation(self):
    """Custom validation test implementation"""
    # Test logic here
    # Must respect line limits (100 for stage 1, 150 for stage 3)
    print("✓ Custom validation passed")
```

## Constraint System

### Theological Constraints
- **LOGOS**: Structural integrity and coherence
- **CHALCEDON**: Duality preservation (human/divine, train/eval)
- **GRACE**: Error tolerance and recovery

### Governance Constraints
- **MAX_TRAINING_HOURS**: 24 hours maximum
- **MAX_MODEL_SIZE_GB**: 10 GB maximum
- **TYPE_SAFETY**: All functions strictly typed
- **ZERO_TRUST**: Verify before training

### Test-Specific Constraints
- **SETUP_INTEGRITY**: Environment validation
- **DATA_INTEGRITY**: Dataset validation
- **MODEL_INTEGRITY**: Model validation
- **GOVERNANCE**: Compliance checking
- **CONSTRAINT_PRESERVATION**: Constraint verification

## Best Practices

### 1. Stage Awareness
- Always check current stage before test generation
- Only generate tests at allowed stages (1 and 3)
- Update stage when training progresses

### 2. Test Organization
- Use descriptive test names and IDs
- Group related tests by stage
- Keep tests focused on single responsibilities

### 3. Resource Management
- Clean up temporary files
- Respect line count limits
- Monitor test execution time

### 4. Documentation
- Document test assumptions
- Update test descriptions
- Record test results

## Emergency Procedures

### When to Use Emergency Override
1. System is in a broken state
2. Standard validation is failing
3. Manual intervention is required
4. Explicit approval obtained

### Emergency Diagnostic Template
```python
"""
EMERGENCY DIAGNOSTIC - MANUAL OVERRIDE
Reason: [Explain why override is needed]
Approval: [Reference approval if any]
Timestamp: [Current timestamp]
"""

# Emergency logic here
# This bypasses normal limits and constraints
# Use extreme caution
```

## Troubleshooting

### Common Issues

1. **"Test generation not allowed at stage X"**
   - Check current stage with `check-generation`
   - Update stage if training has progressed
   - Only stages 1 and 3 allow test generation

2. **"Test generation limit reached"**
   - Check generation count in system status
   - Reuse existing test cases when possible
   - Request limit increase if justified

3. **Test failures**
   - Check test error messages
   - Verify system requirements
   - Review constraint violations

4. **Missing dependencies**
   - Install required packages
   - Check Python path
   - Verify file permissions

## Integration with Existing Workflow

### Before Training
```bash
# Stage 0: Setup
python lora/test_harness.py update-stage --stage 0 --desc "Initial setup"

# Stage 1: Small Validation
python lora/test_harness.py update-stage --stage 1 --desc "Setup complete"
python lora/test_harness.py run
```

### During Training
```bash
# Stage 2: Full LoRA Run (no tests)
python lora/test_harness.py update-stage --stage 2 --desc "Training in progress"
```

### After Training
```bash
# Stage 3: Post-Train Evaluation
python lora/test_harness.py update-stage --stage 3 --desc "Training complete"
python lora/test_harness.py run
```

## File Structure

```
minimal_ai_ide/lora/
├── system_status.json          # System state and history
├── test_harness.py            # Main test harness
├── test_cases_registry.json   # Test case registry
├── AI_TEST_GENERATION_INSTRUCTIONS.md  # AI guidelines
├── demo_test_harness_usage.py # Demonstration script
├── TEST_HARNESS_IMPLEMENTATION_SUMMARY.md  # Implementation details
└── README_TEST_HARNESS.md     # This file
```

## Support

### Documentation
- `AI_TEST_GENERATION_INSTRUCTIONS.md` - Detailed AI guidelines
- `TEST_HARNESS_IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `demo_test_harness_usage.py` - Interactive demonstrations

### Testing
- Run `python lora/demo_test_harness_usage.py` for full demonstration
- Use `--section` parameter for specific demonstrations:
  - `stage` - Stage awareness
  - `harness` - Harness usage
  - `feedback` - Feedback loops
  - `constraints` - Constraint preservation
  - `cli` - Command-line interface
  - `emergency` - Emergency procedures

## Benefits

1. **Prevents Script Explosion**: Structured approach eliminates hundreds of small test scripts
2. **Maintains Validation**: Comprehensive testing without clutter
3. **Improves Efficiency**: AI agents work within clear boundaries
4. **Enhances Stability**: Governance and constraint preservation
5. **Provides Visibility**: Clear system status and test history

## Version Information

- **Version**: LoRA Test Harness v1.0
- **Implementation Date**: 2025-01-30
- **Status**: Fully Operational
- **Compatibility**: Works with existing LoRA training infrastructure

---
*For questions or issues, refer to the implementation summary or run the demonstration script.*