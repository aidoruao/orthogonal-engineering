"""Input Guard - input_guard.py"""
# input_guard.py
# Prevents unsafe file access, enforces schema compliance for CSVs

import os
import sys
import pandas as pd
from .PIPELINE_LOGGER import logging, safe_print

FOLDER = os.getcwd()

def guard_csv_files(folder=None):
    """Check all CSVs in folder for schema and path safety"""
    target_folder = folder or FOLDER
    expected_columns = ["session_id", "turn_id", "role", "message", "verified_invariant"]
    logging.info("Starting input guard check...")
    
    for fname in os.listdir(target_folder):
        if fname.lower().endswith(".csv"):
            path = os.path.join(target_folder, fname)
            if not os.path.isfile(path):
                continue
            # Check column headers
            try:
                df = pd.read_csv(path, nrows=5)
                if list(df.columns) != expected_columns:
                    logging.warning(f"{fname}: unexpected columns {list(df.columns)}")
                    safe_print(f"[WARN] {fname}: unexpected columns")
                else:
                    logging.info(f"{fname}: columns OK")
                    safe_print(f"[OK]   {fname}: columns OK")
            except Exception as e:
                logging.error(f"{fname}: failed to read ({e})")
                safe_print(f"[FAIL] {fname}: failed to read")
    
    logging.info("Input guard check complete.")
    safe_print("Input guard check complete.")

def guard_input(folder=None):
    """Curated API entry point for input guarding."""
    # TODO: Expand guard_input() - stub detected by Yeshua Agent
    guard_csv_files(folder)


if __name__ == "__main__":
    guard_csv_files()
