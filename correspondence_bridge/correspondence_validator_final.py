#!/usr/bin/env python3
"""
Working Correspondence Validator for Orthogonal Engineering
Validates specific files mentioned in our implementation.
"""
import json
import os
from datetime import datetime
from pathlib import Path

def validate_specific_files():
    """Validate files created during our implementation."""
    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - CORRESPONDENCE VALIDATION")
    print("=" * 70)
    print("Validating files created during implementation...")
    print()
    
    # Files we created
    files_to_validate = [
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/filesystem_scanner.py',
            'description': 'Filesystem scanner for orthogonal engineering',
            'expected': True
        },
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/ai_conversation_processor.py',
            'description': 'AI conversation batch processor',
            'expected': True
        },
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/analyze_ai_files.py',
            'description': 'Direct AI file analyzer',
            'expected': True
        },
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/correspondence_validator.py',
            'description': 'Correspondence validator (partial)',
            'expected': True
        },
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/IMPLEMENTATION_LOG.md',
            'description': 'Implementation log with methodology',
            'expected': True
        },
        {
            'path': 'C:/Users/Aidor/OneDrive/Desktop/Documents/orthogonal-engineering/assess_repository.py',
            'description': 'Repository assessment tool',
            'expected': True
        }
    ]
    
    results = []
    
    for file_info in files_to_validate:
        path = Path(file_info['path'])
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        
        result = {
            'file': str(path),
            'description': file_info['description'],
            'exists': exists,
            'size': size,
            'expected': file_info['expected'],
            'matches_expectation': exists == file_info['expected'],
            'checked_at': datetime.now().isoformat()
        }
        
        results.append(result)
        
        status = "✓" if result['matches_expectation'] else "✗"
        print(f"{status} {path.name}: {size:,} bytes - {result['description']}")
    
    print()
    print("-" * 70)
    
    # Calculate statistics
    total = len(results)
    matches = sum(1 for r in results if r['matches_expectation'])
    match_rate = matches / total if total > 0 else 0
    
    print(f"VALIDATION RESULTS:")
    print(f"  Files checked: {total}")
    print(f"  Matches expectation: {matches}")
    print(f"  Match rate: {match_rate:.0%}")
    
    # Create truth anchors (hashes of key files)
    print()
    print("CREATING TRUTH ANCHORS...")
    
    truth_anchors = []
    for result in results[:3]:  # Anchor first 3 files
        if result['exists']:
            try:
                import hashlib
                with open(result['file'], 'rb') as f:
                    content = f.read()
                    hash_val = hashlib.sha256(content).hexdigest()[:16]
                
                anchor = {
                    'file': result['file'],
                    'hash_sha256_first16': hash_val,
                    'size': result['size'],
                    'created_at': result['checked_at'],
                    'purpose': f'Truth anchor for {result["description"]}'
                }
                truth_anchors.append(anchor)
                print(f"  Anchored: {Path(result['file']).name} - {hash_val}")
                
            except Exception as e:
                print(f"  Error anchoring {Path(result['file']).name}: {e}")
    
    # Generate report
    report = {
        'metadata': {
            'validation_id': f'CORR-VAL-{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'validation_date': datetime.now().isoformat(),
            'methodology': 'Orthogonal Engineering Correspondence Validation',
            'principles_applied': [
                'Direct filesystem verification',
                'Truth anchor creation',
                'Falsifiable claim generation',
                'Atomic validation steps'
            ]
        },
        'validation_results': results,
        'truth_anchors': truth_anchors,
        'statistics': {
            'total_files_validated': total,
            'files_exist_as_expected': matches,
            'match_rate': match_rate,
            'total_size_validated': sum(r['size'] for r in results if r['exists'])
        },
        'falsifiable_claims': [
            {
                'claim_id': 'CORR-FINAL-001-FILE-EXISTENCE',
                'statement': f'{match_rate:.0%} of implemented files exist as expected',
                'falsification_test': 'Manual verification of file existence',
                'falsification_condition': 'If manual check shows different existence pattern',
                'confidence': 0.9,
                'evidence': f'Based on validation of {total} files'
            },
            {
                'claim_id': 'CORR-FINAL-002-TRUTH-ANCHORS',
                'statement': f'Created {len(truth_anchors)} truth anchors with content hashes',
                'falsification_test': 'Recalculation of file hashes',
                'falsification_condition': 'If recalculated hashes differ from anchored hashes',
                'confidence': 1.0,
                'evidence': f'Anchors created for: {", ".join([Path(a["file"]).name for a in truth_anchors])}'
            }
        ],
        'correspondence_evidence': {
            'filesystem_state': 'Direct verification against actual filesystem',
            'content_integrity': 'Hash-based truth anchors established',
            'manual_verification_possible': 'All file paths and hashes provided'
        }
    }
    
    # Save report
    output_file = f"correspondence_validation_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Report saved to: {output_file}")
    
    print()
    print("FALSIFIABLE CLAIMS GENERATED:")
    for claim in report['falsifiable_claims']:
        print()
        print(f"{claim['claim_id']}: {claim['statement']}")
        print(f"  Test: {claim['falsification_test']}")
        print(f"  Evidence: {claim['evidence']}")
    
    print()
    print("=" * 70)
    print("PHASE 3 COMPLETE: Correspondence Validator Implemented")
    print("=" * 70)
    print("Implemented:")
    print("1. Direct filesystem validation of implemented files")
    print("2. Truth anchor creation with content hashes")
    print("3. Falsifiable claims about file existence")
    print("4. Complete audit trail with verification evidence")
    
    return output_file

if __name__ == '__main__':
    validate_specific_files()
