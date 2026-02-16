"""
GTA Handling.meta Processing Example

Demonstrates:
- Parsing handling.meta files
- Extracting vehicle data
- Applying value clamps
- Generating reports
"""

import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.scaffold.handling_pipeline import (
    HandlingMetaParser,
    HandlingClampPipeline,
    create_sample_handling_meta,
)
from toolkit.oe.scaffold.logger import ScaffoldLogger


def main():
    """Run handling.meta processing example."""
    print("=" * 60)
    print("GTA Handling.meta Processing Example")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create logger
        logger = ScaffoldLogger(temp_path / "handling_example.jsonl")
        logger.log_start("handling_example")
        
        # Create sample handling.meta
        print("\n1. Creating Sample handling.meta")
        print("-" * 40)
        
        handling_file = temp_path / "handling.meta"
        create_sample_handling_meta(handling_file)
        
        print(f"Sample file created: {handling_file.name}")
        print(f"File size: {handling_file.stat().st_size} bytes")
        
        logger.log_info("sample_created", file=str(handling_file))
        
        # Parse handling.meta
        print("\n2. Parsing handling.meta")
        print("-" * 40)
        
        parser = HandlingMetaParser(logger)
        items = parser.parse_file(handling_file)
        
        print(f"Handling items found: {len(items)}")
        
        vehicle_names = parser.get_vehicle_names()
        print("\nVehicles:")
        for name in vehicle_names:
            print(f"  - {name}")
        
        # Show sample item data
        if items:
            sample = items[0]
            print(f"\nSample data for {sample.name}:")
            for key, value in list(sample.data.items())[:5]:
                print(f"  {key}: {value}")
            if len(sample.data) > 5:
                print(f"  ... and {len(sample.data) - 5} more fields")
        
        logger.log_info("parsing_complete", items_found=len(items))
        
        # Apply clamp pipeline
        print("\n3. Running Clamp Pipeline (Dry-run)")
        print("-" * 40)
        
        pipeline = HandlingClampPipeline(logger)
        results = pipeline.clamp_all(items, apply=False)
        
        # Count violations
        total_violations = sum(len(r["violations"]) for r in results)
        print(f"Total violations found: {total_violations}")
        
        # Show violations
        if total_violations > 0:
            print("\nViolations by vehicle:")
            for result in results:
                if result["violations"]:
                    print(f"\n  {result['vehicle']}:")
                    for v in result["violations"]:
                        print(f"    {v['field']}: {v['original']} → {v['clamped']}")
                        print(f"      (valid range: {v['min']} - {v['max']})")
        else:
            print("\n✓ No violations found - all values within acceptable ranges")
        
        logger.log_info("clamp_complete", 
                       violations=total_violations,
                       dry_run=True)
        
        # Save report
        print("\n4. Generating Report")
        print("-" * 40)
        
        import json
        report_file = temp_path / "clamp_report.json"
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Report saved: {report_file.name}")
        print(f"Report size: {report_file.stat().st_size} bytes")
        
        logger.log_complete("handling_example", 
                          items_processed=len(items),
                          violations=total_violations)
        
        print("\n" + "=" * 60)
        print("Handling processing completed successfully!")
        print("=" * 60)
        print("\nNote: Use --apply flag to actually modify handling values")


if __name__ == "__main__":
    main()
