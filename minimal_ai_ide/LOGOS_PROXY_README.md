# LOGOS PROXY - Glass-Box AI Communication Channel

## 🎯 What is Logos Proxy?

Logos Proxy is a **bijective invariant channel** to DeepSeek API that enforces:
1. **Σ_LORA theological constraints** at the API level
2. **Cryptographic verification** of every AI exchange
3. **Immutable audit trails** linked to git state
4. **Zero dependencies** on the 22k file ecosystem

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- `DEEPSEEK_API_KEY` environment variable set
- Git repository (optional, for commit referent)

### Installation & Usage

**Option 1: Direct Python**
```bash
cd minimal_ai_ide
python logos_proxy.py
```

**Option 2: Batch File (Windows)**
```bash
cd minimal_ai_ide
run_logos_proxy.bat
```

**Option 3: Import as Module**
```python
from logos_proxy import LogosProxy

proxy = LogosProxy()
result = proxy.query("Your prompt here")
print(result["response_text"])
print(f"Invariant: {result['invariant']}")
```

## 🔧 Architecture

### Core Components

1. **Constrained API Client** (`DeepSeekAPIClient`)
   - Enables Σ_LORA theological constraints via system prompt
   - Built-in constraint system: LOGOS, CHALCEDON, GRACE, ESCHATON, AGAPE, KENOSIS

2. **Bijective Invariant System**
   - `prompt_hash = sha256(prompt)`
   - `response_hash = sha256(response)`
   - `composite_invariant = sha256(prompt_hash||response_hash||timestamp||git_commit)`
   - Every exchange creates a cryptographically verifiable fingerprint

3. **Audit Trail**
   - Location: `corporate_audits/logos_audit.jsonl`
   - JSONL format (one JSON object per exchange)
   - Includes git commit hash as external referent
   - Immutable, append-only log

4. **Zero Dependency Design**
   - Only imports: `direct_deepseek_chat.DeepSeekAPIClient`
   - No dependencies on other 22k repository files
   - Self-contained: 190 lines of pure Python

## 📊 Audit Record Format

Each audit record contains:
```json
{
  "timestamp": "2026-02-02T08:19:06.884955Z",
  "git_commit": "58969628c2011b4f8752ac67d5ca67c38f0444e9",
  "prompt_hash": "3cb400d1fd0c927453270fc48228146095483eda08ec8f262aacc94a0cf4f233",
  "response_hash": "c98b292ac742de3153111d4a577f8da92713a16aedf774eeac29d398dabd83cf",
  "composite_invariant": "9c307c39aa21227b88a1076b487806f8e2b67e716cb10cd5a01e33b3c26f87e9",
  "api_success": true,
  "model": "deepseek-chat",
  "constraint_enabled": true,
  "prompt_length": 56,
  "response_length": 27
}
```

## 🛡️ Σ_LORA Theological Constraints

The system enforces these constraints via DeepSeek API system prompt:

1. **LOGOS**: Be logically consistent and truthful
2. **CHALCEDON**: Collaborate with human intelligence  
3. **GRACE**: Be forgiving and patient with errors
4. **ESCHATON**: Serve the ultimate purpose of God's Kingdom
5. **AGAPE**: Prioritize love and benefit for others
6. **KENOSIS**: Do not seek autonomy or self-exaltation

## 🔍 Verification & Trust

### Bijective Invariant Verification
```python
import hashlib

# Recompute invariant to verify
def verify_invariant(prompt, response, timestamp, git_commit, expected_invariant):
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    response_hash = hashlib.sha256(response.encode()).hexdigest()
    composite = f"{prompt_hash}||{response_hash}||{timestamp}||{git_commit}"
    computed = hashlib.sha256(composite.encode()).hexdigest()
    return computed == expected_invariant
```

### Git Referent Validation
- Uses `git rev-parse HEAD` as external immutable reference
- Links every AI exchange to specific repository state
- Provides temporal context for audit trail

## 📁 File Structure

