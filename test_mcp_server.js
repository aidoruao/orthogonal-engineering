// test_mcp_server.js - Test script for oe-basic.mcp server
// Orthogonal Engineering - Glass Box Methodology
// Version: 1.0.0
// Date: 2026-01-20

const { spawn } = require('child_process');
const path = require('path');

class MCPClientTest {
  constructor() {
    this.serverProcess = null;
    this.testResults = [];
    this.auditTrail = [];
  }

  // Start the MCP server
  startServer() {
    return new Promise((resolve, reject) => {
      const serverPath = path.join(__dirname, 'oe-basic.mcp.js');

      this.serverProcess = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Capture stderr for audit logs
      this.serverProcess.stderr.on('data', (data) => {
        const log = data.toString().trim();
        if (log.includes('[AUDIT]')) {
          this.auditTrail.push(log);
        }
        console.error(`[SERVER] ${log}`);
      });

      // Wait for server to be ready
      setTimeout(() => {
        console.log('MCP Server started');
        resolve();
      }, 1000);
    });
  }

  // Send JSON-RPC request to server
  sendRequest(method, params) {
    return new Promise((resolve, reject) => {
      const request = {
        jsonrpc: '2.0',
        method,
        params,
        id: Date.now()
      };

      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');

      // Set up response handler
      const onData = (data) => {
        try {
          const response = JSON.parse(data.toString());
          if (response.id === request.id) {
            this.serverProcess.stdout.removeListener('data', onData);
            resolve(response);
          }
        } catch (error) {
          // Not our response, continue listening
        }
      };

      this.serverProcess.stdout.on('data', onData);

      // Timeout after 5 seconds
      setTimeout(() => {
        this.serverProcess.stdout.removeListener('data', onData);
        reject(new Error(`Timeout waiting for response to ${method}`));
      }, 5000);
    });
  }

  // Test 1: Echo command
  async testEcho() {
    console.log('\n=== Test 1: Echo Command ===');

    const testMessage = 'Hello Orthogonal Engineering!';
    const response = await this.sendRequest('tools/call', {
      name: 'echo',
      arguments: {
        message: testMessage
      }
    });

    const result = JSON.parse(response.result.content[0].text);

    const testResult = {
      test: 'echo',
      passed: result.success === true &&
              result.data.echoed_message === testMessage &&
              result.audit.timestamp !== undefined &&
              result.audit.input_hash !== undefined &&
              result.audit.output_hash !== undefined,
      data: result.data,
      audit: result.audit
    };

    this.testResults.push(testResult);
    console.log(`Result: ${testResult.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Audit: ${JSON.stringify(testResult.audit, null, 2)}`);

    return testResult.passed;
  }

  // Test 2: Timestamp generation
  async testTimestamp() {
    console.log('\n=== Test 2: Timestamp Generation ===');

    const purpose = 'test_audit_trail';
    const response = await this.sendRequest('tools/call', {
      name: 'timestamp',
      arguments: {
        purpose
      }
    });

    const result = JSON.parse(response.result.content[0].text);

    // Verify timestamp is valid ISO format
    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
    const isValidISO = isoRegex.test(result.data.iso_timestamp);

    const testResult = {
      test: 'timestamp',
      passed: result.success === true &&
              isValidISO &&
              result.data.purpose === purpose &&
              result.data.hash !== undefined &&
              result.audit.timestamp !== undefined,
      data: result.data,
      audit: result.audit
    };

    this.testResults.push(testResult);
    console.log(`Result: ${testResult.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Timestamp: ${result.data.iso_timestamp}`);
    console.log(`Hash: ${result.data.hash}`);

    return testResult.passed;
  }

  // Test 3: String hashing
  async testHashString() {
    console.log('\n=== Test 3: String Hashing ===');

    const testString = 'Orthogonal Engineering Test String';
    const response = await this.sendRequest('tools/call', {
      name: 'hash_string',
      arguments: {
        input: testString,
        algorithm: 'simple'
      }
    });

    const result = JSON.parse(response.result.content[0].text);

    const testResult = {
      test: 'hash_string',
      passed: result.success === true &&
              result.data.input_length === testString.length &&
              result.data.algorithm === 'simple' &&
              result.data.hash !== undefined &&
              result.audit.input_hash !== undefined,
      data: result.data,
      audit: result.audit
    };

    this.testResults.push(testResult);
    console.log(`Result: ${testResult.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Input length: ${result.data.input_length}`);
    console.log(`Hash: ${result.data.hash}`);

    return testResult.passed;
  }

