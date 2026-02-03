# ORTHOGONAL ENGINEERING - MCP SERVER README

## Glass Box Methodology Implementation
**Version:** 1.1.0 - Protocol Correct  
**Date:** 2026-01-24  
**Methodology:** Orthogonal Engineering with Popperian Falsification  
**Audit Principle:** Every operation timestamped, hashed, and verifiable  
**Protocol Fixes:** Binary mode, byte-safe framing, Windows compatible  

## OVERVIEW

The Orthogonal Engineering MCP (Model Context Protocol) servers implement **glass box methodology** with **protocol-correct MCP framing** - a complete departure from black box systems. Every operation is:

1. **Transparent:** All actions are visible and inspectable
2. **Auditable:** Every operation creates a timestamped, hashed audit trail
3. **Falsifiable:** Every claim can be independently tested and verified
4. **Atomic:** Operations either fully complete or fully roll back
5. **Correspondence-Verified:** Outputs must match expected filesystem state
6. **Protocol-Correct:** Binary mode, byte-safe framing, Windows compatible

## AVAILABLE MCP SERVERS

### 1. `orthogonal_mcp_server.py` - Protocol-Correct Orthogonal MCP
**Purpose:** Foundation server with audit trail and protocol-correct MCP framing  
**Version:** 1.1.0 (Protocol Correct)  
**Protocol Features:** Binary mode, byte-safe framing, Windows compatible  
**Commands:**
- `echo` - Test command with full audit trail
- `timestamp` - Generate ISO timestamp with hash verification
- `hash_evidence` - Hash evidence with SHA256 for integrity verification
- `validate_json` - Validate JSON structure with schema checking
- `check_boundary` - Check glass-box boundary compliance
- `get_audit_trail` - Retrieve complete audit history with evidence hashes

### 2. `oe-basic.mcp` - Basic Atomic Operations (Legacy)
**Purpose:** Original Node.js implementation (may have protocol issues)  
**Status:** Use `orthogonal_mcp_server.py` for protocol-correct operation

### 3. Planned Servers:
- `oe-filesystem.mcp` - Filesystem operations with correspondence validation
- `oe-git.mcp` - Git operations with atomic commit/diff/status
- `oe-inventory.mcp` - Invariant database management

## INSTALLATION

### Prerequisites:
- Node.js 18.0.0 or higher
- Git (for repository operations)
- Zed editor (for MCP integration)

### Installation Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aidoruao/orthogonal-engineering.git
   cd orthogonal-engineering
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the protocol-correct server:**
   ```bash
   cd mcp
   python test_orthogonal_mcp.py
   ```

4. **Verify protocol fixes:**
   ```bash
   # Check test report
   cat mcp/test_report.json | python -m json.tool
   ```

## ZED EDITOR INTEGRATION

### Configuration:
Add to your Zed `settings.json`:

```json
{
  "mcp_servers": {
    "orthogonal-engineering-mcp": {
      "command": "python",
      "args": ["C:\\Users\\Aidor\\Documents\\orthogonal-engineering-clean\\mcp\\orthogonal_mcp_server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Note:** Use absolute path to the Python server for protocol-correct operation.

### Usage in Zed:
Once configured, you can use MCP commands directly in Zed:

```
# Echo test with audit trail
@orthogonal-engineering-mcp echo message="Hello Orthogonal Engineering"

# Generate timestamp with hash
@orthogonal-engineering-mcp timestamp purpose="audit_trail_verification"

# Hash evidence
@orthogonal-engineering-mcp hash_evidence data="test_data" algorithm="sha256"

# Validate JSON
@orthogonal-engineering-mcp validate_json json='{"test": "data"}' schema='{"type": "object"}'

# Check boundary compliance
@orthogonal-engineering-mcp check_boundary component="mcp_server"

