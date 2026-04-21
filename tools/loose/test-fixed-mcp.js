// test-fixed-mcp.js - Simple test for fixed MCP server
// Orthogonal Engineering - Glass Box Methodology
// Version: 1.0.0
// Date: 2026-01-25

const { spawn } = require('child_process');
const path = require('path');

class SimpleMCPTest {
  constructor() {
    this.serverProcess = null;
    this.responses = [];
  }

  // Start the fixed MCP server
  startServer() {
    return new Promise((resolve, reject) => {
      const serverPath = path.join(__dirname, 'oe-basic-fixed.mcp.js');

      console.log('Starting fixed MCP server...');
      this.serverProcess = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Capture stderr for audit logs
      this.serverProcess.stderr.on('data', (data) => {
        const log = data.toString().trim();
        console.error(`[SERVER] ${log}`);
      });

      // Capture stdout for responses
      this.serverProcess.stdout.on('data', (data) => {
        const response = data.toString().trim();
        if (response) {
          console.log(`[RESPONSE] ${response}`);
          this.responses.push(response);
        }
      });

      // Wait for server to be ready
      setTimeout(() => {
        console.log('Fixed MCP server started');
        resolve();
      }, 1000);
    });
  }

  // Send a simple JSON-RPC request
  sendRequest(method, params) {
    return new Promise((resolve, reject) => {
      const request = {
        jsonrpc: '2.0',
        method,
        params,
        id: Date.now()
      };

      console.log(`\nSending request: ${JSON.stringify(request, null, 2)}`);
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

      // Timeout after 3 seconds
      setTimeout(() => {
        this.serverProcess.stdout.removeListener('data', onData);
        reject(new Error(`Timeout waiting for response to ${method}`));
      }, 3000);
    });
  }

  // Test 1: List available tools
  async testListTools() {
    console.log('\n=== Test 1: List Tools ===');

    try {
      const response = await this.sendRequest('tools/list', {});
      console.log('Success! Server responded with tools list');

      if (response.result && response.result.tools) {
        console.log(`Available tools: ${response.result.tools.length}`);
        response.result.tools.forEach(tool => {
          console.log(`  - ${tool.name}: ${tool.description}`);
        });
        return true;
      }
      return false;
    } catch (error) {
      console.error(`Error: ${error.message}`);
      return false;
    }
  }

  // Test 2: Echo tool
  async testEchoTool() {
    console.log('\n=== Test 2: Echo Tool ===');

    try {
      const response = await this.sendRequest('tools/call', {
        name: 'echo',
        arguments: {
          message: 'Hello from fixed MCP test!'
        }
      });

      console.log('Success! Echo tool responded');

      if (response.result && response.result.content) {
        const result = JSON.parse(response.result.content[0].text);
        console.log(`Echo result: ${JSON.stringify(result, null, 2)}`);
        return result.success === true;
      }
      return false;
    } catch (error) {
      console.error(`Error: ${error.message}`);
      return false;
    }
  }

  // Test 3: Hash string tool
  async testHashTool() {
    console.log('\n=== Test 3: Hash String Tool ===');

    try {
      const response = await this.sendRequest('tools/call', {
        name: 'hash_string',
        arguments: {
          input: 'test',
          algorithm: 'simple'
        }
      });

      console.log('Success! Hash tool responded');

      if (response.result && response.result.content) {
        const result = JSON.parse(response.result.content[0].text);
        console.log(`Hash result: ${JSON.stringify(result, null, 2)}`);
        return result.success === true && result.data.hash !== undefined;
      }
      return false;
    } catch (error) {
      console.error(`Error: ${error.message}`);
      return false;
    }
  }

  // Run all tests
  async runAllTests() {
    console.log('=========================================');
    console.log('FIXED MCP SERVER TEST');
    console.log('Orthogonal Engineering - Glass Box Methodology');
    console.log('=========================================');

    try {
      // Start server
      await this.startServer();

      // Run tests
      const tests = [
        this.testListTools.bind(this),
        this.testEchoTool.bind(this),
        this.testHashTool.bind(this)
      ];

      let passedCount = 0;
      for (let i = 0; i < tests.length; i++) {
        try {
          const passed = await tests[i]();
          if (passed) passedCount++;
          console.log(`Test ${i + 1}: ${passed ? 'PASS' : 'FAIL'}`);
        } catch (error) {
          console.error(`Test ${i + 1} failed with error: ${error.message}`);
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

      // Print audit trail from stderr
      console.log('\nNote: Check the [SERVER] logs above for audit trail');
      console.log('Each operation should have [AUDIT] log entries');

      return passedCount === tests.length;

    } catch (error) {
      console.error('Test suite failed:', error);
      return false;
    } finally {
      // Clean up
      if (this.serverProcess) {
        console.log('\nStopping MCP server...');
        this.serverProcess.kill();
      }
    }
  }
}

// Main execution
if (require.main === module) {
  const tester = new SimpleMCPTest();

  tester.runAllTests().then(success => {
    console.log('\n=========================================');
    console.log(`FINAL RESULT: ${success ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}`);
    console.log('=========================================');

    // Falsifiability claim
    console.log('\nFALSIFIABLE CLAIM:');
    console.log('Fixed MCP server handles JSON-RPC correctly');
    console.log('Falsification test: Run this test script independently');
    console.log('Expected: All 3 tests pass with proper audit logging');

    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('Test suite execution failed:', error);
    process.exit(1);
  });
}

module.exports = { SimpleMCPTest };
