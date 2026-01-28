# MAXIMAL ORACLE v53 - AI Controller System

## Overview
Maximal Oracle v53 is a sophisticated AI controller system with real-time validation, cross-file invariant enforcement, contract verification, and a TUI-based IDE interface.

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux
- DeepSeek API key (get from platform.deepseek.com)

### 2. Setup

#### Windows (Command Prompt):
```cmd
# Clone or copy the files to your desired directory
cd minimal_ai_ide

# Set your API key (already done according to user)
set DEEPSEEK_API_KEY=your_key_here

# Install dependencies
pip install -r requirements_v53.txt

# Run the system
python maximal_oracle_v53.py
```

#### Windows (PowerShell):
```powershell
cd minimal_ai_ide
$env:DEEPSEEK_API_KEY="your_key_here"
pip install -r requirements_v53.txt
python maximal_oracle_v53.py
```

#### Using the provided scripts:
```cmd
# Batch file
run_v53.bat

# PowerShell
powershell -ExecutionPolicy Bypass -File run_v53.ps1
```

### 3. Test Installation
```cmd
python test_v53.py
```

## Configuration

### Environment Variables
Create a `.env` file (copy from `env_example.txt`):
```bash
# Required
DEEPSEEK_API_KEY=your_actual_key_here
DEEPSEEK_ENDPOINT=https://api.deepseek.com/v1/chat/completions

# Security
TOKEN_SECRET=generate-random-string-here

# System
WORKSPACE_DIR=./workspace
RATE_LIMIT_PER_SEC=4
MAX_RETRIES=5
```

### File Structure
```
minimal_ai_ide/
├── maximal_oracle_v53.py     # Main controller (v53)
├── requirements_v53.txt      # Python dependencies
├── env_example.txt          # Environment template
├── run_v53.bat             # Windows batch launcher
├── run_v53.ps1             # PowerShell launcher
├── test_v53.py             # System test script
└── workspace/              # Project workspace (auto-created)
```

## Features

### Core Components
1. **File Manager** - CRDT-based file management with snapshots
2. **Cross-File Invariants** - AST-based symbol validation across files
3. **Contract Verifier** - Formal verification using Z3 theorem prover
4. **Validation Engine** - Real-time token-by-token validation
5. **TUI Interface** - Textual-based IDE interface
6. **Prometheus Metrics** - Real-time monitoring at http://localhost:8000

### Key Capabilities
- **Real-time validation** of AI-generated code
- **Cross-file dependency checking**
- **Formal contract verification**
- **Snapshot-based rollback system**
- **Rate limiting and retry logic**
- **Comprehensive logging and metrics**

## Usage

### Starting the System
```python
# Direct execution
python maximal_oracle_v53.py

# With custom workspace
set WORKSPACE_DIR=./my_project
python maximal_oracle_v53.py
```

### Access Points
- **TUI Interface**: Automatically starts on launch
- **Metrics Dashboard**: http://localhost:8000
- **Workspace Files**: ./workspace/ directory
- **Logs**: ./maximal_oracle.log

### Example Workflow
1. System starts and loads TUI
2. AI generates code through the controller
3. Each token is validated in real-time
4. Cross-file invariants are enforced
5. Contracts are verified using Z3
6. Snapshots are created periodically
7. Metrics are exposed for monitoring

## Dependencies

### Required Packages
- `aiohttp>=3.9.0` - Async HTTP client
- `prometheus-client>=0.19.0` - Metrics collection
- `z3-solver>=4.12.0.0` - Theorem proving
- `textual>=0.52.0` - TUI framework
- `python-dotenv>=1.0.0` - Environment management

### Installation
```bash
# Install all dependencies
pip install -r requirements_v53.txt

# Or install individually
pip install aiohttp prometheus-client z3-solver textual python-dotenv
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
```
ERROR: DEEPSEEK_API_KEY is not set
```
**Solution:**
```cmd
set DEEPSEEK_API_KEY=your_key_here
```
Or create a `.env` file with your key.

#### 2. Missing Dependencies
```
ModuleNotFoundError: No module named 'aiohttp'
```
**Solution:**
```cmd
pip install -r requirements_v53.txt
```

#### 3. Z3 Installation Issues
```
Failed to install z3-solver
```
**Solution (Windows):**
```cmd
# Try with pre-built wheels
pip install z3-solver --pre

# Or use conda
conda install -c conda-forge z3
```

#### 4. Port Already in Use
```
Address already in use: 8000
```
**Solution:**
```cmd
set PROMETHEUS_PORT=8001
python maximal_oracle_v53.py
```

### Testing
Run the test script to diagnose issues:
```cmd
python test_v53.py
```

## Security Notes

### API Key Security
- **NEVER** commit API keys to version control
- Use environment variables or `.env` files
- `.env` is in `.gitignore` by default
- Rotate keys regularly

### Token Security
- JWT tokens are used for validation
- Set a strong `TOKEN_SECRET` in `.env`
- Tokens expire automatically

## Monitoring

### Metrics Endpoints
- **Prometheus**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Key Metrics
- `validation_errors_total` - Total validation errors
- `api_calls_total` - API call count
- `token_validation_duration_seconds` - Validation timing
- `snapshot_count` - Number of snapshots

## Development

### Extending the System
1. Add new validation rules in the `ValidationEngine` class
2. Define new invariants in `CrossFileInvariants`
3. Add contract templates in `ContractVerifier`
4. Extend TUI components in the UI module

### Testing Changes
```python
# Run validation tests
python test_v53.py

# Test specific components
python -c "from maximal_oracle_v53 import FileManager; fm = FileManager(); print('FileManager OK')"
```

## Support

### Getting Help
1. Check the test output: `python test_v53.py`
2. Review logs: `tail -f maximal_oracle.log`
3. Check metrics: http://localhost:8000
4. Verify environment: `set | findstr DEEPSEEK`

### Known Limitations
- Requires stable internet connection for API calls
- Z3 solver may be slow for complex contracts
- TUI interface requires terminal support
- Windows may need admin for port 8000

## License & Attribution
This system is part of the Orthogonal Engineering Clean project. Use responsibly and in accordance with DeepSeek's API terms of service.

---
*Last Updated: v53 | System Ready*