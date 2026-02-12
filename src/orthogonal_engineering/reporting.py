import json


def generate_report(hashed_records, output_path):
    report_data = {
        "total_records": len(hashed_records),
        "records": hashed_records,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    return report_data
