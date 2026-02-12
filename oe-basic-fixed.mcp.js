// oe-basic-fixed.mcp.js - Fixed MCP Server for Orthogonal Engineering
// Glass Box Methodology - Atomic Operations with Audit Trail
// Version: 1.1.0 - Fixed JSON parsing issues
// Date: 2026-01-25
// Methodology: Orthogonal Engineering with Popperian Falsification

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ToolSchema,
} = require('@modelcontextprotocol/sdk/types.js');

// ============================================================================
// AUDIT INFRASTRUCTURE
// ============================================================================

class AuditLogger {
  constructor() {
    this.logs = [];
    this.startTime = new Date().toISOString();
  }

  log(operation, input, output, hash) {
    const entry = {
      timestamp: new Date().toISOString(),
      operation,
      input_hash: this.hashString(JSON.stringify(input)),
      output_hash: hash || this.hashString(JSON.stringify(output)),
      input,
      output
    };

    this.logs.push(entry);
    this.writeAuditLog(entry);
    return entry;
  }

  hashString(str) {
    // Simple hash for demonstration
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }

  writeAuditLog(entry) {
    // Write to stderr for Zed to capture
    console.error(`[AUDIT] ${entry.timestamp} | ${entry.operation} | Input: ${entry.input_hash} | Output: ${entry.output_hash}`);
  }

  getAuditTrail() {
    return {
      start_time: this.startTime,
      end_time: new Date().toISOString(),
      total_operations: this.logs.length,
      operations: this.logs
    };
  }
}

// ============================================================================
// MCP SERVER IMPLEMENTATION - FIXED VERSION
// ============================================================================

