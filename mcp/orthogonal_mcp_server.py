#!/usr/bin/env python3
"""
ORTHOGONAL MCP SERVER - Subtractive Clarity Implementation
Glass-Box Boundary Compliant MCP Server for Orthogonal Engineering

Version: 1.1.0 - Protocol Correct
Schema ID: MCP-ORTHOGONAL-1.1
Date: 2026-01-25
Authority: Orthogonal Engineering Glass-Box Boundary
Protocol Fixes: Binary Mode, Byte-Safe Framing, Windows Compatible

🎯 PURPOSE:
Implement Model Context Protocol server with subtractive clarity principles:
1. Explicit communication protocols (binary mode, byte-safe framing)
2. Glass-box boundary compliance (audit trails, evidence collection)
3. Deterministic behavior (same inputs → same outputs)
4. Clear failure modes (actionable error messages)
5. Protocol correctness (Content-Length = bytes, not characters)

🔧 DESIGN PRINCIPLES:
- Subtractive Clarity: Remove ambiguity at every layer
- Glass-Box: Transparent execution with audit trails
- Orthogonal Separation: Clean separation of concerns
- Deterministic: Reproducible, predictable behavior
- Protocol Correct: Binary mode, byte-safe framing, Windows compatible
"""

import hashlib
import json
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# ============================================================================
# SUBTRACTIVE CLARITY: EXPLICIT TYPES AND CONTRACTS
# ============================================================================


class MessageType(Enum):
    """Explicit message types - no ambiguous strings."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class ToolCategory(Enum):
    """Explicit tool categories - no ambiguous grouping."""

    AUDIT = "audit"
    VALIDATION = "validation"
    EVIDENCE = "evidence"
    BOUNDARY = "boundary"
    UTILITY = "utility"


@dataclass
class AuditEntry:
    """Explicit audit entry structure - no ambiguous fields."""

    timestamp: str
    operation: str
    input_hash: str
    output_hash: str
    evidence_path: Optional[str] = None
    boundary_violation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        # TODO: Expand to_dict() - stub detected by Yeshua Agent
        return asdict(self)


@dataclass
class MCPRequest:
    """Explicit request structure - no ambiguous JSON parsing."""

    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_json(cls, json_str: str) -> "MCPRequest":
        """Explicit parsing with clear error handling."""
        try:
            data = json.loads(json_str)
            return cls(
                jsonrpc=data.get("jsonrpc", "2.0"),
                id=data.get("id"),
                method=data.get("method"),
                params=data.get("params"),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValueError(f"Invalid request structure: {e}")


@dataclass
class MCPResponse:
    """Explicit response structure - no ambiguous fields."""

    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """Explicit serialization - no ambiguous formatting."""
        data = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            data["id"] = self.id
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error
        return json.dumps(data, separators=(",", ":"))


# ============================================================================
# GLASS-BOX BOUNDARY: AUDIT AND EVIDENCE INFRASTRUCTURE
# ============================================================================


class GlassBoxAuditor:
    """Glass-box audit trail with evidence collection."""

    def __init__(self):
        self.entries: List[AuditEntry] = []
        self.start_time = datetime.now().isoformat()

    def hash_data(self, data: Any) -> str:
        """Deterministic hashing - no ambiguous hash algorithms."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()[:16]

    def log_operation(
        self,
        operation: str,
        input_data: Any,
        output_data: Any,
        evidence_path: Optional[str] = None,
        boundary_violation: bool = False,
    ) -> AuditEntry:
        """Explicit logging - no ambiguous audit entries."""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            input_hash=self.hash_data(input_data),
            output_hash=self.hash_data(output_data),
            evidence_path=evidence_path,
            boundary_violation=boundary_violation,
        )

        self.entries.append(entry)

        # Glass-box transparency: Write to stderr for immediate visibility
        sys.stderr.write(
            f"[GLASS-BOX AUDIT] {entry.timestamp} | "
            f"{entry.operation} | "
            f"Input: {entry.input_hash} | "
            f"Output: {entry.output_hash} | "
            f"Violation: {entry.boundary_violation}\n"
        )
        sys.stderr.flush()

        return entry

    def get_audit_trail(self, format: str = "json") -> Dict[str, Any]:
        """Explicit audit retrieval - no ambiguous formats."""
        trail = {
            "start_time": self.start_time,
            "end_time": datetime.now().isoformat(),
            "total_operations": len(self.entries),
            "operations": [entry.to_dict() for entry in self.entries],
        }

        if format == "summary":
            return {
                "summary": {
                    "time_range": f"{self.start_time} to {trail['end_time']}",
                    "total_operations": trail["total_operations"],
                    "boundary_violations": sum(
                        1 for e in self.entries if e.boundary_violation
                    ),
                    "audit_integrity": "SHA256 hashed with timestamps",
                }
            }

        return trail


