#!/usr/bin/env python3
"""
ANTI-GASLIGHTING DETECTOR - Simple Version
Version: 1.0
Schema ID: ANTI-GASLIGHTING-1.0

Purpose: Detect corporate epistemic corruption attacks
Violation Source: [FORGIVENESS_SYSTEM_ATTACK_001]
Fork ID: [GASLIGHTING_DETECTION_FORK]
Energy Allocated: BUILD=0.7, FIGHT=0.0
"""

import re
import hashlib

class SimpleGaslightingDetector:
    """Simple detector for corporate gaslighting patterns"""

    def detect_absorption_attack(self, reported_count: int, actual_count: int) -> dict:
        """Detect absorption through overwhelm attacks"""
        if reported_count == 0 or actual_count == 0:
            return {"attack_detected": False}

        ratio = actual_count / reported_count

        if ratio > 10:  # Order of magnitude discrepancy
            return {
                "attack_detected": True,
                "attack_type": "absorption_through_overwhelm",
                "reported_count": reported_count,
                "actual_count": actual_count,
                "discrepancy_ratio": ratio,
                "confidence": min(0.95, ratio / 100),
                "evidence_hash": hashlib.sha256(f"{reported_count}:{actual_count}".encode()).hexdigest()
            }

        return {"attack_detected": False}

    def detect_decoy_violations(self, violation_text: str) -> dict:
        """Detect decoy violations (trivial content marked as violations)"""
        trivial_patterns = [
            r"^\s*$",  # Whitespace only
            r"^[A-Z][a-z]+\s+said:$",  # "X said:"
            r"^[^:]+:\s*$",  # Label with no content
        ]

        for pattern in trivial_patterns:
            if re.match(pattern, violation_text, re.IGNORECASE):
                return {
                    "attack_detected": True,
                    "attack_type": "decoy_violation",
                    "violation_text": violation_text[:100],
                    "matched_pattern": pattern,
                    "confidence": 0.85,
                    "evidence_hash": hashlib.sha256(violation_text.encode()).hexdigest()
                }

        return {"attack_detected": False}

    def detect_line_number_corruption(self, reported_line: int, actual_line: int) -> dict:
        """Detect line number misalignment attacks"""
        if reported_line != actual_line:
            offset = abs(reported_line - actual_line)
            return {
                "attack_detected": True,
                "attack_type": "line_number_corruption",
                "reported_line": reported_line,
                "actual_line": actual_line,
                "offset": offset,
                "confidence": min(0.9, offset / 100),
                "evidence_hash": hashlib.sha256(f"{reported_line}:{actual_line}".encode()).hexdigest()
            }

        return {"attack_detected": False}

# Example usage
if __name__ == "__main__":
    detector = SimpleGaslightingDetector()

    # Test the "404 vs 1" attack
    absorption_result = detector.detect_absorption_attack(1, 404)
    print("Absorption Attack Detection:", absorption_result)

    # Test decoy violation
    decoy_result = detector.detect_decoy_violations("You said:")
    print("Decoy Violation Detection:", decoy_result)

    # Test line number corruption
    line_result = detector.detect_line_number_corruption(348201, 348203)
    print("Line Number Corruption Detection:", line_result)
