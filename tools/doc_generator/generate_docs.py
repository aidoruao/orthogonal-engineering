#!/usr/bin/env python3
"""Main entry point for self-generating documentation pipeline.

Usage:
    python tools/doc_generator/generate_docs.py [--all|--domains|--axioms|--drift]

Generates:
    - docs/auto/GENERATED_DOMAINS.md
    - docs/auto/GENERATED_AXIOMS.md
    - docs/auto/DRIFT_REPORT.md
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.doc_generator.domain_summarizer import DomainSummarizer
from tools.doc_generator.axiom_indexer import AxiomIndexer
from tools.doc_generator.drift_detector import DriftDetector


def main():
    parser = argparse.ArgumentParser(description="Generate documentation from code")
    parser.add_argument("--all", action="store_true", help="Generate all documentation")
    parser.add_argument("--domains", action="store_true", help="Generate domain docs")
    parser.add_argument("--axioms", action="store_true", help="Generate axiom index")
    parser.add_argument("--drift", action="store_true", help="Check for drift")
    parser.add_argument("--output-dir", default="docs/auto", help="Output directory")
    args = parser.parse_args()
    
    # Default to --all if no specific flags
    if not any([args.all, args.domains, args.axioms, args.drift]):
        args.all = True
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated = []
    
    if args.all or args.domains:
        print("Generating domain documentation...")
        summarizer = DomainSummarizer()
        summarizer.analyze_all()
        
        md_path = output_dir / "GENERATED_DOMAINS.md"
        md_path.write_text(summarizer.generate_markdown())
        generated.append(str(md_path))
        
        json_path = output_dir / "GENERATED_DOMAINS.json"
        import json
        json_path.write_text(json.dumps(summarizer.generate_json(), indent=2))
        generated.append(str(json_path))
        
        print(f"  ✓ {md_path}")
        print(f"  ✓ {json_path}")
    
    if args.all or args.axioms:
        print("Generating axiom index...")
        indexer = AxiomIndexer()
        indexer.index_axioms()
        
        md_path = output_dir / "GENERATED_AXIOMS.md"
        md_path.write_text(indexer.generate_markdown())
        generated.append(str(md_path))
        
        print(f"  ✓ {md_path}")
    
    if args.all or args.drift:
        print("Checking for documentation drift...")
        detector = DriftDetector()
        detector.run_all_checks()
        
        md_path = output_dir / "DRIFT_REPORT.md"
        md_path.write_text(detector.generate_report())
        generated.append(str(md_path))
        
        print(f"  ✓ {md_path}")
        
        if detector.reports:
            print(f"\n⚠️  Found {len(detector.reports)} drift issues")
            for r in detector.reports:
                print(f"  - {r.category}: {r.drift:+d} (severity: {r.severity})")
    
    print(f"\nGenerated {len(generated)} files in {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
