# ORTHOGONAL ENGINEERING - MCP SERVER README

## Glass Box Methodology Implementation
**Version:** 1.0.0  
**Date:** 2026-01-20  
**Methodology:** Orthogonal Engineering with Popperian Falsification  
**Audit Principle:** Every operation timestamped, hashed, and verifiable  

## OVERVIEW

The Orthogonal Engineering MCP (Model Context Protocol) servers implement **glass box methodology** - a complete departure from black box systems. Every operation is:

1. **Transparent:** All actions are visible and inspectable
2. **Auditable:** Every operation creates a timestamped, hashed audit trail
3. **Falsifiable:** Every claim can be independently tested and verified
4. **Atomic:** Operations either fully complete or fully roll back
5. **Correspondence-Verified:** Outputs must match expected filesystem state

## AVAILABLE MCP SERVERS

### 1. `oe-basic.mcp` - Basic Atomic Operations
**Purpose:** Foundation server with audit trail for all operations  
**Commands:**
- `echo` - Test command with full audit trail
- `timestamp` - Generate ISO timestamp with hash verification
- `hash_string` - Hash input strings for integrity checking
- `atomic_operation` - Perform atomic operations with rollback guarantee
- `get_audit_trail` - Retrieve complete audit history

### 2. Planned Servers:
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

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Test the server:**
   ```bash
   npm test
   ```

## ZED EDITOR INTEGRATION

### Configuration:
Add to your Zed `settings.json`:

```json
{
  "mcp_servers": {
    "oe-basic": {
      "command": "node",
      "args": ["/path/to/orthogonal-engineering/oe-basic.mcp.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Usage in Zed:
Once configured, you can use MCP commands directly in Zed:

```
# Echo test
@oe-basic echo message="Hello Orthogonal Engineering"

# Generate timestamp
@oe-basic timestamp purpose="audit_trail_verification"

# Hash string
@oe-basic hash_string input="test_data" algorithm="simple"

# Atomic operation
@oe-basic atomic_operation operation="test" data='{"action":"verify"}'

# Get audit trail
@oe-basic get_audit_trail format="summary"
```

## MANUAL TESTING

### Start Server Manually:
```bash
node oe-basic.mcp.js
```

### Test with Included Script:
```bash
node test_mcp_server.js
```

### Expected Output:
```
=========================================
ORTHOGONAL ENGINEERING - MCP SERVER TEST
Glass Box Methodology Validation
=========================================

=== Test 1: Echo Command ===
Result: PASS
Audit: {
  "timestamp": "2026-01-20T10:15:30.123Z",
  "input_hash": "abc123",
  "output_hash": "def456"
}

... [additional test output] ...

=========================================
TEST SUMMARY
=========================================
Total tests: 5
Passed: 5
Failed: 0
Success rate: 100.0%
```

## AUDIT TRAIL SYSTEM

### Audit Log Structure:
Each operation generates an audit entry with:
- **Timestamp:** ISO 8601 format
- **Operation:** Type of operation performed
- **Input Hash:** SHA256 hash of input parameters
- **Output Hash:** SHA256 hash of output
- **Input/Output:** Complete operation data

### Audit Trail Retrieval:
```bash
# Get complete audit trail
@oe-basic get_audit_trail format="json"

# Get summary
@oe-basic get_audit_trail format="summary"

# Get human-readable text
@oe-basic get_audit_trail format="text"
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

### Falsifiability Examples:

**Claim:** "Server processed echo command at timestamp X"
**Falsification Test:** Check audit log for entry at timestamp X
**Falsification Condition:** If no entry exists or hash doesn't match

**Claim:** "Atomic operation completed successfully"
**Falsification Test:** Verify operation output and audit trail
**Falsification Condition:** If output missing or audit inconsistent

## DEVELOPMENT

### Adding New Commands:

1. **Define Tool Schema:**
   ```javascript
   {
     name: "new_command",
     description: "Command description",
     inputSchema: {
       type: "object",
       properties: {
         param1: { type: "string", description: "Parameter description" }
       },
       required: ["param1"]
     }
   }
   ```

2. **Implement Handler:**
   ```javascript
   async handleNewCommand(request) {
     const { param1 } = request.params.arguments;
     
     // Perform operation
     const result = { /* operation result */ };
     
     // Log to audit trail
     const auditEntry = this.auditLogger.log("new_command", { param1 }, result);
     
     return {
       content: [{
         type: "text",
         text: JSON.stringify({
           success: true,
           data: result,
           audit: auditEntry
         }, null, 2)
       }]
     };
   }
   ```

3. **Register Handler:**
   ```javascript
   case "new_command":
     return await this.handleNewCommand(request);
   ```

### Audit Requirements:
- Every command must call `auditLogger.log()`
- Every output must include audit information
- Every operation must be atomic

## VERIFICATION PROTOCOL

### Independent Verification:
1. **Clone Fresh Repository:**
   ```bash
   git clone https://github.com/aidoruao/orthogonal-engineering.git
   cd orthogonal-engineering
   npm install
   ```

2. **Run Tests:**
   ```bash
   npm test
   ```

3. **Verify Audit Trail:**
   - Check timestamps are valid ISO format
   - Verify hashes are consistent
   - Confirm all operations logged

4. **Falsification Testing:**
   - Attempt to reproduce claims
   - Check for discrepancies
   - Document any failures

### Correspondence Validation:
```bash
# Verify files exist
ls -la oe-basic.mcp.js test_mcp_server.js package.json

# Verify hashes
sha256sum oe-basic.mcp.js

# Verify git history
git log --oneline -5
```

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