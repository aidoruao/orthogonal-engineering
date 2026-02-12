from pathlib import Path
from .processing import process_files
from .validation import validate_records
from .hashing import hash_records
from .reporting import generate_report


def run_full_audit(data_path: Path, output_path: Path):
    records = process_files(data_path)
    validated = validate_records(records)
    hashed = hash_records(validated)
    report = generate_report(hashed, output_path)
    return report
