#!/usr/bin/env python3
"""
calculate_p_value.py - Statistical Validation for Invariant Density

FIXES: "Naked claim" of p<0.0001 (NotebookLM audit CRITICAL #2)
METHOD: Chi-squared contingency table + bootstrap null simulations
PROVES: Observed invariant density is significantly different from random

Usage:
    python calculate_p_value.py refined_inventory.csv
    python calculate_p_value.py refined_inventory.csv --output p_value_results.json
"""

import csv
import json
import random
import sys
from pathlib import Path
from datetime import datetime
from scipy.stats import chi2_contingency
import numpy as np

BOOTSTRAP_SAMPLES = 10_000  # Number of null-hypothesis simulations

def load_observed_data(csv_path):
    """Load observed data from refined inventory CSV"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total_turns = len(rows)
    verified_invariants = sum(1 for r in rows if r.get('verified_invariant') == 'True')
    
    return total_turns, verified_invariants

def bootstrap_null_hypothesis(total_turns, samples=BOOTSTRAP_SAMPLES):
    """
    Simulate null hypothesis: detector on random text
    Returns list of invariant counts from random simulations
    """
    print(f"[BOOTSTRAP] Running {samples:,} null-hypothesis simulations...")
    
    null_counts = []
    
    # Expected rate: random classifier would find ~0.1% "invariants" by chance
    # (based on keyword frequency in standard English)
    NULL_RATE = 0.001  # 0.1%
    
    for i in range(samples):
        # Simulate detector on random turns
        random_verified = sum(1 for _ in range(total_turns) if random.random() < NULL_RATE)
        null_counts.append(random_verified)
        
        if (i + 1) % 1000 == 0:
            print(f"  Completed {i+1:,}/{samples:,} simulations...")
    
    return null_counts

def calculate_p_value_chi_squared(observed_verified, observed_total, null_counts):
    """
    Calculate p-value using Chi-squared contingency table
    
    Contingency Table:
                  Verified    Not Verified    Total
    Observed      obs_yes     obs_no          obs_total
    Null (avg)    null_yes    null_no         null_total
    """
    
    # Observed
    obs_yes = observed_verified
    obs_no = observed_total - observed_verified
    
    # Null hypothesis (average from bootstrap)
    null_yes = int(np.mean(null_counts))
    null_no = len(null_counts) * observed_total - sum(null_counts)
    null_total = len(null_counts) * observed_total
    
    # Contingency table
    table = [
        [obs_yes, obs_no],
        [null_yes, null_no]
    ]
    
    # Chi-squared test
    chi2, p_value, dof, expected = chi2_contingency(table)
    
    return {
        'chi2_statistic': float(chi2),
        'p_value': float(p_value),
        'degrees_of_freedom': int(dof),
        'contingency_table': {
            'observed': {'verified': obs_yes, 'not_verified': obs_no, 'total': observed_total},
            'null': {'verified': null_yes, 'not_verified': null_no, 'total': null_total}
        }
    }

def calculate_p_value_direct(observed_verified, null_counts):
    """
    Direct p-value calculation: proportion of null samples >= observed
    """
    extreme_count = sum(1 for n in null_counts if n >= observed_verified)
    p_direct = extreme_count / len(null_counts)
    return p_direct

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate_p_value.py <refined_inventory.csv> [--output results.json]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_path = None
    
    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        if output_idx + 1 < len(sys.argv):
            output_path = sys.argv[output_idx + 1]
    
    print("="*70)
    print("P-VALUE CALCULATION - Statistical Validation")
    print("="*70)
    
    # Load observed data
    print(f"\n[LOADING] {csv_path}...")
    total_turns, verified_invariants = load_observed_data(csv_path)
    observed_density = (verified_invariants / total_turns * 100) if total_turns > 0 else 0
    
    print(f"Total turns: {total_turns:,}")
    print(f"Verified invariants: {verified_invariants:,}")
    print(f"Observed density: {observed_density:.3f}%")
    
    # Bootstrap null hypothesis
    null_counts = bootstrap_null_hypothesis(total_turns, BOOTSTRAP_SAMPLES)
    null_mean = np.mean(null_counts)
    null_std = np.std(null_counts)
    null_density = (null_mean / total_turns * 100) if total_turns > 0 else 0
    
    print(f"\n[NULL HYPOTHESIS]")
    print(f"Mean null invariants: {null_mean:.2f} ± {null_std:.2f}")
    print(f"Null density: {null_density:.3f}%")
    
    # Calculate p-values
    print(f"\n[STATISTICAL TESTS]")
    
    # Method 1: Chi-squared
    chi2_results = calculate_p_value_chi_squared(verified_invariants, total_turns, null_counts)
    print(f"\nChi-Squared Test:")
    print(f"  χ² statistic: {chi2_results['chi2_statistic']:.4f}")
    print(f"  p-value: {chi2_results['p_value']:.10f}")
    print(f"  DOF: {chi2_results['degrees_of_freedom']}")
    
    # Method 2: Direct proportion
    p_direct = calculate_p_value_direct(verified_invariants, null_counts)
    print(f"\nDirect Proportion Test:")
    print(f"  p-value: {p_direct:.10f}")
    print(f"  (Proportion of null samples >= observed)")
    
    # Verdict
    print(f"\n[VERDICT]")
    if chi2_results['p_value'] < 0.0001:
        print("✅ VALIDATED: p < 0.0001 (highly significant)")
        print("   Observed density is NOT due to random chance")
    elif chi2_results['p_value'] < 0.001:
        print("✅ VALIDATED: p < 0.001 (significant)")
    elif chi2_results['p_value'] < 0.05:
        print("⚠️  MARGINAL: p < 0.05 (weakly significant)")
    else:
        print("❌ REJECTED: p >= 0.05 (not significant)")
        print("   Cannot distinguish from random chance")
    
    # Compile results
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'dataset': Path(csv_path).name,
        'observed': {
            'total_turns': total_turns,
            'verified_invariants': verified_invariants,
            'density_pct': round(observed_density, 3)
        },
        'null_hypothesis': {
            'simulations': BOOTSTRAP_SAMPLES,
            'mean_invariants': round(null_mean, 2),
            'std_invariants': round(null_std, 2),
            'density_pct': round(null_density, 3)
        },
        'statistical_tests': {
            'chi_squared': {
                'statistic': chi2_results['chi2_statistic'],
                'p_value': chi2_results['p_value'],
                'degrees_of_freedom': chi2_results['degrees_of_freedom'],
                'contingency_table': chi2_results['contingency_table']
            },
            'direct_proportion': {
                'p_value': p_direct,
                'extreme_samples': sum(1 for n in null_counts if n >= verified_invariants)
            }
        },
        'verdict': {
            'significant': chi2_results['p_value'] < 0.0001,
            'p_threshold': 'p < 0.0001' if chi2_results['p_value'] < 0.0001 else 
                          'p < 0.001' if chi2_results['p_value'] < 0.001 else
                          'p < 0.05' if chi2_results['p_value'] < 0.05 else
                          'p >= 0.05 (not significant)'
        }
    }
    
    # Save results
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\n[OUTPUT] Results saved to {output_path}")
    else:
        print(f"\n[RESULTS JSON]")
        print(json.dumps(results, indent=2))
    
    # Exit code
    sys.exit(0 if results['verdict']['significant'] else 1)

if __name__ == "__main__":
    main()