# Get audit trail
@orthogonal-engineering-mcp get_audit_trail format="summary"
```

## MANUAL TESTING

### Start Protocol-Correct Server:
```bash
cd orthogonal-engineering-clean/mcp
python orthogonal_mcp_server.py
```

### Test with Protocol-Correct Script:
```bash
cd orthogonal-engineering-clean/mcp
python test_orthogonal_mcp.py
```

### Expected Output:
```
============================================================
ORTHOGONAL MCP SERVER TEST SUITE - FIXED
Subtractive Clarity & Glass-Box Boundary Compliance
Protocol Correct: Binary Mode, Byte-Safe Framing
============================================================

=== Test 1: List Tools ===
✅ Success! Found 6 tools:
   • get_audit_trail (audit): Get glass-box audit trail with evidence hashes
   • validate_json (validation): Validate JSON structure with schema checking
   • hash_evidence (evidence): Hash evidence with SHA256 for integrity verification
   • check_boundary (boundary): Check glass-box boundary compliance
   • echo (utility): Echo input with audit trail - basic connectivity test
   • timestamp (utility): Generate ISO timestamp with hash - for audit synchronization

... [additional test output with audit logs] ...

============================================================
TEST SUMMARY
============================================================
Total tests: 5
Passed: 5
Failed: 0
Success rate: 100.0%

Audit logs captured: 2
  1. [GLASS-BOX AUDIT] 2026-01-24T19:31:00.274500 | server_init | Input: 74c284188e351ad2 | Output: b86abf3096ca6142 | Violation: False
  2. [GLASS-BOX AUDIT] 2026-01-24T19:31:00.274648 | server_start | Input: 80658a5e71ded25b | Output: 409443a6ee5aa296 | Violation: False

🎉 ALL TESTS PASSED!
Orthogonal MCP server is ready for Zed integration.
```

## AUDIT TRAIL SYSTEM

### Audit Log Structure:
Each operation generates an audit entry with:
- **Timestamp:** ISO 8601 format with microseconds
- **Operation:** Type of operation performed
- **Input Hash:** SHA256 hash of input parameters
- **Output Hash:** SHA256 hash of output
- **Input/Output:** Complete operation data
- **Boundary Violation:** Boolean flag for glass-box boundary compliance

### Audit Trail Retrieval:
```bash
# Get complete audit trail
@orthogonal-engineering-mcp get_audit_trail format="json"

# Get summary
@orthogonal-engineering-mcp get_audit_trail format="summary"

