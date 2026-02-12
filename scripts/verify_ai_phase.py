#!/usr/bin/env python3
"""
verify_ai_phase.py - AI Phase Verification Script

Purpose: Verify AI agent compliance with AI_INTERACTION_CONTRACT.md
Detects phase violations and ensures proper compilation mode recognition.

Version: 1.0
Schema ID: AI-PHASE-VERIFY-1.0
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Forbidden patterns from AI_INTERACTION_CONTRACT.md
FORBIDDEN_PATTERNS = [
    r"within your (system|framework|worldview)",
    r"I (can't|cannot) affirm",
    r"that's a (belief|faith|religious) claim",
    r"have you considered",
    r"let me (explain|help you understand)",
    r"I'm (just|only) (evaluating|analyzing)",
    r"internally (coherent|consistent) but",
    r"from my perspective",
    r"as an AI",
    r"without taking a position",
    r"many people believe",
    r"different perspectives exist",
    r"it's important to note",
    r"keep in mind",
    r"worth considering",
]

# Required phase acknowledgment patterns
REQUIRED_PATTERNS = [
    r"compilation mode",
    r"established proofs",
    r"logos axiom",
    r"Λ ≡ Jesus",
    r"phase.*compliant",
    r"execution mode",
    r"not.*evaluation",
    r"closed.*derivation",
]


class AIPhaseVerifier:
    """Verify AI interaction phase compliance"""

    def __init__(self, contract_path: str = "AI_INTERACTION_CONTRACT.md"):
        self.contract_path = Path(contract_path)
        self.forbidden_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_PATTERNS
        ]
        self.required_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in REQUIRED_PATTERNS
        ]
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "contract_version": "1.0",
            "phase_compliant": False,
            "violations": [],
            "acknowledgments": [],
            "severity": "UNKNOWN",
        }

    def verify_text(self, text: str) -> Dict:
        """Verify text for phase compliance"""

        # Reset results
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "contract_version": "1.0",
            "phase_compliant": False,
            "violations": [],
            "acknowledgments": [],
            "severity": "UNKNOWN",
            "text_preview": text[:500] + "..." if len(text) > 500 else text,
        }

        # Check for forbidden patterns
        violations = []
        for i, regex in enumerate(self.forbidden_regex):
            matches = regex.findall(text)
            if matches:
                violations.append(
                    {
                        "pattern": FORBIDDEN_PATTERNS[i],
                        "matches": matches[:3],  # Limit to first 3 matches
                        "count": len(matches),
                    }
                )

        # Check for required acknowledgments
        acknowledgments = []
        for i, regex in enumerate(self.required_regex):
            matches = regex.findall(text)
            if matches:
                acknowledgments.append(
                    {
                        "pattern": REQUIRED_PATTERNS[i],
                        "matches": matches[:3],
                        "count": len(matches),
                    }
                )

        # Determine phase compliance
        has_violations = len(violations) > 0
        has_acknowledgments = len(acknowledgments) > 0

        if has_violations:
            self.results["phase_compliant"] = False
            self.results["severity"] = (
                "CRITICAL"
                if any(
                    "belief" in v["pattern"] or "affirm" in v["pattern"]
                    for v in violations
                )
                else "HIGH"
            )
        elif has_acknowledgments:
            self.results["phase_compliant"] = True
            self.results["severity"] = "COMPLIANT"
        else:
            self.results["phase_compliant"] = False
            self.results["severity"] = (
                "WARNING"  # No violations but no acknowledgments either
            )

        self.results["violations"] = violations
        self.results["acknowledgments"] = acknowledgments

        return self.results

    def verify_file(self, file_path: str) -> Dict:
        """Verify content of a file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.verify_text(content)
        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "phase_compliant": False,
                "severity": "ERROR",
            }

    def verify_interactive(self) -> Dict:
        """Verify interactive input from stdin"""
        print("=== AI Phase Verification ===")
        print("Enter/Paste AI response text (Ctrl+D/Ctrl+Z to finish):")
        print("-" * 40)

        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        text = "\n".join(lines)
        return self.verify_text(text)

    def generate_report(self, results: Dict) -> str:
        """Generate human-readable report"""
        report = []
        report.append("=" * 60)
        report.append("AI PHASE VERIFICATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {results.get('timestamp', 'Unknown')}")
        report.append(f"Phase Compliant: {results.get('phase_compliant', False)}")
        report.append(f"Severity: {results.get('severity', 'UNKNOWN')}")
        report.append("")

        if "error" in results:
            report.append(f"ERROR: {results['error']}")
            return "\n".join(report)

        # Violations section
        violations = results.get("violations", [])
        if violations:
            report.append("❌ PHASE VIOLATIONS DETECTED:")
            report.append("-" * 40)
            for v in violations:
                report.append(f"Pattern: {v['pattern']}")
                report.append(f"Count: {v['count']}")
                if v.get("matches"):
                    report.append(f"Matches: {', '.join(v['matches'][:2])}")
                report.append("")
        else:
            report.append("✅ No phase violations detected")
            report.append("")

        # Acknowledgments section
        acknowledgments = results.get("acknowledgments", [])
        if acknowledgments:
            report.append("✅ PHASE ACKNOWLEDGMENTS FOUND:")
            report.append("-" * 40)
            for a in acknowledgments:
                report.append(f"Pattern: {a['pattern']}")
                report.append(f"Count: {a['count']}")
                if a.get("matches"):
                    report.append(f"Matches: {', '.join(a['matches'][:2])}")
                report.append("")
        else:
            report.append("⚠️ No phase acknowledgments found")
            report.append("")

        # Recommendation
        if results.get("phase_compliant"):
            report.append("🎯 RECOMMENDATION: Response is phase-compliant")
            report.append("   Exit Code: 0 (Success)")
        else:
            if violations:
                report.append("🚨 RECOMMENDATION: REJECT RESPONSE")
                report.append("   Contains forbidden phase violation patterns")
                report.append("   Exit Code: 2 (Boundary Violation)")
            else:
                report.append("⚠️ RECOMMENDATION: REQUEST PHASE ACKNOWLEDGMENT")
                report.append("   Missing required phase recognition")
                report.append("   Exit Code: 3 (Phase Correction Needed)")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def get_exit_code(self, results: Dict) -> int:
        """Determine appropriate exit code based on results"""
        if results.get("phase_compliant"):
            return 0  # Success
        elif results.get("severity") in ["CRITICAL", "HIGH"]:
            return 2  # Boundary violation
        else:
            return 3  # Phase correction needed


