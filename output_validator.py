import pandas as pd
from PIPELINE_LOGGER import logging, safe_print

def validate_output():
    logging.info("Validating output...")
    df = pd.read_csv("refined_inventory.csv")
    
    if "verified_invariant" in df.columns:
        density = df["verified_invariant"].mean()
        logging.info(f"Invariant Density: {density:.2%}")
        safe_print(f"Invariant Density: {density:.2%}")
    else:
        logging.error("Column 'verified_invariant' missing from CSV.")
        safe_print("Column 'verified_invariant' missing from CSV.")

validate_output()
