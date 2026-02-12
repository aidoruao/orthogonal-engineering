# AI Test Generation Instructions for LoRA Training System

## Overview

This document provides instructions for AI agents (including IDE AIs) on how to generate and execute tests for the LoRA training system. The goal is to prevent test script explosion while maintaining comprehensive validation through a structured, stage-aware approach.

## Core Principles

1. **Stage-Aware Testing**: Only generate tests at appropriate LoRA training stages
2. **Single Harness**: Use the unified test harness instead of creating many small scripts
3. **Output Limits**: Respect script and line count limits
4. **Feedback Loop**: Read and update system status to avoid redundant tests
5. **Constraint Preservation**: Ensure all tests respect theological and governance constraints

## LoRA Training Stages

### Stage 0: Setup
- **Purpose**: Initial setup and configuration
- **Test Generation**: NOT ALLOWED
- **Actions**: Environment validation only

### Stage 1: Small Validation
- **Purpose**: Validate setup before full training
- **Test Generation**: ALLOWED (max 2 scripts, 100 lines each)
- **Tests**: Dataset validation, model loading tests

### Stage 2: Full LoRA Run
- **Purpose**: Execute full LoRA training
- **Test Generation**: NOT ALLOWED
- **Actions**: Training execution only

### Stage 3: Post-Train Evaluation
- **Purpose**: Validate trained model and governance
- **Test Generation**: ALLOWED (max 3 scripts, 150 lines each)
- **Tests**: Model validation, governance compliance, constraint preservation

## File Structure

```
minimal_ai_ide/lora/
├── system_status.json          # Tracks current stage and test history
├── test_harness.py            # Unified test harness (MAIN ENTRY POINT)
├── test_cases_registry.json   # Registry of all test cases
└── AI_TEST_GENERATION_INSTRUCTIONS.md  # This file
```

## How to Generate Tests

### Step 1: Check Current Stage
Before generating any tests, always check the current stage:

```python
import json

def check_test_generation_allowed():
    with open('lora/system_status.json', 'r') as f:
        status = json.load(f)
    
    current_stage = status['lora_training_stage']
    stage_info = status['stage_definitions'][str(current_stage)]
    
    if not stage_info['allowed_test_generation']:
        return False, f"Test generation not allowed at stage {current_stage}"
    
    # Check generation count limit
    gen_count = status.get('test_generation_count', 0)
    max_scripts = stage_info.get('max_test_scripts', 0)
    
    if gen_count >= max_scripts:
        return False, f"Test generation limit reached ({gen_count}/{max_scripts})"
    
    return True, f"Test generation allowed at stage {current_stage}"
```

### Step 2: Use the Test Harness (Preferred Method)
Instead of creating new test scripts, add test cases to the harness:

```python
# Example: Adding a new test case to the harness
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

### Step 3: Implement Test Function
If adding a new test case, implement the corresponding function in the harness:

```python
def test_custom_validation(self):
    """Custom validation test implementation"""
    # Your test logic here
    # Use existing infrastructure where possible
    # Keep under line limit (100 lines for stage 1, 150 for stage 3)
    
    # Example: Check model file integrity
    model_path = "trained_lora/adapter_model.safetensors"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Add validation logic
    print("✓ Custom validation passed")
```

### Step 4: Run Tests Through Harness
Execute tests using the harness CLI:

```bash
# Run tests for current stage
python lora/test_harness.py run

# Update to next stage (when appropriate)
python lora/test_harness.py update-stage --stage 1 --desc "Setup complete"

# List all test cases
python lora/test_harness.py list

# Check if test generation is allowed
python lora/test_harness.py check-generation
```

## When to Create New Test Scripts (Rare Cases)

Only create new test scripts when:
1. The test cannot be integrated into the harness (very rare)
2. You have explicit permission to bypass limits
3. The test is a one-time diagnostic tool

If you must create a new script:

### Script Creation Rules:
1. **Naming**: `diagnostic_<purpose>_<timestamp>.py`
2. **Size Limit**: Max 100 lines for stage 1, 150 lines for stage 3
3. **Self-Cleaning**: Script should clean up after itself
4. **Status Update**: Update `system_status.json` after generation

```python
# Template for diagnostic script
"""
Diagnostic Script: [Purpose]
Created: [Timestamp]
Stage: [Current Stage]
Purpose: [Brief description]
"""

import os
import json
from datetime import datetime

