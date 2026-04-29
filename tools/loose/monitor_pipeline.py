"""Monitor Pipeline - Monitor Pipeline"""
import os
from PIPELINE_LOGGER import logging, safe_print

def monitor():
    current_dir = os.getcwd()
    logging.info(f"Monitoring Substrate: {current_dir}")
    safe_print(f"Monitoring Substrate: {current_dir}")
    
    for f in ["canal_refiner.py", "refined_inventory.csv"]:
        status = "EXISTS" if os.path.exists(f) else "MISSING"
        logging.info(f"{f}: {status}")
        safe_print(f"{f}: {status}")

monitor()