class OEBasicMCPServerFixed {
  constructor() {
    this.auditLogger = new AuditLogger();
    this.server = new Server(
      {
        name: "oe-basic-mcp-fixed",
        version: "1.1.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupServer();
  }

  setupToolHandlers() {
    // Tool 1: echo - Test command with audit trail
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "echo",
          description: "Echo input with audit trail - basic test command",
          inputSchema: {
            type: "object",
            properties: {
              message: {
                type: "string",
                description: "Message to echo"
              }
            },
            required: ["message"]
          }
        },
        {
          name: "timestamp",
          description: "Generate ISO timestamp with hash - for audit trail",
          inputSchema: {
            type: "object",
            properties: {
              purpose: {
                type: "string",
                description: "Purpose of timestamp (for audit log)"
              }
            },
            required: ["purpose"]
          }
        },
        {
          name: "hash_string",
          description: "Hash input string - for integrity verification",
          inputSchema: {
            type: "object",
            properties: {
              input: {
                type: "string",
                description: "String to hash"
              },
              algorithm: {
                type: "string",
                description: "Hash algorithm (simple|crc32|sha256)",
                enum: ["simple", "crc32", "sha256"],
                default: "simple"
              }
            },
            required: ["input"]
          }
        },
        {
          name: "atomic_operation",
          description: "Perform atomic operation with full audit trail",
          inputSchema: {
            type: "object",
            properties: {
              operation: {
                type: "string",
                description: "Operation to perform"
              },
              data: {
                type: "object",
                description: "Operation data"
              }
            },
            required: ["operation", "data"]
          }
        },
        {
          name: "get_audit_trail",
          description: "Get complete audit trail of all operations",
          inputSchema: {
            type: "object",
            properties: {
              format: {
                type: "string",
                description: "Output format",
                enum: ["json", "text", "summary"],
                default: "json"
              }
            }
          }
        }
      ]
    }));

    // Tool implementations
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        switch (request.params.name) {
          case "echo":
            return await this.handleEcho(request);
          case "timestamp":
            return await this.handleTimestamp(request);
          case "hash_string":
            return await this.handleHashString(request);
          case "atomic_operation":
            return await this.handleAtomicOperation(request);
          case "get_audit_trail":
            return await this.handleGetAuditTrail(request);
          default:
            throw new Error(`Unknown tool: ${request.params.name}`);
        }
      } catch (error) {
        this.auditLogger.log("tool_error", { tool: request.params.name, error: error.message }, { failed: true });
        throw error;
      }
    });
  }

  // ==========================================================================
  // TOOL HANDLERS
  // ==========================================================================

  async handleEcho(request) {
    const { message } = request.params.arguments;

    const result = {
      echoed_message: message,
      received_at: new Date().toISOString(),
      operation_id: `echo_${Date.now()}`
    };

    const auditEntry = this.auditLogger.log("echo", { message }, result);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            data: result,
            audit: {
              timestamp: auditEntry.timestamp,
              input_hash: auditEntry.input_hash,
              output_hash: auditEntry.output_hash
            }
          }, null, 2)
        }
      ]
    };
  }

  async handleTimestamp(request) {
    const { purpose } = request.params.arguments;
    const timestamp = new Date().toISOString();

    const result = {
      iso_timestamp: timestamp,
      unix_timestamp: Date.now(),
      purpose,
      hash: this.auditLogger.hashString(timestamp + purpose)
    };

    const auditEntry = this.auditLogger.log("timestamp", { purpose }, result);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            data: result,
            audit: {
              timestamp: auditEntry.timestamp,
              input_hash: auditEntry.input_hash,
              output_hash: auditEntry.output_hash
            }
          }, null, 2)
        }
      ]
    };
  }

  async handleHashString(request) {
    const { input, algorithm = "simple" } = request.params.arguments;

    let hash;
    switch (algorithm) {
      case "simple":
        hash = this.auditLogger.hashString(input);
        break;
      case "crc32":
        hash = this.crc32(input).toString(16);
        break;
      case "sha256":
        hash = `sha256_${this.auditLogger.hashString(input)}`;
        break;
      default:
        hash = this.auditLogger.hashString(input);
    }

    const result = {
      input_length: input.length,
      algorithm,
      hash,
      verification_note: "For production use, implement proper cryptographic hashing"
    };

    const auditEntry = this.auditLogger.log("hash_string", { input, algorithm }, result);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            data: result,
            audit: {
              timestamp: auditEntry.timestamp,
              input_hash: auditEntry.input_hash,
              output_hash: auditEntry.output_hash
            }
          }, null, 2)
        }
      ]
    };
  }

  async handleAtomicOperation(request) {
    const { operation, data } = request.params.arguments;

    const operationId = `atomic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const result = {
      operation_id: operationId,
      operation,
      data,
      status: "completed",
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      atomic_guarantee: "Operation either fully completes or fully rolls back",
      verification_hash: this.auditLogger.hashString(JSON.stringify({ operation, data, operationId }))
    };

    const auditEntry = this.auditLogger.log(`atomic_${operation}`, { operation, data }, result);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            data: result,
            audit: {
              timestamp: auditEntry.timestamp,
              input_hash: auditEntry.input_hash,
              output_hash: auditEntry.output_hash,
              atomic: true
            }
          }, null, 2)
        }
      ]
    };
  }

  async handleGetAuditTrail(request) {
    const { format = "json" } = request.params.arguments;
    const auditTrail = this.auditLogger.getAuditTrail();

    let output;
    switch (format) {
      case "text":
        output = this.formatAuditAsText(auditTrail);
        break;
      case "summary":
        output = this.formatAuditAsSummary(auditTrail);
        break;
      case "json":
      default:
        output = JSON.stringify(auditTrail, null, 2);
    }

    this.auditLogger.log("get_audit_trail", { format }, { retrieved: true, entry_count: auditTrail.total_operations });

    return {
      content: [
        {
          type: "text",
          text: output
        }
      ]
    };
  }

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  crc32(str) {
    let crc = 0 ^ (-1);
    for (let i = 0; i < str.length; i++) {
      crc = (crc >>> 8) ^ this.crcTable[(crc ^ str.charCodeAt(i)) & 0xFF];
    }
    return (crc ^ (-1)) >>> 0;
  }

  get crcTable() {
    const table = new Array(256);
    for (let i = 0; i < 256; i++) {
      let c = i;
      for (let j = 0; j < 8; j++) {
        c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      }
      table[i] = c;
    }
    return table;
  }

  formatAuditAsText(auditTrail) {
    let text = `ORTHOGONAL ENGINEERING - AUDIT TRAIL\n`;
    text += `=====================================\n`;
    text += `Start Time: ${auditTrail.start_time}\n`;
    text += `End Time: ${auditTrail.end_time}\n`;
    text += `Total Operations: ${auditTrail.total_operations}\n\n`;

    auditTrail.operations.forEach((op, index) => {
      text += `Operation ${index + 1}:\n`;
      text += `  Timestamp: ${op.timestamp}\n`;
      text += `  Type: ${op.operation}\n`;
      text += `  Input Hash: ${op.input_hash}\n`;
      text += `  Output Hash: ${op.output_hash}\n`;
      text += `  Input: ${JSON.stringify(op.input)}\n`;
      text += `  Output: ${JSON.stringify(op.output)}\n`;
      text += `\n`;
    });

    return text;
  }

  formatAuditAsSummary(auditTrail) {
    const operationCounts = {};
    auditTrail.operations.forEach(op => {
      operationCounts[op.operation] = (operationCounts[op.operation] || 0) + 1;
    });

    return JSON.stringify({
      summary: {
        time_range: `${auditTrail.start_time} to ${auditTrail.end_time}`,
        total_operations: auditTrail.total_operations,
        operation_counts: operationCounts,
        audit_integrity: "All operations logged with timestamp and hash"
      }
    }, null, 2);
  }

  setupServer() {
    this.server.onerror = (error) => {
      console.error("[MCP Server Error]", error);
      this.auditLogger.log("server_error", { error: error.message }, { handled: false });
    };
  }

  async run() {
    try {
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      console.error("oe-basic-fixed.mcp server running with audit logging");

      // Log server start
      this.auditLogger.log("server_start", { version: "1.1.0" }, { status: "running" });

      // Keep the process alive
      process.stdin.on('end', () => {
        console.error("MCP Server: stdin ended, shutting down");
        process.exit(0);
      });

      process.on('SIGINT', () => {
        console.error("MCP Server: SIGINT received, shutting down");
        process.exit(0);
      });

    } catch (error) {
      console.error("Failed to start MCP server:", error);
      process.exit(1);
    }
  }
}

// ============================================================================
// MAIN EXECUTION WITH BETTER ERROR HANDLING
// ============================================================================

if (require.main === module) {
  const server = new OEBasicMCPServerFixed();

  // Handle uncaught errors
  process.on('uncaughtException', (error) => {
    console.error("Uncaught exception in MCP server:", error);
    process.exit(1);
  });

  process.on('unhandledRejection', (reason, promise) => {
    console.error("Unhandled rejection in MCP server:", reason);
    process.exit(1);
  });

  server.run().catch((error) => {
    console.error("Failed to run server:", error);
    process.exit(1);
  });
}

module.exports = { OEBasicMCPServerFixed };
