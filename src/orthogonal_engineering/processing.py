from pathlib import Path
import json


def process_files(data_path: Path):
    records = []
    for file in data_path.rglob("*"):
        if file.suffix.lower() in [".json", ".jsonl"]:
            with open(file, "r", encoding="utf-8") as f:
                if file.suffix.lower() == ".jsonl":
                    for line in f:
                        records.append(json.loads(line))
                else:
                    records.append(json.load(f))
    return records
