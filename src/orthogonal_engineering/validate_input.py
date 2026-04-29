"""Validate Input - Validate Input"""
import pandas as pd
import os
from .PIPELINE_LOGGER import logging, safe_print

def validate(file="refined_inventory.csv"):
    logging.info(f"Validating {file}...")
    
    if not os.path.exists(file): 
        logging.error(f"{file} not found.")
        safe_print(f"FAILED: {file} not found.")
        return False
    
    df = pd.read_csv(file)
    logging.info(f"{file} is valid. Rows: {len(df)}")
    safe_print(f"SUCCESS: {file} is valid. Rows: {len(df)}")
    return True


def validate_input_schema(file="refined_inventory.csv"):
    """Curated API entry point for input schema validation."""
    # TODO: Expand validate_input_schema() - stub detected by Yeshua Agent
    return validate(file)


if __name__ == "__main__":
    validate()
