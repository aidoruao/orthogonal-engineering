"""Ai Core - Ai Core"""
import json
import os
import re
import subprocess
from typing import Any, Dict, Optional, Tuple

import requests


class ToolProtocol:
    """Formal tool schema and execution guarantee"""

    TOOL_SCHEMA = {
        "read_file": {
            "description": "Read contents of a file",
            "parameters": {"path": "str"},
            "returns": "file content as string",
        },
        "write_file": {
            "description": "Write content to a file",
            "parameters": {"path": "str", "content": "str"},
            "returns": "success/failure status",
        },
        "list_files": {
            "description": "List files matching glob pattern",
            "parameters": {"glob": "str"},
            "returns": "list of file paths",
        },
        "run_command": {
            "description": "Execute shell command",
            "parameters": {"cmd": "str"},
            "returns": "command output",
        },
    }

    @staticmethod
    def parse_tool_call(model_output: str) -> Optional[Tuple[str, Dict]]:
        """
        Parse structured tool call from model output.
        Format: TOOL_CALL:<tool_name>{json_parameters}
        Example: TOOL_CALL:read_file{"path": "config.rs"}
        """
        pattern = r"TOOL_CALL:(\w+)(\{.*?\})"
        match = re.search(pattern, model_output, re.DOTALL)

        if not match:
            return None

        tool_name = match.group(1)
        try:
            params = json.loads(match.group(2))
            return tool_name, params
        except json.JSONDecodeError:
            return None

    @staticmethod
    def validate_tool_call(tool_name: str, params: Dict) -> str:
        """Validate tool call against schema"""
        if tool_name not in ToolProtocol.TOOL_SCHEMA:
            return f"Unknown tool: {tool_name}"

        schema = ToolProtocol.TOOL_SCHEMA[tool_name]
        required_params = set(schema["parameters"].keys())
        provided_params = set(params.keys())

        if required_params != provided_params:
            return f"Tool {tool_name} requires parameters: {list(required_params)}"

        return ""  # Empty string = valid


class MinimalAI:
    def __init__(self, config_path="config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.endpoint = self.config["endpoint"]
        self.model = self.config["model"]
        self.project_root = self.config.get("project_root", ".")
        self.tool_protocol = ToolProtocol()

    def generate(self, prompt: str) -> str:
        """Send prompt to local AI, get response"""
        response = requests.post(
            self.endpoint, json={"model": self.model, "prompt": prompt, "stream": False}
        )
        return response.json()["response"]

    def ask_about_file(self, filepath: str, question: str) -> str:
        """Ask AI about a specific file"""
        full_path = os.path.join(self.project_root, filepath)
        with open(full_path, "r") as f:
            content = f.read()
        prompt = f"File: {filepath}\nContent:\n```\n{content}\n```\nQuestion: {question}\nAnswer:"
        return self.generate(prompt)

    def edit_file(self, filepath: str, instruction: str) -> str:
        """Edit file with AI instruction"""
        full_path = os.path.join(self.project_root, filepath)
        with open(full_path, "r") as f:
            content = f.read()
        prompt = f"Edit file '{filepath}':\nCurrent:\n```\n{content}\n```\nInstruction: {instruction}\nProvide new content only:"
        new_content = self.generate(prompt)
        with open(full_path, "w") as f:
            f.write(new_content)
        return f"Updated {filepath}"

    def execute_tool(self, tool_name: str, params: Dict) -> Dict:
        """Execute tool with guaranteed outcome"""
        # Execute based on tool name
        if tool_name == "read_file":
            path = os.path.join(self.project_root, params["path"])
            with open(path, "r") as f:
                return {"success": True, "result": f.read()}

        elif tool_name == "write_file":
            path = os.path.join(self.project_root, params["path"])
            with open(path, "w") as f:
                f.write(params["content"])
            return {"success": True, "result": f"Written {params['path']}"}

        elif tool_name == "list_files":
            import glob

            files = glob.glob(
                os.path.join(self.project_root, params["glob"]), recursive=True
            )
            return {"success": True, "result": files}

        elif tool_name == "run_command":
            result = subprocess.run(
                params["cmd"], shell=True, capture_output=True, text=True
            )
            return {
                "success": result.returncode == 0,
                "result": result.stdout,
                "error": result.stderr,
            }

        return {"success": False, "error": f"Tool {tool_name} not implemented"}

    def generate_with_tools(self, prompt: str) -> str:
        """
        Generate with tool schema injection and execution loop
        """
        # Inject tool schema into prompt
        tool_schema_desc = json.dumps(ToolProtocol.TOOL_SCHEMA, indent=2)
        enhanced_prompt = f"""TOOLS AVAILABLE:
{tool_schema_desc}

FORMAT: Use TOOL_CALL:<tool>{{parameters}} for tool calls.
Example: TOOL_CALL:read_file{{"path": "config.rs"}}

QUERY: {prompt}

RESPONSE:"""

        # Get initial model response
        response = self.generate(enhanced_prompt)

        # Check for tool calls and execute
        tool_call = self.tool_protocol.parse_tool_call(response)

        if tool_call:
            tool_name, params = tool_call

            # Validate
            error = self.tool_protocol.validate_tool_call(tool_name, params)
            if error:
                return f"TOOL_VALIDATION_ERROR: {error}"

            # Execute (GUARANTEED)
            result = self.execute_tool(tool_name, params)

            if result["success"]:
                # Return result to model for continuation
                continuation_prompt = f"Tool {tool_name} executed successfully. Result: {result['result']}\nContinue:"
                return self.generate(continuation_prompt)
            else:
                return f"TOOL_EXECUTION_ERROR: {result.get('error', 'Unknown error')}"

        # No tool call, return raw response
        return response

    def ask_with_tools(self, filepath: str, question: str) -> str:
        """Enhanced ask that can use tools"""
        prompt = f"Examine {filepath} and answer: {question}"
        return self.generate_with_tools(prompt)
