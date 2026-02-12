#!/usr/bin/env python3
"""
SHOW_UNICODE_FIXES.py — Shows exact Unicode fixes needed for mathematical proof system

This script identifies all Unicode characters in controller_proven.py and 
test_mathematically_proven.py that cause encoding errors on Windows CP1252 console.
It shows the exact lines that need fixing and provides ASCII replacements.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


def find_unicode_characters(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find all Unicode characters in a file with line numbers."""
    results = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find all non-ASCII characters
            unicode_chars = re.findall(r'[^\x00-\x7F]', line)
            if unicode_chars:
                # Get character positions
                for char in unicode_chars:
                    char_pos = line.find(char)
                    results.append((line_num, char, line.strip()))
                    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return results


def get_ascii_replacement(char: str) -> str:
    """Get ASCII replacement for Unicode character."""
    replacements = {
        # Emojis
        '⚡': '[LIGHTNING]',  # U+26A1
        '✅': '[OK]',         # U+2705
        '❌': '[ERROR]',      # U+274C
        '🔬': '[ANALYZE]',    # U+1F52C
        '🚀': '[RUN]',        # U+1F680
        '🔍': '[CHECK]',      # U+1F50D
        '📊': '[STATS]',      # U+1F4CA
        '⚠': '[WARNING]',     # U+26A0
        '✓': '[CHECK]',       # U+2713
        '✗': '[FAIL]',        # U+2717
        
        # Punctuation
        '—': '--',            # U+2014 (em dash)
        '•': '*',             # U+2022 (bullet)
        
        # Variation selector (usually follows emoji)
        '️': '',              # U+FE0F
    }
    
    return replacements.get(char, f'[U+{ord(char):04X}]')


def analyze_file(file_path: Path) -> Dict:
    """Analyze a file for Unicode issues."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {file_path}")
    print(f"{'='*80}")
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return {}
    
    unicode_chars = find_unicode_characters(file_path)
    
    if not unicode_chars:
        print("✅ No Unicode characters found")
        return {}
    
    # Group by line
    lines_dict = {}
    for line_num, char, line_text in unicode_chars:
        if line_num not in lines_dict:
            lines_dict[line_num] = {
                'text': line_text,
                'chars': set(),
                'positions': []
            }
        lines_dict[line_num]['chars'].add(char)
        # Find all positions of this char in the line
        positions = [i for i, c in enumerate(line_text) if c == char]
        lines_dict[line_num]['positions'].extend(positions)
    
    print(f"Found {len(unicode_chars)} Unicode characters in {len(lines_dict)} lines")
    print()
    
    # Show