# Get human-readable text
@orthogonal-engineering-mcp get_audit_trail format="text"
```

## GLASS BOX METHODOLOGY

### Core Principles:

1. **No Black Boxes:**
   - All code is open and inspectable
   - All operations are logged
   - All outputs are verifiable

2. **Popperian Falsification:**
   - Every claim has explicit falsification test
   - Independent verification possible
   - Discrepancies falsify claims

3. **Atomic Audit Trail:**
   - Every action timestamped
   - Every output hashed
   - Every change committed to git

4. **Correspondence Validation:**
   - Outputs must match filesystem state
   - Hashes must be consistent
   - Claims must be verifiable

5. **Protocol Correctness:**
   - Binary mode MCP framing
   - Byte-safe Content-Length handling
   - Windows compatible operation
   - No text mode ambiguity

### Falsifiability Examples:

**Claim:** "Server processed echo command at timestamp X"
**Falsification Test:** Check audit log for entry at timestamp X
**Falsification Condition:** If no entry exists or hash doesn't match

**Claim:** "Atomic operation completed successfully"
**Falsification Test:** Verify operation output and audit trail
**Falsification Condition:** If output missing or audit inconsistent

**Claim:** "MCP protocol is correctly implemented"
**Falsification Test:** Run `test_orthogonal_mcp.py` and check for hangs
**Falsification Condition:** If tests hang or fail due to protocol violations

**Claim:** "System is Windows compatible"
**Falsification Test:** Run tests on Windows without `fcntl` errors
**Falsification Condition:** If platform-specific failures occur

## DEVELOPMENT

### Protocol Requirements:
- **Binary Mode:** All MCP communication must use binary mode (`sys.stdin.buffer`, `sys.stdout.buffer`)
- **Byte-Safe Framing:** Content-Length must count bytes, not characters
- **Windows Compatibility:** No platform-specific APIs like `fcntl` or `select` on pipes
- **Unbuffered I/O:** Use `bufsize=0` for subprocess communication

### Adding New Commands:

1. **Define Tool Schema (Python):**
   ```python
   {
       "name": "new_command",
       "description": "Command description",
       "category": "utility",  # audit, validation, evidence, boundary, utility
       "inputSchema": {
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Parameter description"}
           },
           "required": ["param1"]
       }
   }
   ```

2. **Implement Handler with Audit Trail:**
   ```python
   def handle_new_command(self, arguments: dict) -> dict:
       param1 = arguments.get("param1")
       
       # Perform operation
       result = {"processed": param1, "status": "success"}
       
       # Log to glass-box audit trail
       audit_entry = self.auditor.log_operation(
           operation="new_command",
           input_data={"param1": param1},
           output_data=result,
           boundary_violation=False
       )
       
       return {
           "success": True,
           "data": result,
           "metadata": {
               "operation": "new_command",
               "timestamp": audit_entry["timestamp"],
               "audit_id": audit_entry["id"]
           }
       }
   ```

3. **Register Handler:**
   ```python
   case "new_command":
       result = self.tools.handle_new_command(arguments)
   ```

### Audit Requirements:
- Every command must call `auditor.log_operation()`
- Every output must include audit metadata
- Every operation must be atomic
- Every boundary violation must be flagged

## VERIFICATION PROTOCOL

### Independent Verification:
1. **Clone Fresh Repository:**
   ```bash
   git clone https://github.com/aidoruao/orthogonal-engineering.git
   cd orthogonal-engineering
   ```

2. **Run Protocol-Correct Tests:**
   ```bash
   cd mcp
   python test_orthogonal_mcp.py
   ```

3. **Verify Audit Trail:**
   - Check timestamps are valid ISO format with microseconds
   - Verify hashes are consistent (SHA

## TROUBLESHOOTING

### Common Issues:

1. **Server Won't Start:**
   - Check Node.js version: `node --version`
   - Verify dependencies: `npm list`
   - Check file permissions

2. **Zed Integration Fails:**
   - Verify Zed settings.json syntax
   - Check path to server file
   - Restart Zed after configuration changes

3. **Audit Trail Missing:**
   - Check server is running with audit logging
   - Verify NODE_ENV is not 'test'
   - Check stderr for audit messages

4. **Hash Verification Fails:**
   - Ensure same input produces same hash
   - Check for whitespace differences
   - Verify encoding (UTF-8)

### Debug Mode:
```bash
# Start server with debug logging
NODE_ENV=debug node oe-basic.mcp.js

# Test with verbose output
DEBUG=* node test_mcp_server.js
```

## SECURITY CONSIDERATIONS

### Audit Trail Security:
- Audit logs should be append-only
- Hashes should use cryptographic algorithms (SHA256)
- Timestamps should be from trusted time source

### Input Validation:
- All inputs must be validated
- No arbitrary code execution
- Sanitize all user-provided data

### Access Control:
- Server should run with minimal privileges
- Audit logs should be protected
- Git operations should use appropriate permissions

## CONTRIBUTING

### Development Workflow:
1. **Fork Repository**
2. **Create Feature Branch**
3. **Implement Changes with Audit Trail**
4. **Add Falsification Tests**
5. **Submit Pull Request**

### Code Standards:
- All code must include audit logging
- All functions must have falsification tests
- All changes must be committed to git
- All claims must be verifiable

### Testing Requirements:
- 100% test coverage for audit functionality
- Falsification tests for all claims
- Correspondence validation for all outputs

## LICENSE

MIT License - See LICENSE file for details.

## CONTACT

- **Repository:** https://github.com/aidoruao/orthogonal-engineering
- **Issues:** https://github.com/aidoruao/orthogonal-engineering/issues
- **Methodology:** Orthogonal Engineering with Popperian Falsification

---

**Glass Box Guarantee:** Every operation in this system is transparent, auditable, and falsifiable. There are no black boxes.