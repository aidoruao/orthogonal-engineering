import shutil
import os
from datetime import datetime
from .PIPELINE_LOGGER import logging, safe_print

def backup(target="refined_inventory.csv"):
    if os.path.exists(target):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{stamp}_{target}"
        shutil.copy(target, backup_name)
        logging.info(f"Backup created: {backup_name}")
        safe_print(f"BACKUP CREATED: {backup_name}")
        return backup_name
    else:
        logging.warning(f"{target} does not exist, no backup created")
        safe_print(f"[WARN] {target} not found, no backup created")
        return None


def rollback_transaction(target="refined_inventory.csv"):
    """Curated API entry point for rollback/backup."""
    return backup(target)


if __name__ == "__main__":
    backup()
