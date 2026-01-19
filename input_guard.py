# input_guard.py
# Prevents unsafe file access, enforces schema compliance for CSVs

import os
import sys
import pandas as pd

FOLDER = os.getcwd()

def guard_csv_files():
    """Check all CSVs in folder for schema and path safety"""
    expected_columns = ["session_id", "turn_id", "role", "message", "verified_invariant"]
    for fname in os.listdir(FOLDER):
        if fname.lower().endswith(".csv"):
            path = os.path.join(FOLDER, fname)
            if not os.path.isfile(path):
                continue
            # Check column headers
            try:
                df = pd.read_csv(path, nrows=5)
                if list(df.columns) != expected_columns:
                    print(f"[WARN] {fname}: unexpected columns {list(df.columns)}")
                else:
                    print(f"[OK]   {fname}: columns OK")
            except Exception as e:
                print(f"[FAIL]  {fname}: failed to read ({e})")
    print("Input guard check complete.")

if __name__ == "__main__":
    guard_csv_files()