# ============================================================================
# ORTHOGONAL TOOLS: CLEAN SEPARATION OF CONCERNS
# ============================================================================


class OrthogonalTools:
    """Orthogonal tool collection - clean separation by category."""

    def __init__(self, auditor: GlassBoxAuditor):
        self.auditor = auditor
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        """Explicit tool definitions - no ambiguous capabilities."""
        return {
            # AUDIT TOOLS
            "get_audit_trail": {
                "category": ToolCategory.AUDIT,
                "description": "Get glass-box audit trail with evidence hashes",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["json", "summary"],
                            "default": "json",
                            "description": "Output format",
                        }
                    },
                },
                "handler": self.handle_get_audit_trail,
            },
            # VALIDATION TOOLS
            "validate_json": {
                "category": ToolCategory.VALIDATION,
                "description": "Validate JSON structure with schema checking",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "json_string": {
                            "type": "string",
                            "description": "JSON string to validate",
                        },
                        "schema": {
                            "type": "object",
                            "description": "JSON schema to validate against",
                        },
                    },
                    "required": ["json_string"],
                },
                "handler": self.handle_validate_json,
            },
            # EVIDENCE TOOLS
            "hash_evidence": {
                "category": ToolCategory.EVIDENCE,
                "description": "Hash evidence with SHA256 for integrity verification",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Data to hash as evidence",
                        },
                        "algorithm": {
                            "type": "string",
                            "enum": ["sha256", "sha512"],
                            "default": "sha256",
                            "description": "Hash algorithm",
                        },
                    },
                    "required": ["data"],
                },
                "handler": self.handle_hash_evidence,
            },
            # BOUNDARY TOOLS
            "check_boundary": {
                "category": ToolCategory.BOUNDARY,
                "description": "Check glass-box boundary compliance",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation to check",
                        },
                        "input_data": {
                            "type": "object",
                            "description": "Input data for boundary check",
                        },
                    },
                    "required": ["operation", "input_data"],
                },
                "handler": self.handle_check_boundary,
            },
            # UTILITY TOOLS
            "echo": {
                "category": ToolCategory.UTILITY,
                "description": "Echo input with audit trail - basic connectivity test",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo"}
                    },
                    "required": ["message"],
                },
                "handler": self.handle_echo,
            },
            "timestamp": {
                "category": ToolCategory.UTILITY,
                "description": "Generate ISO timestamp with hash - for audit synchronization",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "purpose": {
                            "type": "string",
                            "description": "Purpose of timestamp",
                        }
                    },
                    "required": ["purpose"],
                },
                "handler": self.handle_timestamp,
            },
        }

    # ==========================================================================
    # TOOL HANDLERS - EXPLICIT IMPLEMENTATIONS
    # ==========================================================================

    def handle_get_audit_trail(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit audit trail retrieval."""
        format = arguments.get("format", "json")
        trail = self.auditor.get_audit_trail(format)

        self.auditor.log_operation(
            operation="get_audit_trail", input_data=arguments, output_data=trail
        )

        return {
            "success": True,
            "data": trail,
            "metadata": {
                "operation": "get_audit_trail",
                "format": format,
                "retrieved_at": datetime.now().isoformat(),
            },
        }

    def handle_validate_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit JSON validation."""
        json_string = arguments["json_string"]
        schema = arguments.get("schema")

        try:
            data = json.loads(json_string)
            is_valid = True
            validation_errors = []

            if schema:
                # Basic schema validation (simplified for example)
                if isinstance(schema, dict) and "type" in schema:
                    expected_type = schema["type"]
                    actual_type = type(data).__name__
                    if expected_type == "array" and not isinstance(data, list):
                        is_valid = False
                        validation_errors.append(f"Expected array, got {actual_type}")
                    elif expected_type == "object" and not isinstance(data, dict):
                        is_valid = False
                        validation_errors.append(f"Expected object, got {actual_type}")

            result = {
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "parsed_data": data if is_valid else None,
            }

            self.auditor.log_operation(
                operation="validate_json",
                input_data={
                    "json_string": json_string[:100] + "..."
                    if len(json_string) > 100
                    else json_string
                },
                output_data=result,
            )

            return {
                "success": True,
                "data": result,
                "metadata": {
                    "operation": "validate_json",
                    "valid": is_valid,
                    "error_count": len(validation_errors),
                },
            }

        except json.JSONDecodeError as e:
            error_result = {
                "is_valid": False,
                "validation_errors": [f"JSON decode error: {str(e)}"],
                "parsed_data": None,
            }

            self.auditor.log_operation(
                operation="validate_json",
                input_data={
                    "json_string": json_string[:100] + "..."
                    if len(json_string) > 100
                    else json_string
                },
                output_data=error_result,
                boundary_violation=True,
            )

            return {
                "success": False,
                "error": f"Invalid JSON: {str(e)}",
                "data": error_result,
            }

    def handle_hash_evidence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit evidence hashing."""
        data = arguments["data"]
        algorithm = arguments.get("algorithm", "sha256")

        if algorithm == "sha256":
            hash_obj = hashlib.sha256(data.encode("utf-8"))
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(data.encode("utf-8"))
        else:
            hash_obj = hashlib.sha256(data.encode("utf-8"))

        hash_value = hash_obj.hexdigest()

        result = {
            "algorithm": algorithm,
            "hash": hash_value,
            "input_length": len(data),
            "verification_note": "Use same algorithm and input to verify",
        }

        self.auditor.log_operation(
            operation="hash_evidence",
            input_data={"data_length": len(data), "algorithm": algorithm},
            output_data=result,
        )

        return {
            "success": True,
            "data": result,
            "metadata": {
                "operation": "hash_evidence",
                "algorithm": algorithm,
                "hashed_at": datetime.now().isoformat(),
            },
        }

    def handle_check_boundary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit boundary checking."""
        operation = arguments["operation"]
        input_data = arguments["input_data"]

        # Basic boundary checks
        boundary_violation = False
        violations = []

        if not operation:
            boundary_violation = True
            violations.append("Operation name is required")

        if not isinstance(input_data, dict):
            boundary_violation = True
            violations.append("Input data must be an object")

        result = {
            "operation": operation,
            "boundary_violation": boundary_violation,
            "violations": violations,
            "recommendation": "Add @glass_box_boundary decorator if not present",
        }

        self.auditor.log_operation(
            operation="check_boundary",
            input_data={
                "operation": operation,
                "input_data_type": type(input_data).__name__,
            },
            output_data=result,
            boundary_violation=boundary_violation,
        )

        return {
            "success": not boundary_violation,
            "data": result,
            "metadata": {
                "operation": "check_boundary",
                "has_violations": boundary_violation,
                "violation_count": len(violations),
            },
        }

    def handle_echo(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit echo with audit."""
        message = arguments["message"]

        result = {
            "echoed_message": message,
            "received_at": datetime.now().isoformat(),
            "operation_id": f"echo_{int(time.time() * 1000)}",
        }

        self.auditor.log_operation(
            operation="echo", input_data={"message": message}, output_data=result
        )

        return {
            "success": True,
            "data": result,
            "metadata": {"operation": "echo", "timestamp": result["received_at"]},
        }

    def handle_timestamp(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit timestamp generation."""
        purpose = arguments["purpose"]
        timestamp = datetime.now().isoformat()

        result = {
            "iso_timestamp": timestamp,
            "unix_timestamp": int(time.time()),
            "purpose": purpose,
            "hash": self.auditor.hash_data(timestamp + purpose),
        }

        self.auditor.log_operation(
            operation="timestamp", input_data={"purpose": purpose}, output_data=result
        )

        return {
            "success": True,
            "data": result,
            "metadata": {
                "operation": "timestamp",
                "purpose": purpose,
                "generated_at": timestamp,
            },
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Explicit tool listing."""
        tools_list = []
        for name, tool_info in self.tools.items():
            tools_list.append(
                {
                    "name": name,
                    "description": tool_info["description"],
                    "inputSchema": tool_info["input_schema"],
                    "category": tool_info["category"].value,
                }
            )

        self.auditor.log_operation(
            operation="list_tools",
            input_data={},
            output_data={"tool_count": len(tools_list)},
        )

        return tools_list


# ============================================================================
# MCP SERVER: SUBTRACTIVE CLARITY COMMUNICATION PROTOCOL
# ============================================================================


class OrthogonalMCPServer:
    """
    Orthogonal MCP Server with subtractive clarity communication.

    Key Features:
    1. Explicit message framing (no ambiguous JSON boundaries)
    2. Clear error handling (no silent failures)
    3. Glass-box audit trails (transparent execution)
    4. Deterministic behavior (reproducible results)
    """

    def __init__(self):
        self.auditor = GlassBoxAuditor()
        self.tools = OrthogonalTools(self.auditor)

        # Log server initialization
        self.auditor.log_operation(
            operation="server_init",
            input_data={"version": "1.0.0", "schema_id": "MCP-ORTHOGONAL-1.0"},
            output_data={"status": "initialized", "tool_count": len(self.tools.tools)},
        )

    def read_message(self) -> Optional[str]:
        """
        Read MCP message with explicit BYTE framing.

        Uses Content-Length header framing as per MCP specification.
        Binary mode, byte-safe, no text mode ambiguity.
        """
        try:
            # Read headers as bytes
            headers = {}
            while True:
                # Read bytes until newline
                line_bytes = b""
                while True:
                    char = sys.stdin.buffer.read(1)
                    if not char:
                        raise RuntimeError("MCP client closed stdin")
                    if char == b"\n":
                        break
                    line_bytes += char

                # Remove trailing \r if present
                if line_bytes.endswith(b"\r"):
                    line_bytes = line_bytes[:-1]

                # Empty line means end of headers
                if line_bytes == b"":
                    break

                # Parse header
                if b":" not in line_bytes:
                    raise ValueError(f"Invalid header line: {line_bytes}")

                key, value = line_bytes.split(b":", 1)
                headers[key.decode().strip().lower()] = value.decode().strip()

            # Check for Content-Length
            if "content-length" not in headers:
                return None

            content_length = int(headers["content-length"])

            # Read exactly content_length bytes
            message_bytes = b""
            while len(message_bytes) < content_length:
                chunk = sys.stdin.buffer.read(content_length - len(message_bytes))
                if not chunk:
                    raise RuntimeError(
                        f"Expected {content_length} bytes, got {len(message_bytes)}"
                    )
                message_bytes += chunk

            return message_bytes.decode("utf-8")

        except Exception as e:
            self.auditor.log_operation(
                operation="read_message_error",
                input_data={"error": str(e)},
                output_data={"handled": False},
                boundary_violation=True,
            )
            return None

    def write_message(self, message: str):
        """
        Write MCP response with explicit BYTE framing.

        Clear protocol: Content-Length header + JSON body.
        Binary mode, byte-safe, no text mode ambiguity.
        """
        try:
            # Convert message to bytes
            message_bytes = message.encode("utf-8")

            # Write headers as bytes
            header = f"Content-Length: {len(message_bytes)}\r\n\r\n".encode("ascii")
            sys.stdout.buffer.write(header)

            # Write body as bytes
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()

            self.auditor.log_operation(
                operation="write_message",
                input_data={"message_length": len(message_bytes)},
                output_data={"written": True},
            )

        except Exception as e:
            self.auditor.log_operation(
                operation="write_message_error",
                input_data={"error": str(e)},
                output_data={"handled": False},
                boundary_violation=True,
            )

    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle MCP request with explicit routing.

        Clear separation: tools/list vs tools/call
        No ambiguous method handling.
        """
        try:
            if request.method == "tools/list":
                # List available tools
                tools = self.tools.list_tools()

                response = MCPResponse(id=request.id, result={"tools": tools})

                self.auditor.log_operation(
                    operation="list_tools_request",
                    input_data={"request_id": request.id},
                    output_data={"tool_count": len(tools)},
                )

                return response

            elif request.method == "tools/call":
                # Call specific tool
                if not request.params or "name" not in request.params:
                    raise ValueError("Tool name is required")

                tool_name = request.params["name"]
                arguments = request.params.get("arguments", {})

                if tool_name not in self.tools.tools:
                    raise ValueError(f"Unknown tool: {tool_name}")

                # Call tool handler
                tool_info = self.tools.tools[tool_name]
                result = tool_info["handler"](arguments)

                response = MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    },
                )

                self.auditor.log_operation(
                    operation=f"call_tool_{tool_name}",
                    input_data={"tool": tool_name, "arguments": arguments},
                    output_data={"success": result.get("success", False)},
                )

                return response

            else:
                raise ValueError(f"Unknown method: {request.method}")

        except Exception as e:
            error_response = MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "data": {
                        "operation": request.method if request.method else "unknown",
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat(),
                    },
                },
            )

            self.auditor.log_operation(
                operation="request_error",
                input_data={
                    "method": request.method,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                output_data={"handled": True},
                boundary_violation=True,
            )

            return error_response

    def run(self):
        """
        Main server loop with explicit lifecycle.

        Clear startup/shutdown, no ambiguous state.
        """
        try:
            # Log server start
            self.auditor.log_operation(
                operation="server_start",
                input_data={"pid": os.getpid(), "python_version": sys.version},
                output_data={"status": "running"},
            )

            # Write startup message to stderr (visible in Zed)
            sys.stderr.write(
                f"[ORTHOGONAL MCP SERVER] Started at {datetime.now().isoformat()}\n"
                f"[ORTHOGONAL MCP SERVER] Version: 1.0.0 | Schema: MCP-ORTHOGONAL-1.0\n"
                f"[ORTHOGONAL MCP SERVER] Tools available: {len(self.tools.tools)}\n"
                f"[ORTHOGONAL MCP SERVER] Glass-Box Audit: ACTIVE\n"
            )
            sys.stderr.flush()

            # Main loop
            while True:
                # Read message
                message = self.read_message()
                if message is None:
                    # EOF or error
                    break

                # Parse request
                request = MCPRequest.from_json(message)

                # Handle request
                response = self.handle_request(request)

                # Send response
                self.write_message(response.to_json())

        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            self.auditor.log_operation(
                operation="server_shutdown",
                input_data={"signal": "SIGINT"},
                output_data={"status": "shutdown_complete"},
            )

            sys.stderr.write("[ORTHOGONAL MCP SERVER] Graceful shutdown complete\n")
            sys.stderr.flush()

        except Exception as e:
            # Critical error
            self.auditor.log_operation(
                operation="server_crash",
                input_data={"error": str(e), "traceback": traceback.format_exc()},
                output_data={"handled": False},
                boundary_violation=True,
            )

            sys.stderr.write(f"[ORTHOGONAL MCP SERVER] Critical error: {str(e)}\n")
            sys.stderr.flush()
            raise


# ============================================================================
# MAIN ENTRY POINT: EXPLICIT EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Explicit entry point with clear error handling.

    No ambiguous startup, clear exit codes.
    """
    import os

    try:
        # Create and run server
        server = OrthogonalMCPServer()
        server.run()

        # Exit cleanly
        sys.exit(0)

    except SystemExit:
        # Already exiting
        raise

    except Exception as e:
        # Critical startup failure
        sys.stderr.write(f"[ORTHOGONAL MCP SERVER] Failed to start: {str(e)}\n")
        sys.stderr.write(
            f"[ORTHOGONAL MCP SERVER] Traceback: {traceback.format_exc()}\n"
        )
        sys.stderr.flush()
        sys.exit(1)