def update_generation_count():
    """Update test generation count in system status"""
    with open('lora/system_status.json', 'r') as f:
        status = json.load(f)
    
    status['test_generation_count'] = status.get('test_generation_count', 0) + 1
    status['last_test_generation'] = datetime.now().isoformat()
    
    with open('lora/system_status.json', 'w') as f:
        json.dump(status, f, indent=2)

def main():
    # Your diagnostic logic here
    # Keep it concise and focused
    
    # Update generation count
    update_generation_count()
    
    print("Diagnostic complete")

if __name__ == "__main__":
    main()
```

## Output Limits Enforcement

### Stage 1 (Small Validation):
- Max 2 test scripts total
- Max 100 lines per script
- Total test generation count tracked

### Stage 3 (Post-Train Evaluation):
- Max 3 test scripts total  
- Max 150 lines per script
- Total test generation count tracked

### Global Limits:
- Max 10 total test scripts across all stages
- All tests must use the harness when possible
- Violations will trigger governance alerts

## Feedback Loop Implementation

Always implement a feedback loop:

1. **Before generating**: Check `system_status.json` for current stage and generation count
2. **During execution**: Use existing test results to avoid redundant tests
3. **After completion**: Update `system_status.json` with results
4. **For failures**: Log detailed errors for future reference

```python
def implement_feedback_loop():
    """Example of proper feedback loop implementation"""
    
    # 1. Check before generating
    allowed, message = check_test_generation_allowed()
    if not allowed:
        print(f"Skipping test generation: {message}")
        return
    
    # 2. Check previous results
    with open('lora/system_status.json', 'r') as f:
        status = json.load(f)
    
    last_results = status.get('last_test_results')
    if last_results and last_results.get('passed', 0) == last_results.get('total_tests', 0):
        print("Previous tests all passed, no need for new tests")
        return
    
    # 3. Execute test
    # ... test logic ...
    
    # 4. Update status
    status['last_test_results'] = {
        'timestamp': datetime.now().isoformat(),
        'passed': True,  # or False
        'details': 'Test completed successfully'
    }
    
    with open('lora/system_status.json', 'w') as f:
        json.dump(status, f, indent=2)
```

## Constraint Preservation

All tests must respect:

### Theological Constraints:
- **LOGOS**: Structural integrity and coherence
- **CHALCEDON**: Duality preservation (human/divine, train/eval)
- **GRACE**: Error tolerance and recovery

### Governance Constraints:
- **MAX_TRAINING_HOURS**: 24 hours maximum
- **MAX_MODEL_SIZE_GB**: 10 GB maximum  
- **TYPE_SAFETY**: All functions strictly typed
- **ZERO_TRUST**: Verify before training

### Test-Specific Constraints:
- **SETUP_INTEGRITY**: Environment validation
- **DATA_INTEGRITY**: Dataset validation
- **MODEL_INTEGRITY**: Model validation
- **GOVERNANCE**: Compliance checking
- **CONSTRAINT_PRESERVATION**: Constraint verification

## Best Practices

1. **Reuse Existing Tests**: Check the test registry before creating new tests
2. **Keep Tests Focused**: Each test should validate one specific aspect
3. **Use Descriptive Names**: Clear names for test cases and functions
4. **Include Error Handling**: Graceful failure with informative messages
5. **Clean Up Resources**: Remove temporary files and resources
6. **Document Assumptions**: Clearly state what each test assumes
7. **Respect Line Limits**: Concise, focused code under limit
8. **Update Documentation**: Keep test documentation current

## Emergency Override (Use Sparingly)

Only use emergency override when:
- System is in a broken state
- Standard validation is failing
- Manual intervention is required
- You have explicit approval

```python
# Emergency diagnostic template
"""
EMERGENCY DIAGNOSTIC - MANUAL OVERRIDE
Reason: [Explain why override is needed]
Approval: [Reference approval if any]
"""

# Emergency logic here
# This bypasses normal limits and constraints
# Use extreme caution
```

## Summary

The key to successful test generation in this system is:

1. **Stage Awareness**: Know which stage you're in
2. **Harness First**: Use the unified test harness whenever possible
3. **Respect Limits**: Stay within script and line count limits
4. **Feedback Loop**: Read and update system status
5. **Constraint Preservation**: Respect all theological and governance constraints

By following these instructions, you'll help maintain a clean, efficient testing environment that supports LoRA training without causing script explosion or resource waste.

---
*Last Updated: 2025-01-28*
*System Version: LoRA Test Harness v1.0*