#!/usr/bin/env python3
"""
CORPORATE-STYLE ATOMIC INVARIANT EXTRACTION SYSTEM
===================================================

This system extracts hard invariants from the repository and encodes them
into maximally atomic, strict JSON for corporate-style enforcement.

Key Principles:
1. Atomicity - One invariant per entry, no mixed rules
2. Determinism - No guessing, no hallucinations, no omissions
3. Auditability - Every entry contains everything needed for verification
4. Enforcement - Explicit enforcement points and mandatory flags
5. Safety - Protected files and execution rules are strictly defined

Usage:
    python extract_invariants.py [--output invariants.json] [--verbose]
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class AtomicInvariantExtractor:
    """
    Corporate-style invariant extraction engine.

    Extracts hard invariants from repository with maximal atomicity and strictness.
    Never guesses, never hallucinates, never omits critical information.
    """

    def __init__(self, root_dir: str = ".", verbose: bool = False):
        self.root_dir = Path(root_dir).resolve()
        self.verbose = verbose
        self.invariants: List[Dict[str, Any]] = []
        self.file_cache: Dict[str, str] = {}
        self.rule_counter = 1

        # Categories for classification
        self.categories = {
            "code": [".py", ".rs", ".js", ".ts", ".java", ".cpp", ".c", ".go"],
            "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"],
            "protected": [".env", "secrets", "keys", "credentials", "password"],
            "tool": ["tool", "warden", "controller", "enforcer"],
            "documentation": [".md", ".txt", ".rst", ".html", ".pdf"],
            "binary": [".exe", ".dll", ".so", ".dylib", ".bin", ".dat"],
        }

    def log(self, message: str, level: str = "INFO"):
        """Corporate-style logging with levels."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def read_file_safe(self, filepath: Path) -> Optional[str]:
        """Safely read file with error handling and caching."""
        try:
            if str(filepath) in self.file_cache:
                return self.file_cache[str(filepath)]

            if not filepath.exists():
                self.log(f"File not found: {filepath}", "WARNING")
                return None

            # Skip binary files
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.file_cache[str(filepath)] = content
                return content
            except UnicodeDecodeError:
                self.log(f"Skipping binary file: {filepath}", "INFO")
                return None

        except Exception as e:
            self.log(f"Error reading {filepath}: {e}", "ERROR")
            return None

    def categorize_file(self, filepath: Path) -> str:
        """Categorize file based on name, extension, and content."""
        filename = filepath.name.lower()
        ext = filepath.suffix.lower()

        # Check for protected files
        for pattern in self.categories["protected"]:
            if pattern in filename:
                return "protected"

        # Check by extension
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category

        # Check by name patterns for tools
        for pattern in self.categories["tool"]:
            if pattern in filename:
                return "tool"

        # Default category
        return "unknown"

    def scan_critical_files(self) -> List[Dict[str, str]]:
        """
        Instruction 1: Scan for Critical Files / Paths

        Scan the repository for all files and directories that define
        functionality or safety rules.
        """
        self.log("Scanning for critical files and paths...")

        critical_files = []

        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip hidden directories and virtual environments
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", "venv", ".venv"]
            ]

            # Process directories
            for dir_name in dirs:
                dir_path = root_path / dir_name
                category = self.categorize_file(dir_path)
                critical_files.append(
                    {
                        "path": str(dir_path.relative_to(self.root_dir)),
                        "type": "directory",
                        "category": category,
                        "absolute_path": str(dir_path),
                    }
                )

            # Process files
            for file_name in files:
                file_path = root_path / file_name

                # Skip hidden files
                if file_name.startswith("."):
                    continue

                category = self.categorize_file(file_path)
                critical_files.append(
                    {
                        "path": str(file_path.relative_to(self.root_dir)),
                        "type": "file",
                        "category": category,
                        "absolute_path": str(file_path),
                    }
                )

        # Sort for consistency
        critical_files.sort(key=lambda x: x["path"])

        self.log(f"Found {len(critical_files)} critical files/directories")
        return critical_files

    def extract_tool_schema(
        self, critical_files: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Instruction 2: Extract Tool Schema / Function Signatures

        Extract every tool or function callable by the system, including
        parameters and return types.
        """
        self.log("Extracting tool schemas and function signatures...")

        tool_schemas = []

        for file_info in critical_files:
            if file_info["type"] != "file":
                continue

            if file_info["category"] not in ["code", "tool"]:
                continue

            filepath = Path(file_info["absolute_path"])
            content = self.read_file_safe(filepath)

            if not content:
                continue

            # Extract from Python files
            if filepath.suffix == ".py":
                tools = self._extract_python_tools(filepath, content)
                tool_schemas.extend(tools)

            # Extract from JSON config files
            elif filepath.suffix == ".json":
                tools = self._extract_json_tools(filepath, content)
                tool_schemas.extend(tools)

        self.log(f"Extracted {len(tool_schemas)} tool schemas")
        return tool_schemas

    def _extract_python_tools(
        self, filepath: Path, content: str
    ) -> List[Dict[str, Any]]:
        """Extract tool schemas from Python files."""
        tools = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Look for function definitions
                if isinstance(node, ast.FunctionDef):
                    tool_name = node.name

                    # Check if it looks like a tool (has docstring mentioning tool, or specific patterns)
                    if self._is_likely_tool(node, content):
                        params = {}

                        # Extract parameters
                        for arg in node.args.args:
                            param_name = arg.arg
                            # Try to infer type from annotation
                            if arg.annotation:
                                try:
                                    param_type = ast.unparse(arg.annotation)
                                except:
                                    param_type = "Any"
                            else:
                                param_type = "Any"
                            params[param_name] = param_type

                        # Extract return type
                        return_type = "Any"
                        if node.returns:
                            try:
                                return_type = ast.unparse(node.returns)
                            except:
                                return_type = "Any"

                        tools.append(
                            {
                                "tool_name": tool_name,
                                "parameters": params,
                                "return_type": return_type,
                                "source_file": str(filepath.relative_to(self.root_dir)),
                                "line_number": node.lineno,
                            }
                        )

                # Look for class definitions with execute_tool methods
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if (
                            isinstance(item, ast.FunctionDef)
                            and item.name == "execute_tool"
                        ):
                            # This is a tool execution class
                            tools.append(
                                {
                                    "tool_name": node.name,
                                    "parameters": {
                                        "tool_name": "str",
                                        "params": "Dict",
                                    },
                                    "return_type": "Dict",
                                    "source_file": str(
                                        filepath.relative_to(self.root_dir)
                                    ),
                                    "line_number": node.lineno,
                                    "is_tool_class": True,
                                }
                            )

        except SyntaxError as e:
            self.log(f"Syntax error in {filepath}: {e}", "WARNING")

        return tools

    def _is_likely_tool(self, node: ast.FunctionDef, content: str) -> bool:
        """Determine if a function is likely a tool based on various heuristics."""
        func_name = node.name.lower()

        # Check name patterns
        tool_patterns = ["tool", "execute", "run", "call", "invoke", "process"]
        if any(pattern in func_name for pattern in tool_patterns):
            return True

        # Check docstring for tool mentions
        if ast.get_docstring(node):
            docstring = ast.get_docstring(node).lower()
            if any(pattern in docstring for pattern in tool_patterns):
                return True

        # Check for decorators
        for decorator in node.decorator_list:
            try:
                decorator_name = ast.unparse(decorator).lower()
                if any(pattern in decorator_name for pattern in tool_patterns):
                    return True
            except:
                pass

        return False

    def _extract_json_tools(self, filepath: Path, content: str) -> List[Dict[str, Any]]:
        """Extract tool schemas from JSON files."""
        tools = []

        try:
            data = json.loads(content)

            # Look for TOOL_SCHEMA patterns
            if isinstance(data, dict):
                for key, value in data.items():
                    if "tool" in key.lower() or "schema" in key.lower():
                        if isinstance(value, dict):
                            for tool_name, tool_def in value.items():
                                if isinstance(tool_def, dict):
                                    params = tool_def.get("parameters", {})
                                    return_type = tool_def.get("returns", "Any")

                                    tools.append(
                                        {
                                            "tool_name": tool_name,
                                            "parameters": params,
                                            "return_type": return_type,
                                            "source_file": str(
                                                filepath.relative_to(self.root_dir)
                                            ),
                                            "from_json_key": key,
                                        }
                                    )

        except json.JSONDecodeError as e:
            self.log(f"JSON error in {filepath}: {e}", "WARNING")

        return tools

    def detect_protected_files(
        self, critical_files: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Instruction 3: Detect Protected / Immutable Files

        Identify files or directories that must never be overwritten or deleted.
        """
        self.log("Detecting protected and immutable files...")

        protected_files = []

        for file_info in critical_files:
            if file_info["category"] == "protected":
                protected_files.append(
                    {
                        "path": file_info["path"],
                        "protection_level": "strict",
                        "reason": "Contains sensitive information or critical system files",
                        "type": file_info["type"],
                        "category": file_info["category"],
                    }
                )

            # Additional protection rules based on content analysis
            elif file_info["type"] == "file":
                filepath = Path(file_info["absolute_path"])
                content = self.read_file_safe(filepath)

                if content:
                    # Check for protection indicators in content
                    protection_level, reason = self._analyze_protection_level(
                        filepath, content
                    )
                    if protection_level:
                        protected_files.append(
                            {
                                "path": file_info["path"],
                                "protection_level": protection_level,
                                "reason": reason,
                                "type": file_info["type"],
                                "category": file_info["category"],
                            }
                        )

        self.log(f"Detected {len(protected_files)} protected files/directories")
        return protected_files

    def _analyze_protection_level(
        self, filepath: Path, content: str
    ) -> Tuple[Optional[str], str]:
        """Analyze file content to determine protection level."""
        filename = filepath.name.lower()
        content_lower = content.lower()

        # Strict protection patterns
        strict_patterns = [
            r"secret",
            r"password",
            r"api[_-]?key",
            r"token",
            r"credential",
            r"private[_-]?key",
            r"certificate",
            r".env",
            r"config.*secret",
        ]

        for pattern in strict_patterns:
            if re.search(pattern, filename) or re.search(pattern, content_lower):
                return "strict", f"Contains {pattern.replace('_', ' ')} pattern"

        # High protection patterns
        high_patterns = [
            r"controller",
            r"warden",
            r"enforcer",
            r"auth",
            r"permission",
            r"admin",
            r"root",
            r"system",
        ]

        for pattern in high_patterns:
            if re.search(pattern, filename) or re.search(pattern, content_lower):
                return "high", f"System control file with {pattern} pattern"

        # Medium protection patterns
        medium_patterns = [r"config", r"setting", r"database", r"schema", r"model"]

        for pattern in medium_patterns:
            if re.search(pattern, filename) or re.search(pattern, content_lower):
                return "medium", f"Configuration file with {pattern} pattern"

        return None, ""

    def extract_execution_rules(
        self, critical_files: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Instruction 4: Extract Execution Rules / Safety Invariants

        Identify all hard-coded rules or constraints that the AI must follow.
        """
        self.log("Extracting execution rules and safety invariants...")

        execution_rules = []

        for file_info in critical_files:
            if file_info["type"] != "file":
                continue

            filepath = Path(file_info["absolute_path"])
            content = self.read_file_safe(filepath)

            if not content:
                continue

            # Extract rules from Python files
            if filepath.suffix == ".py":
                rules = self._extract_python_rules(filepath, content)
                execution_rules.extend(rules)

            # Extract rules from config files
            elif filepath.suffix in [".json", ".yaml", ".yml", ".toml"]:
                rules = self._extract_config_rules(filepath, content)
                execution_rules.extend(rules)

        self.log(f"Extracted {len(execution_rules)} execution rules")
        return execution_rules

    def _extract_python_rules(
        self, filepath: Path, content: str
    ) -> List[Dict[str, Any]]:
        """Extract execution rules from Python files."""
        rules = []

        # Look for rule patterns in comments and strings
        rule_patterns = [
            (r"#\s*RULE:\s*(.+?)(?:\n|$)", "comment_rule"),
            (r'"""\s*RULE:\s*(.+?)\s*"""', "docstring_rule"),
            (r"'''\s*RULE:\s*(.+?)\s*'''", "docstring_rule"),
            (r"#\s*Never\s+(.+?)(?:\n|$)", "safety_rule"),
            (r"#\s*Always\s+(.+?)(?:\n|$)", "safety_rule"),
            (r"#\s*Must\s+(.+?)(?:\n|$)", "mandatory_rule"),
            (r"assert\s+(.+?)[,\n]", "assertion_rule"),
        ]

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for pattern, rule_type in rule_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        description = match[0]
                    else:
                        description = match

                    rule_id = f"R{self.rule_counter:03d}"
                    self.rule_counter += 1

                    rules.append(
                        {
                            "rule_id": rule_id,
                            "description": description.strip(),
                            "enforcement_point": str(
                                filepath.relative_to(self.root_dir)
                            ),
                            "line_number": line_num,
                            "rule_type": rule_type,
                            "mandatory": rule_type in ["mandatory_rule", "safety_rule"],
                        }
                    )

        return rules

    def _extract_config_rules(
        self, filepath: Path, content: str
    ) -> List[Dict[str, Any]]:
        """Extract execution rules from config files."""
        rules = []

        try:
            if filepath.suffix == ".json":
                data = json.loads(content)
                rules.extend(self._extract_rules_from_dict(data, filepath))

            # Add support for other config formats here

        except Exception as e:
            self.log(f"Error parsing config file {filepath}: {e}", "WARNING")

        return rules

    def _extract_rules_from_dict(
        self, data: Dict, filepath: Path, prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """Recursively extract rules from dictionary structures."""
        rules = []

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Look for rule-like keys
            if any(
                rule_word in key.lower()
                for rule_word in ["rule", "constraint", "restriction", "policy"]
            ):
                rule_id = f"R{self.rule_counter:03d}"
                self.rule_counter += 1

                rules.append(
                    {
                        "rule_id": rule_id,
                        "description": f"Config rule: {full_key} = {value}",
                        "enforcement_point": str(filepath.relative_to(self.root_dir)),
                        "config_key": full_key,
                        "mandatory": True,
                    }
                )

            # Recursively process nested dictionaries
            if isinstance(value, dict):
                rules.extend(self._extract_rules_from_dict(value, filepath, full_key))

        return rules

    def create_atomic_json_dataset(
        self,
        critical_files: List[Dict[str, str]],
        tool_schemas: List[Dict[str, Any]],
        protected_files: List[Dict[str, Any]],
        execution_rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Instruction 5: Create Atomic JSON Dataset of Invariants

        For each rule, file, or tool discovered, create an atomic JSON entry
        combining file path, tool/schema, and enforcement invariant.
        """
        self.log("Creating atomic JSON dataset of invariants...")

        atomic_dataset = []

        # Create entries for critical files
        for file_info in critical_files:
            atomic_dataset.append(
                {
                    "file_path": file_info["path"],
                    "tool_or_rule": "FILE_SYSTEM_ENTRY",
                    "parameters": None,
                    "return_type": None,
                    "enforcement_point": "file_system",
                    "mandatory": True,
                    "type": file_info["type"],
                    "category": file_info["category"],
                    "atomic_id": f"FILE_{hashlib.md5(file_info['path'].encode()).hexdigest()[:8]}",
                }
            )

        # Create entries for tool schemas
        for tool in tool_schemas:
            atomic_dataset.append(
                {
                    "file_path": tool.get("source_file", "unknown"),
                    "tool_or_rule": tool["tool_name"],
                    "parameters": tool["parameters"],
                    "return_type": tool["return_type"],
                    "enforcement_point": tool.get("source_file", "unknown"),
                    "mandatory": True,
                    "line_number": tool.get("line_number"),
                    "atomic_id": f"TOOL_{hashlib.md5(tool['tool_name'].encode()).hexdigest()[:8]}",
                }
            )

        # Create entries for protected files
        for protected in protected_files:
            atomic_dataset.append(
                {
                    "file_path": protected["path"],
                    "tool_or_rule": "PROTECTED",
                    "parameters": None,
                    "return_type": None,
                    "enforcement_point": protected.get("enforcement_point", "system"),
                    "mandatory": True,
                    "protection_level": protected["protection_level"],
                    "reason": protected["reason"],
                    "atomic_id": f"PROTECTED_{hashlib.md5(protected['path'].encode()).hexdigest()[:8]}",
                }
            )

        # Create entries for execution rules
        for rule in execution_rules:
            atomic_dataset.append(
                {
                    "file_path": rule["enforcement_point"],
                    "tool_or_rule": rule["rule_id"],
                    "parameters": {"description": rule["description"]},
                    "return_type": "enforcement_result",
                    "enforcement_point": rule["enforcement_point"],
                    "mandatory": rule.get("mandatory", True),
                    "line_number": rule.get("line_number"),
                    "rule_type": rule.get("rule_type", "unknown"),
                    "atomic_id": f"RULE_{rule['rule_id']}",
                }
            )

        self.log(f"Created {len(atomic_dataset)} atomic invariant entries")
        return atomic_dataset

    def generate_invariants_report(
        self, output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete invariants report and save to JSON file.
        """
        self.log("Generating complete invariants report...")

        # Execute all extraction steps
        critical_files = self.scan_critical_files()
        tool_schemas = self.extract_tool_schema(critical_files)
        protected_files = self.detect_protected_files(critical_files)
        execution_rules = self.extract_execution_rules(critical_files)
        atomic_dataset = self.create_atomic_json_dataset(
            critical_files, tool_schemas, protected_files, execution_rules
        )

        # Create comprehensive report
        report = {
            "metadata": {
                "generated_at": self._get_timestamp(),
                "root_directory": str(self.root_dir),
                "total_invariants": len(atomic_dataset),
                "extractor_version": "1.0.0",
                "hash": self._calculate_report_hash(atomic_dataset),
            },
            "critical_files": critical_files,
            "tool_schemas": tool_schemas,
            "protected_files": protected_files,
            "execution_rules": execution_rules,
            "atomic_dataset": atomic_dataset,
            "summary": {
                "total_files": len(critical_files),
                "total_tools": len(tool_schemas),
                "total_protected": len(protected_files),
                "total_rules": len(execution_rules),
                "strict_protected": len(
                    [p for p in protected_files if p["protection_level"] == "strict"]
                ),
                "mandatory_rules": len(
                    [r for r in execution_rules if r.get("mandatory", False)]
                ),
            },
        }

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.log(f"Report saved to: {output_path}")

        return report

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _calculate_report_hash(self, atomic_dataset: List[Dict[str, Any]]) -> str:
        """Calculate hash of atomic dataset for verification."""
        dataset_str = json.dumps(atomic_dataset, sort_keys=True)
        return hashlib.sha256(dataset_str.encode()).hexdigest()[:16]

    def validate_invariants(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the extracted invariants for consistency and completeness.
        """
        self.log("Validating invariants...")

        validation_results = {"passed": [], "warnings": [], "errors": []}

        # Check for duplicate atomic IDs
        atomic_ids = [item["atomic_id"] for item in report["atomic_dataset"]]
        duplicates = set([id for id in atomic_ids if atomic_ids.count(id) > 1])
        if duplicates:
            validation_results["errors"].append(
                {
                    "check": "unique_atomic_ids",
                    "message": f"Duplicate atomic IDs found: {list(duplicates)}",
                    "severity": "error",
                }
            )

        # Check for missing enforcement points
        missing_enforcement = [
            item
            for item in report["atomic_dataset"]
            if not item.get("enforcement_point")
            or item["enforcement_point"] == "unknown"
        ]
        if missing_enforcement:
            validation_results["warnings"].append(
                {
                    "check": "enforcement_points",
                    "message": f"{len(missing_enforcement)} entries missing enforcement points",
                    "severity": "warning",
                }
            )

        # Check for mandatory flags on protected files
        unprotected_mandatory = [
            item
            for item in report["atomic_dataset"]
            if item.get("tool_or_rule") == "PROTECTED"
            and not item.get("mandatory", False)
        ]
        if unprotected_mandatory:
            validation_results["errors"].append(
                {
                    "check": "protected_mandatory",
                    "message": f"{len(unprotected_mandatory)} protected files not marked as mandatory",
                    "severity": "error",
                }
            )

        # Check hash consistency
        calculated_hash = self._calculate_report_hash(report["atomic_dataset"])
        if report["metadata"]["hash"] != calculated_hash:
            validation_results["errors"].append(
                {
                    "check": "hash_consistency",
                    "message": f"Hash mismatch: expected {report['metadata']['hash']}, got {calculated_hash}",
                    "severity": "error",
                }
            )

        validation_results["passed"].append(
            {
                "check": "basic_structure",
                "message": f"Report contains {len(report['atomic_dataset'])} atomic invariants",
            }
        )

        return validation_results


def main():
    """Main entry point for the invariant extraction system."""
    parser = argparse.ArgumentParser(
        description="Extract atomic invariants from repository for corporate-style enforcement"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="invariants.json",
        help="Output JSON file (default: invariants.json)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--validate", action="store_true", help="Validate invariants after extraction"
    )

    args = parser.parse_args()

    # Create extractor
    extractor = AtomicInvariantExtractor(root_dir=args.root, verbose=args.verbose)

    # Generate report
    report = extractor.generate_invariants_report(output_file=args.output)

    # Validate if requested
    if args.validate:
        validation = extractor.validate_invariants(report)

        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)

        for result_type in ["errors", "warnings", "passed"]:
            items = validation[result_type]
            if items:
                print(f"\n{result_type.upper()}: {len(items)}")
                for item in items:
                    print(f"  • {item['message']}")

    # Print summary
    print("\n" + "=" * 60)
    print("INVARIANTS EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Root directory: {args.root}")
    print(f"Output file: {args.output}")
    print(f"Total invariants: {report['metadata']['total_invariants']}")
    print(f"Generated at: {report['metadata']['generated_at']}")
    print(f"Report hash: {report['metadata']['hash']}")

    summary = report["summary"]
    print(f"\nSummary:")
    print(f"  • Critical files: {summary['total_files']}")
    print(f"  • Tool schemas: {summary['total_tools']}")
    print(
        f"  • Protected files: {summary['total_protected']} ({summary['strict_protected']} strict)"
    )
    print(
        f"  • Execution rules: {summary['total_rules']} ({summary['mandatory_rules']} mandatory)"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
