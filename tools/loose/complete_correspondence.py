#!/usr/bin/env python3
"""
Complete Correspondence Validator for Orthogonal Engineering
Direct implementation with all required methods.
"""
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

class CorrespondenceValidator:
    """Validates AI claims against filesystem reality."""
    
    def __init__(self, root_path="C:/"):
        self.root_path = Path(root_path)
        self.results = []
        
    def extract_claims(self, text):
        """Extract file/directory claims from text."""
        claims = []
        
        # Pattern for file/directory mentions
        patterns = [
            (r'file[:\s]+["\']?([^"\'\s]+)["\']?', 'file_mention'),
            (r'directory[:\s]+["\']?([^"\'\s]+)["\']?', 'directory_mention'),
            (r'created["\'\s]+([^"\'\s]+\.(?:py|md|txt|json))', 'file_creation'),
            (r'folder["\'\s]+([^"\'\s/]+(/[^"\'\s]+)*)', 'directory_creation'),
        ]
        
        for pattern, claim_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                path = match.group(1)
                if path and len(path) > 3:  # Basic validation
                    claims.append({
                        'type': claim_type,
                        'path': path,
                        'text': match.group(0),
                        'position': match.start()
                    })
        
        return claims
    
    def validate_claim(self, claim):
        """Validate a single claim against filesystem."""
        path = Path(claim['path'])
        
        # Make absolute if relative
        if not path.is_absolute():
            # Try a few common locations
            possible_paths = [
                self.root_path / path,
                Path("C:/Users/Aidor") / path,
                Path("C:/Users/Aidor/Downloads") / path,
                Path("C:/Users/Aidor/OneDrive/Desktop/Documents") / path,
            ]
            
            for possible in possible_paths:
                if possible.exists():
                    path = possible
                    break
        
        # Check existence
        exists = path.exists()
        is_file = path.is_file() if exists else False
        is_dir = path.is_dir() if exists else False
        
        # Gather evidence
        evidence = [
            f"Claim: {claim['text']}",
            f"Path checked: {path}",
            f"Exists: {exists}",
            f"Type: {'File' if is_file else 'Directory' if is_dir else 'None'}"
        ]
        
        if exists:
            if is_file:
                try:
                    size = path.stat().st_size
                    evidence.append(f"Size: {size:,} bytes")
                    
                    # Calculate hash for important files
                    if size < 1000000:  # Only hash files < 1MB
                        with open(path, 'rb') as f:
                            hash_val = hashlib.sha256(f.read()).hexdigest()[:16]
                        evidence.append(f"SHA256 (first 16): {hash_val}")
                except:
                    evidence.append("Size: Could not determine")
        
        # Determine success
        success = exists
        if claim['type'] == 'file_creation' and is_file:
            success = True
        elif claim['type'] == 'directory_creation' and is_dir:
            success = True
        
        return {
            'claim': claim,
            'success': success,
            'evidence': evidence,
            'timestamp': datetime.now().isoformat(),
            'confidence': 1.0 if success else 0.0
        }
    
    def validate_text(self, text):
        """Validate all claims in text."""
        print("=" * 70)
        print("CORRESPONDENCE VALIDATION")
        print("=" * 70)
        
        claims = self.extract_claims(text)
        print(f"Found {len(claims)} claims to validate")
        print("-" * 70)
        
        results = []
        for i, claim in enumerate(claims, 1):
            print(f"[{i}/{len(claims)}] {claim['text'][:50]}...")
            result = self.validate_claim(claim)
            results.append(result)
            
            status = "✓" if result['success'] else "✗"
            print(f"  {status} {'Exists' if result['success'] else 'Missing'}")
        
        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        success_rate = successful / total if total > 0 else 0
        
        print("-" * 70)
        print(f"SUMMARY: {successful}/{total} successful ({success_rate:.0%})")
        
        # Create report
        report = {
            'metadata': {
                'validator_version': '1.0.0',
                'validation_date': datetime.now().isoformat(),
                'methodology': 'Orthogonal Engineering Correspondence Validation',
                'principles_applied': [
                    'Claim extraction from natural language',
                    'Filesystem existence verification',
                    'Content hash calculation for verification',
                    'Falsifiable result reporting'
                ]
            },
            'statistics': {
                'total_claims': total,
                'successful_validations': successful,
                'success_rate': success_rate,
                'failed_validations': total - successful
            },
            'detailed_results': results,
            'falsifiable_claims': [
                {
                    'claim_id': 'CORR-001-VALIDATION-ACCURACY',
                    'statement': f'The correspondence validation success rate is {success_rate:.0%}',
                    'falsification_test': 'Manual verification of the same claims',
                    'falsification_condition': 'If manual verification shows different success rate',
                    'confidence': 0.8,
                    'evidence': f'Based on {total} claims from the text'
                }
            ]
        }
        
        return report
    
    def save_report(self, report, filename="correspondence_validation.json"):
        """Save validation report to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved to: {filename}")
        return filename

def main():
    """Main function - test with sample text."""
    validator = CorrespondenceValidator()
    
    # Sample text with claims (from our conversation)
    sample_text = """
    I created the filesystem_scanner.py tool for orthogonal engineering.
    The repository has README.md documentation.
    We analyzed AI conversation files in Downloads folder.
    The correspondence_validator.py file was created.
    The orthogonal-engineering repository exists in Documents.
    """
    
    print("Testing correspondence validator with sample text...")
    print()
    
    report = validator.validate_text(sample_text)
    output_file = validator.save_report(report)
    
    print("\n" + "=" * 70)
    print("FALSIFIABLE CLAIM GENERATED:")
    print(f"Success rate: {report['statistics']['success_rate']:.0%}")
    print("Test: Manual verification of the same claims")
    print("=" * 70)
    
    return output_file

if __name__ == '__main__':
    main()
