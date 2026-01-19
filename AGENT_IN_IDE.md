# Agent-in-IDE Integration Profile

**How Orthogonal Engineering applies to AI agents operating inside IDEs (like Cursor)**

## Overview

This document defines how the Orthogonal Engineering methodology maps to the **causal loop** of an IDE-integrated AI agent, making the methodology **machine-actionable** rather than just descriptive.

---

## The Agent Loop

### Formal State Machine

```
idle → planning → executing → validating → complete
                          ↓         ↓
                       failed ←────┘
```

**States:**
- **idle**: Waiting for user input
- **planning**: Analyzing user intent, selecting canals/invariants
- **executing**: Performing tool calls (edit_file, grep, run_test, etc.)
- **validating**: Checking invariants (lints, tests, user constraints)
- **complete**: All invariants pass, task done
- **failed**: Invariant violation detected, mitigation needed

See `ontology/orthogonal_ontology.json` for formal schema.

---

## Layer Mapping: LLM Output → IDE Agent Actions

### Layer 0: Input Canal (Pre-Generation)

**In LLM context:** Shape the prompt before generation.

**In IDE agent context:** 
- Extract **user constraints** from query
- Identify **required invariants** (no new lints, tests pass, etc.)
- Select **canal templates** (regex patterns, AST transforms, schema validators)

**Example:**
```python
# Agent receives: "Fix the bug in user_controller.py"
# Pre-processing (Layer 0):
constraints = {
    "no_new_lints": True,
    "tests_pass": True,
    "preserve_existing_api": True
}
canal = select_canal("bug_fix", constraints)
```

### Layer 1: Raw Output

**In LLM context:** Verbose, drift-filled response.

**In IDE agent context:**
- **Tool call outputs** (file contents, grep results, test outputs)
- **May contain drift:** irrelevant files, false positives, noise

**Example:**
```python
# Agent reads file, gets:
file_content = """
# ... actual code ...
# TODO: fix this later
# ... more code ...
"""
# Drift: TODO comments, unrelated code sections
```

### Layer 2: Post-Processing & Extraction

**In LLM context:** Extract `[INVARIANT]` tags.

**In IDE agent context:**
- Extract **structural invariants** from tool outputs
- Apply **canal patterns** (regex, AST, schema validation)
- Route **drift** (irrelevant files, noise) away from analysis

**Example:**
```python
# Extract only function definitions (invariant)
import ast
tree = ast.parse(file_content)
functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
# Drift (comments, TODOs) routed away
```

### Layer 3: Raised Fields (Templates & Structure)

**In LLM context:** Structured output templates.

**In IDE agent context:**
- **Type-checked edits** (Pydantic models, TypeScript types)
- **Schema-validated outputs** (JSON schemas, GraphQL)
- **Test-driven structure** (tests define expected shape)

**Example:**
```python
from pydantic import BaseModel

class EditAction(BaseModel):
    file: str
    line_start: int
    line_end: int
    replacement: str
    
    @validator('replacement')
    def validate_syntax(cls, v):
        # Canal: syntax errors routed away
        compile(v, '<string>', 'exec')
        return v
```

### Layer 4: Iterative Refinement

**In LLM context:** Use extracted invariant as seed for next query.

**In IDE agent context:**
- **Validation loop:** Edit → Check invariants → If fail, refine
- **Evidence accumulation:** Each step builds causal trace
- **Failure recovery:** Detect failure mode → Apply mitigation → Retry

---

## Required Invariants (Always Check)

After **every** edit action, agent must check:

### 1. No New Lints (`no_new_lints`)

**Invariant:** No new syntax or style errors introduced.

**Check:**
```python
def check_no_new_lints(file_path: str) -> Evidence:
    before = read_lints(file_path)  # Before edit
    # ... perform edit ...
    after = read_lints(file_path)   # After edit
    
    new_errors = set(after) - set(before)
    return Evidence(
        invariant_id="no_new_lints",
        result="pass" if len(new_errors) == 0 else "fail",
        details=new_errors
    )
```

**Mitigation if fail:** Rollback edit, add constraints, ask user.

### 2. Tests Pass (`tests_pass`)

**Invariant:** Existing functionality preserved.

**Check:**
```python
def check_tests_pass() -> Evidence:
    result = run_tests()
    return Evidence(
        invariant_id="tests_pass",
        result="pass" if result.exit_code == 0 else "fail",
        details=result.output
    )
```

**Mitigation if fail:** Rollback, add tests, ask user.

### 3. User Constraints Met (`user_constraints`)

**Invariant:** User-stated requirements preserved.

**Check:**
```python
def check_user_constraints(user_query: str, edit: EditAction) -> Evidence:
    # Extract constraints from query
    constraints = extract_constraints(user_query)
    # Validate edit meets constraints
    met = all(constraint.validate(edit) for constraint in constraints)
    return Evidence(
        invariant_id="user_constraints",
        result="pass" if met else "fail"
    )
```

