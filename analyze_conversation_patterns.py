#!/usr/bin/env python3
"""
Conversation Pattern Analysis for Orthogonal Engineering

Analyzes depth_analysis_FULL.json to validate methodology claims about:
- Turn-taking patterns (canal-like structure)
- Depth scores (invariant extraction success)
- Message patterns (drift vs signal)
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def analyze_conversation_patterns(json_path: str) -> Dict:
    """Analyze conversation patterns for orthogonal engineering validation."""
    print(f"Analyzing {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Extract metrics
    depth_scores = []
    turn_ratios = []
    msg_counts = []
    durations = []
    
    # Categorize by depth (invariant extraction success proxy)
    high_depth = []  # depth_score > 0.5 (successful invariant extraction)
    medium_depth = []  # 0.3 <= depth_score <= 0.5
    low_depth = []  # depth_score < 0.3 (high drift, low signal)
    
    # Categorize by turn ratio (canal structure proxy)
    balanced_turns = []  # 0.8 <= turn_ratio <= 1.2 (good canal)
    imbalanced_turns = []  # turn_ratio < 0.8 or > 1.2 (drift)
    
    for conv in conversations:
        depth = conv.get('depth_score', 0)
        turn_ratio = conv.get('turn_ratio', 0)
        msg_count = conv.get('msg_count', 0)
        duration = conv.get('duration_hours', 0)
        
        depth_scores.append(depth)
        turn_ratios.append(turn_ratio)
        msg_counts.append(msg_count)
        durations.append(duration)
        
        # Categorize by depth
        if depth > 0.5:
            high_depth.append(conv)
        elif depth >= 0.3:
            medium_depth.append(conv)
        else:
            low_depth.append(conv)
        
        # Categorize by turn ratio
        if 0.8 <= turn_ratio <= 1.2:
            balanced_turns.append(conv)
        else:
            imbalanced_turns.append(conv)
    
    # Compute statistics
    def safe_mean(lst):
        return statistics.mean(lst) if lst else 0
    
    def safe_median(lst):
        return statistics.median(lst) if lst else 0
    
    def safe_stdev(lst):
        return statistics.stdev(lst) if len(lst) > 1 else 0
    
    stats = {
        'depth_score': {
            'mean': safe_mean(depth_scores),
            'median': safe_median(depth_scores),
            'stdev': safe_stdev(depth_scores),
            'min': min(depth_scores) if depth_scores else 0,
            'max': max(depth_scores) if depth_scores else 0
        },
        'turn_ratio': {
            'mean': safe_mean(turn_ratios),
            'median': safe_median(turn_ratios),
            'stdev': safe_stdev(turn_ratios),
            'min': min(turn_ratios) if turn_ratios else 0,
            'max': max(turn_ratios) if turn_ratios else 0
        },
        'message_count': {
            'mean': safe_mean(msg_counts),
            'median': safe_median(msg_counts),
            'stdev': safe_stdev(msg_counts),
            'min': min(msg_counts) if msg_counts else 0,
            'max': max(msg_counts) if msg_counts else 0
        },
        'duration_hours': {
            'mean': safe_mean(durations),
            'median': safe_median(durations),
            'stdev': safe_stdev(durations),
            'min': min(durations) if durations else 0,
            'max': max(durations) if durations else 0
        }
    }
    
    # Methodology validation metrics
    methodology_validation = {
        'total_conversations': len(conversations),
        'high_depth_count': len(high_depth),
        'high_depth_rate': len(high_depth) / len(conversations) if conversations else 0,
        'balanced_turn_count': len(balanced_turns),
        'balanced_turn_rate': len(balanced_turns) / len(conversations) if conversations else 0,
        'invariant_extraction_success_rate': len(high_depth) / len(conversations) if conversations else 0,
        'canal_structure_success_rate': len(balanced_turns) / len(conversations) if conversations else 0
    }
    
    # Correlation analysis (depth vs turn ratio)
    # High depth + balanced turns = successful canal + invariant extraction
    successful_patterns = [
        conv for conv in conversations
        if conv.get('depth_score', 0) > 0.5 and 0.8 <= conv.get('turn_ratio', 0) <= 1.2
    ]
    
    methodology_validation['successful_pattern_count'] = len(successful_patterns)
    methodology_validation['successful_pattern_rate'] = len(successful_patterns) / len(conversations) if conversations else 0
    
    # Top conversations by depth (best invariant extraction examples)
    top_by_depth = sorted(conversations, key=lambda x: x.get('depth_score', 0), reverse=True)[:10]
    
    return {
        'metadata': {
            'source_file': json_path,
            'total_conversations': len(conversations),
            'analysis_date': Path(json_path).stat().st_mtime if Path(json_path).exists() else None
        },
        'statistics': stats,
        'categorization': {
            'by_depth': {
                'high': len(high_depth),
                'medium': len(medium_depth),
                'low': len(low_depth)
            },
            'by_turn_ratio': {
                'balanced': len(balanced_turns),
                'imbalanced': len(imbalanced_turns)
            }
        },
        'methodology_validation': methodology_validation,
        'top_conversations_by_depth': [
            {
                'id': conv.get('id'),
                'title': conv.get('title'),
                'depth_score': conv.get('depth_score'),
                'turn_ratio': conv.get('turn_ratio'),
                'msg_count': conv.get('msg_count')
            }
            for conv in top_by_depth
        ]
    }

if __name__ == '__main__':
    import sys
    
    json_path = sys.argv[1] if len(sys.argv) > 1 else r'c:\Users\Aidor\Desktop\depth_analysis_FULL.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'data/conversation_patterns_analysis.json'
    
    print(f"Reading from: {json_path}")
    print(f"Writing to: {output_path}")
    
    results = analyze_conversation_patterns(json_path)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete!")
    print(f"Total conversations: {results['metadata']['total_conversations']}")
    print(f"\nMethodology Validation:")
    print(f"  High depth (successful invariant extraction): {results['methodology_validation']['high_depth_rate']:.2%}")
    print(f"  Balanced turns (canal structure): {results['methodology_validation']['balanced_turn_rate']:.2%}")
    print(f"  Successful patterns (both): {results['methodology_validation']['successful_pattern_rate']:.2%}")
    print(f"\nStatistics:")
    print(f"  Mean depth score: {results['statistics']['depth_score']['mean']:.3f}")
    print(f"  Mean turn ratio: {results['statistics']['turn_ratio']['mean']:.3f}")
