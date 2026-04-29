"""Output Validator - Output Validator"""
import pandas as pd
from .PIPELINE_LOGGER import logging, safe_print

def validate_output(csv_path="refined_inventory.csv"):
    logging.info("Validating output...")
    df = pd.read_csv(csv_path)
    
    if "verified_invariant" in df.columns:
        density = df["verified_invariant"].mean()
        logging.info(f"Invariant Density: {density:.2%}")
        safe_print(f"Invariant Density: {density:.2%}")
        return density
    else:
        logging.error("Column 'verified_invariant' missing from CSV.")
        safe_print("Column 'verified_invariant' missing from CSV.")
        return None


if __name__ == "__main__":
    validate_output()