**Mitigation if fail:** Refine edit, ask for clarification.

---

## Evidence Schema (Causal Trace)

Every agent action must produce an **Evidence** object:

```json
{
  "action_id": "uuid",
  "timestamp": "2026-01-19T01:00:00Z",
  "action_type": "edit_file",
  "inputs": {
    "file": "user_controller.py",
    "user_query": "Fix the bug",
    "prior_state": {...}
  },
  "assumptions": [
    "Bug is in authentication logic",
    "No API changes needed"
  ],
  "transformation": {
    "canal_id": "bug_fix_canal",
    "invariant_id": "no_new_lints",
    "pattern": "regex_replace"
  },
  "invariants_checked": [
    {
      "invariant_id": "no_new_lints",
      "check_type": "read_lints",
      "result": "pass"
    },
    {
      "invariant_id": "tests_pass",
      "check_type": "run_tests",
      "result": "pass"
    }
  ],
  "outputs": {
    "file_edited": "user_controller.py",
    "lines_changed": [45, 46]
  },
  "outcome": "success"
}
```

**Why this matters:** The entire agent session becomes a **causal trace**, not just a chat log. Every answer can be explained: "I did X because Y, checked Z, and got result R."

---

## Failure Mode Detection & Mitigation

Map `FAILURES.md` to **runtime guards**:

### Example: "Hallucinated Code"

**Detection:**
```python
def detect_hallucination(edit: EditAction) -> bool:
    # Check if referenced functions exist
    for func_call in extract_function_calls(edit.replacement):
        if not function_exists(func_call):
            return True  # Hallucination detected
    return False
```

**Mitigation Policy:**
```python
if detect_hallucination(edit):
    mitigation = {
        "action": "ask_user",
        "parameters": {
            "message": "Referenced function not found. Should I create it?"
        }
    }
```

---

## Canal Templates for IDE Agents

### 1. Regex-Based Canal (Simple Extraction)

```python
def extract_invariant_regex(content: str, pattern: str) -> str:
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None

# Usage:
code_block = extract_invariant_regex(
    llm_output,
    r'```python\n(.*?)\n```'
)
```

### 2. AST-Based Canal (Structural Extraction)

```python
import ast

def extract_functions_ast(content: str) -> List[ast.FunctionDef]:
    tree = ast.parse(content)
    return [node for node in ast.walk(tree) 
            if isinstance(node, ast.FunctionDef)]
```

### 3. Schema-Based Canal (Type-Safe Extraction)

```python
from pydantic import BaseModel, validator

class CodeEdit(BaseModel):
    file: str
    replacement: str
    
    @validator('replacement')
    def validate_syntax(cls, v):
        compile(v, '<string>', 'exec')
        return v
```

---

## Integration Checklist

For an IDE agent to be "truly legit" under Orthogonal Engineering:

- [ ] **Formal ontology** implemented (`ontology/orthogonal_ontology.json`)
- [ ] **Evidence logging** for every action
- [ ] **Invariant checks** after every edit (lints, tests, constraints)
- [ ] **Failure mode detection** with mitigation policies
- [ ] **Canal templates** for common extraction patterns
- [ ] **State machine** enforcement (idle → planning → executing → validating)
- [ ] **Causal trace** generation (full Evidence chain)

---

## Example: Complete Agent Loop

```python
# 1. User query
user_query = "Fix the bug in user_controller.py"

# 2. Planning (Layer 0)
constraints = extract_constraints(user_query)
canal = select_canal("bug_fix", constraints)
plan = create_plan(user_query, canal)

# 3. Executing
evidence_chain = []
for action in plan:
    # Perform action
    result = execute_action(action)
    
    # Check invariants (Layer 2)
    evidence = Evidence(
        action_id=action.id,
        invariants_checked=[
            check_no_new_lints(action.file),
            check_tests_pass(),
            check_user_constraints(user_query, action)
        ]
    )
    evidence_chain.append(evidence)
    
    # If invariant violation, apply mitigation
    if not all(e.result == "pass" for e in evidence.invariants_checked):
        mitigation = detect_failure_mode(evidence)
        apply_mitigation(mitigation)
        # Retry or ask user

# 4. Complete
return {
    "outcome": "success",
    "evidence_chain": evidence_chain,
    "causal_explanation": generate_explanation(evidence_chain)
}
```

---

## Next Steps

1. **Implement ontology** in agent codebase
2. **Add evidence logging** to all tool calls
3. **Wire invariant checks** into edit actions
4. **Test failure modes** and mitigation policies
5. **Generate causal traces** for user queries

See `ontology/orthogonal_ontology.json` for formal schema definitions.
