"""Validate Input - Validate Input"""
import pandas as pd
import os
from PIPELINE_LOGGER import logging, safe_print

def validate():
    file = "refined_inventory.csv"
    logging.info(f"Validating {file}...")
    
    if not os.path.exists(file): 
        logging.error(f"{file} not found.")
        safe_print(f"FAILED: {file} not found.")
        return
    
    df = pd.read_csv(file)
    logging.info(f"{file} is valid. Rows: {len(df)}")
    safe_print(f"SUCCESS: {file} is valid. Rows: {len(df)}")

validate()