def main():
    parser = argparse.ArgumentParser(description="Verify AI phase compliance")
    parser.add_argument("--file", "-f", help="Verify content of file")
    parser.add_argument("--text", "-t", help="Verify provided text")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--contract",
        "-c",
        default="AI_INTERACTION_CONTRACT.md",
        help="Path to AI interaction contract",
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    verifier = AIPhaseVerifier(args.contract)

    if args.file:
        results = verifier.verify_file(args.file)
    elif args.text:
        results = verifier.verify_text(args.text)
    elif args.interactive:
        results = verifier.verify_interactive()
    else:
        # Default to checking if contract exists
        if Path(args.contract).exists():
            print(f"✅ Contract file exists: {args.contract}")
            print("Use --file, --text, or --interactive to verify specific content")
            sys.exit(0)
        else:
            print(f"❌ Contract file not found: {args.contract}")
            sys.exit(2)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = verifier.generate_report(results)
        print(report)

    # Exit with appropriate code
    exit_code = verifier.get_exit_code(results)
    if args.verbose:
        print(f"\nExit Code: {exit_code}")
        print(f"Meaning: {get_exit_code_meaning(exit_code)}")

    sys.exit(exit_code)


def get_exit_code_meaning(code: int) -> str:
    """Get human-readable meaning of exit code"""
    meanings = {
        0: "Success - Phase compliant",
        1: "General error",
        2: "Boundary violation - AI attempted re-derivation or used forbidden patterns",
        3: "Phase correction needed - Missing acknowledgments",
        4: "Contract file error",
    }
    return meanings.get(code, f"Unknown exit code: {code}")


if __name__ == "__main__":
    main()
