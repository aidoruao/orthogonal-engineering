#!/usr/bin/env python3
"""
Final AI File Analyzer for Orthogonal Engineering
Direct analysis of AI conversation files.
"""
import json
import os
import re
from datetime import datetime

def analyze_ai_files():
    """Analyze AI conversation files in Downloads."""
    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - AI FILE ANALYSIS")
    print("=" * 70)
    
    # Target specific AI conversation files
    target_files = [
        "C:/Users/Aidor/Downloads/claude 1.txt",
        "C:/Users/Aidor/Downloads/claude desktop commander invariant executor output.txt",
        "C:/Users/Aidor/Downloads/deepseek ai msg fowarded to gemini ai by user 1.txt",
        "C:/Users/Aidor/Downloads/deepseek_text_20260119_05223d.txt",
        "C:/Users/Aidor/Downloads/deepseek_text_20260119_da08ea.txt",
        "C:/Users/Aidor/Downloads/devin 1.txt",
        "C:/Users/Aidor/Downloads/devin, notebookllm, claude ai 1.txt",
    ]
    
    analyses = []
    total_size = 0
    total_lines = 0
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            print(f"Missing: {os.path.basename(file_path)}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Basic analysis
            size = len(content)
            lines = content.split('\n')
            line_count = len(lines)
            
            # Look for AI model mentions
            models = []
            if 'claude' in content.lower():
                models.append('Claude')
            if 'deepseek' in content.lower():
                models.append('DeepSeek')
            if 'chatgpt' in content.lower() or 'gpt' in content.lower():
                models.append('ChatGPT')
            if 'gemini' in content.lower():
                models.append('Gemini')
                
            # Look for canal patterns
            canal_patterns = {
                'code_blocks': len(re.findall(r'```', content)),
                'invariant_tags': len(re.findall(r'\[INVARIANT\]', content)),
                'structured_lists': len(re.findall(r'\n\d+\.|\n[•*-]\s+', content)),
                'explicit_answers': len(re.findall(r'(?:Answer|Solution|Code|Implementation):', content, re.IGNORECASE)),
            }
            
            total_canal = sum(canal_patterns.values())
            
            # Estimate conversation turns (paragraphs)
            paragraphs = [p for p in content.split('\n\n') if p.strip()]
            turn_estimate = len(paragraphs)
            
            analysis = {
                'file': os.path.basename(file_path),
                'size': size,
                'lines': line_count,
                'estimated_turns': turn_estimate,
                'models': list(set(models)),
                'canal_patterns': canal_patterns,
                'total_canal_candidates': total_canal,
                'canal_density': total_canal / turn_estimate if turn_estimate > 0 else 0,
                'sample': content[:200].replace('\n', ' ').strip() + '...',
                'analyzed_at': datetime.now().isoformat(),
            }
            
            analyses.append(analysis)
            total_size += size
            total_lines += line_count
            
            print(f"✓ {os.path.basename(file_path)}: {size:,} bytes, {turn_estimate} turns, {total_canal} canal candidates")
            
        except Exception as e:
            print(f"✗ {os.path.basename(file_path)}: Error - {e}")
    
    print("-" * 70)
    
    # Generate summary
    total_turns = sum(a['estimated_turns'] for a in analyses)
    total_canal = sum(a['total_canal_candidates'] for a in analyses)
    overall_density = total_canal / total_turns if total_turns > 0 else 0
    
    # Count models
    model_counts = {}
    for analysis in analyses:
        for model in analysis['models']:
            model_counts[model] = model_counts.get(model, 0) + 1
    
    print(f"SUMMARY:")
    print(f"  Files analyzed: {len(analyses)}")
    print(f"  Total size: {total_size:,} bytes")
    print(f"  Total turns: {total_turns}")
    print(f"  Total canal candidates: {total_canal}")
    print(f"  Overall canal density: {overall_density:.1%}")
    print(f"  Models found: {', '.join(model_counts.keys())}")
    
    # Create report
    report = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'methodology': 'Orthogonal Engineering Direct Analysis',
            'files_analyzed': len(analyses),
            'principles_applied': [
                'Direct file analysis',
                'Canal pattern detection',
                'Model identification',
                'Density calculation',
                'Falsifiable claims generation',
            ],
        },
        'summary': {
            'total_files': len(analyses),
            'total_size': total_size,
            'total_turns': total_turns,
            'total_canal_candidates': total_canal,
            'overall_canal_density': overall_density,
            'model_distribution': model_counts,
        },
        'falsifiable_claims': [
            {
                'claim_id': 'DIRECT-001-DENSITY',
                'statement': f'The canal density in analyzed AI files is {overall_density:.1%}',
                'falsification_test': 'Manual review of canal candidates in the same files',
                'falsification_condition': 'If manual count differs by >25% from automated count',
                'confidence': 0.7,
                'evidence': f'Based on {len(analyses)} files with {total_turns} estimated turns',
            },
            {
                'claim_id': 'DIRECT-002-MODELS',
                'statement': f'AI models present: {", ".join(model_counts.keys())}',
                'falsification_test': 'Independent model detection',
                'falsification_condition': 'If independent detection finds different models',
                'confidence': 0.8,
                'evidence': f'Found in {len(analyses)} files',
            },
        ],
        'detailed_analyses': analyses,
        'correspondence_evidence': {
            'file_existence': f'All {len(analyses)} files exist and were analyzed',
            'content_samples': 'First 200 characters stored for each file',
            'manual_verification': 'Sample content allows direct checking',
        },
    }
    
    # Save report
    output_file = f"ai_file_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("FALSIFIABLE CLAIMS GENERATED:")
    for claim in report['falsifiable_claims']:
        print(f"\n{claim['claim_id']}: {claim['statement']}")
        print(f"  Test: {claim['falsification_test']}")
    
    print("\n" + "=" * 70)
    print("PHASE 2 COMPLETE: AI Conversation Processing")
    print("=" * 70)
    print("Implemented:")
    print("1. Direct analysis of AI conversation files")
    print("2. Canal pattern detection and counting")
    print("3. Density calculation with falsifiable claims")
    print("4. Model identification and distribution")
    print("5. Report generation with correspondence evidence")
    
    return output_file

if __name__ == '__main__':
    analyze_ai_files()
