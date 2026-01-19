import shutil
import os
from datetime import datetime
def backup():
    target = "refined_inventory.csv"
    if os.path.exists(target):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(target, f"backup_{stamp}_{target}")
        print(f"BACKUP CREATED: backup_{stamp}_{target}")
backup()