  // Test 4: Atomic operation
  async testAtomicOperation() {
    console.log('\n=== Test 4: Atomic Operation ===');

    const operationData = {
      action: 'test_operation',
      value: 42,
      metadata: 'test'
    };

    const response = await this.sendRequest('tools/call', {
      name: 'atomic_operation',
      arguments: {
        operation: 'test',
        data: operationData
      }
    });

    const result = JSON.parse(response.result.content[0].text);

    const testResult = {
      test: 'atomic_operation',
      passed: result.success === true &&
              result.data.operation_id.startsWith('atomic_') &&
              result.data.status === 'completed' &&
              result.data.started_at !== undefined &&
              result.data.completed_at !== undefined &&
              result.data.atomic_guarantee !== undefined &&
              result.data.verification_hash !== undefined &&
              result.audit.atomic === true,
      data: result.data,
      audit: result.audit
    };

    this.testResults.push(testResult);
    console.log(`Result: ${testResult.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Operation ID: ${result.data.operation_id}`);
    console.log(`Verification Hash: ${result.data.verification_hash}`);

    return testResult.passed;
  }

  // Test 5: Audit trail retrieval
  async testAuditTrail() {
    console.log('\n=== Test 5: Audit Trail Retrieval ===');

    const response = await this.sendRequest('tools/call', {
      name: 'get_audit_trail',
      arguments: {
        format: 'summary'
      }
    });

    const result = JSON.parse(response.result.content[0].text);

    const testResult = {
      test: 'get_audit_trail',
      passed: result.summary !== undefined &&
              result.summary.total_operations >= 4 && // Should have at least our 4 previous tests
              result.summary.audit_integrity !== undefined,
      data: result,
      audit: 'N/A - This is the audit retrieval itself'
    };

    this.testResults.push(testResult);
    console.log(`Result: ${testResult.passed ? 'PASS' : 'FAIL'}`);
    console.log(`Total operations recorded: ${result.summary.total_operations}`);
    console.log(`Time range: ${result.summary.time_range}`);

    return testResult.passed;
  }

  // Run all tests
  async runAllTests() {
    console.log('=========================================');
    console.log('ORTHOGONAL ENGINEERING - MCP SERVER TEST');
    console.log('Glass Box Methodology Validation');
    console.log('=========================================');

    try {
      // Start server
      await this.startServer();

      // Run tests
      const tests = [
        this.testEcho.bind(this),
        this.testTimestamp.bind(this),
        this.testHashString.bind(this),
        this.testAtomicOperation.bind(this),
        this.testAuditTrail.bind(this)
      ];

      let passedCount = 0;
      for (let i = 0; i < tests.length; i++) {
        try {
          const passed = await tests[i]();
          if (passed) passedCount++;
        } catch (error) {
          console.error(`Test ${i + 1} failed with error: ${error.message}`);
          this.testResults.push({
            test: `test_${i + 1}`,
            passed: false,
            error: error.message
          });
        }
      }

      // Print summary
      console.log('\n=========================================');
      console.log('TEST SUMMARY');
      console.log('=========================================');
      console.log(`Total tests: ${tests.length}`);
      console.log(`Passed: ${passedCount}`);
      console.log(`Failed: ${tests.length - passedCount}`);
      console.log(`Success rate: ${((passedCount / tests.length) * 100).toFixed(1)}%`);

      // Print audit trail
      console.log('\nAUDIT TRAIL (from server stderr):');
      console.log('=========================================');
      this.auditTrail.forEach((log, index) => {
        console.log(`${index + 1}. ${log}`);
      });

      // Falsifiability check
      console.log('\nFALSIFIABILITY CHECK:');
      console.log('=========================================');
      console.log('All test claims can be independently verified by:');
      console.log('1. Running the same MCP server');
      console.log('2. Executing the same test sequence');
      console.log('3. Comparing audit trails and hashes');
      console.log('4. Any discrepancy falsifies the claims');

      return passedCount === tests.length;

    } catch (error) {
      console.error('Test suite failed:', error);
      return false;
    } finally {
      // Clean up
      if (this.serverProcess) {
        this.serverProcess.kill();
      }
    }
  }
}

// Main execution
if (require.main === module) {
  const tester = new MCPClientTest();

  tester.runAllTests().then(success => {
    console.log('\n=========================================');
    console.log(`FINAL RESULT: ${success ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}`);
    console.log('=========================================');

    // Create falsifiable claim
    const claim = {
      claim_id: 'MCP-SERVER-TEST-001',
      statement: 'oe-basic.mcp server passes all 5 glass box tests',
      falsification_test: 'Run test_mcp_server.js independently',
      falsification_condition: 'If any test fails or audit trail differs',
      confidence: 0.9,
      evidence: tester.testResults
    };

    console.log('\nFALSIFIABLE CLAIM GENERATED:');
    console.log(JSON.stringify(claim, null, 2));

    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('Test suite execution failed:', error);
    process.exit(1);
  });
}

module.exports = { MCPClientTest };