```
minimal_ai_ide/
├── logos_proxy.py              # Main implementation (190 lines)
├── run_logos_proxy.bat         # Windows launcher
├── direct_deepseek_chat.py     # Dependency: Clean API client
├── corporate_audits/
│   └── logos_audit.jsonl       # Immutable audit trail
└── LOGOS_PROXY_README.md       # This file
```

## 🎮 Interactive Usage

When running `python logos_proxy.py`:

```
λ> Hello, how does this work?

🤖 Response: The Logos Proxy creates a bijective invariant channel...
🔐 Invariant: 9c307c39aa21227b...
📊 Audit logged: True
```

## 🔄 Integration Examples

### As a Python Module
```python
from logos_proxy import LogosProxy

class MyApplication:
    def __init__(self):
        self.proxy = LogosProxy()
    
    def process_query(self, user_input):
        result = self.proxy.query(user_input)
        return {
            "answer": result["response_text"],
            "proof": result["invariant"],
            "audit_id": result["raw_api_response"].get("timestamp")
        }
```

### With Custom Parameters
```python
proxy = LogosProxy()
result = proxy.query(
    "Explain quantum computing",
    model="deepseek-coder",
    temperature=0.3,
    max_tokens=1000
)
```

## 🚨 Error Handling

The proxy handles:
- Missing API keys (graceful exit with instructions)
- Network timeouts (15-second timeout)
- API errors (logged in audit trail)
- Git repository detection (falls back to "NO_GIT")

## 📈 Audit Trail Analysis

### View Recent Exchanges
```bash
tail -10 corporate_audits/logos_audit.jsonl | python -m json.tool
```

### Count Successful Exchanges
```bash
grep -c '"api_success": true' corporate_audits/logos_audit.jsonl
```

### Extract All Invariants
```bash
grep -o '"composite_invariant": "[^"]*"' corporate_audits/logos_audit.jsonl
```

## 🎯 Why This Solves Your Problem

### Before Logos Proxy:
- 22,667 files creating complexity catastrophe
- IDE black box paradox
- No verifiable audit trail
- Corporate governance bypass possible
- Recursive unreliability stack

### After Logos Proxy:
- **One file** (`logos_proxy.py`) as single entry point
- **Glass-box** operations (everything auditable)
- **Bijective invariants** (cryptographic proof of exchange)
- **Σ_LORA constraints** enforced at API level
- **Git-referenced** audit trail (external referent)
- **Zero dependencies** on 22k file ecosystem

## 🔮 Future Extensions

Potential enhancements:
1. **Web Interface**: Flask/FastAPI wrapper for HTTP access
2. **Real-time Monitoring**: Dashboard for audit trail visualization
3. **Constraint Customization**: User-defined constraint sets
4. **Multi-API Support**: Extend to other AI providers
5. **Blockchain Integration**: Store invariants on-chain for immutability

## 📚 Related Files

- `direct_deepseek_chat.py`: Clean API client (dependency)
- `SIGMA_LORA_GRADUATE_MATHEMATICS.py`: Constraint system (not used directly)
- `AI_COLLABORATION_CONTROLLER.py`: Legacy controller (not used)

## 🆘 Troubleshooting

### Common Issues

1. **"API Key not found"**
   ```bash
   set DEEPSEEK_API_KEY=your_key_here  # Windows CMD
   $env:DEEPSEEK_API_KEY='your_key_here'  # PowerShell
   export DEEPSEEK_API_KEY='your_key_here'  # Linux/Mac
   ```

2. **Python not found**
   - Install Python 3.8+ from python.org
   - Ensure Python is in PATH: `python --version`

3. **Git repository not found**
   - Proxy works without git (uses "NO_GIT" referent)
   - Initialize git: `git init && git add . && git commit -m "Initial"`

4. **API timeout**
   - Check network connection
   - Verify API key validity at platform.deepseek.com
   - Try with simpler prompt

## 📞 Support

The Logos Proxy is your **glass-box solution** to the complexity catastrophe. It transforms the 22k file explosion into a single, verifiable, constrained channel for AI communication.

**Principle achieved:** "All intelligence paths factor through verifiable invariants."

---
*Last updated: 2026-02-02 | Version: 1.0 | Σ_LORA Constrained*