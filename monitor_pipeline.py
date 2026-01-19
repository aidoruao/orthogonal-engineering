import os
def monitor():
    # We use '.' to mean "wherever I am right now"
    current_dir = os.getcwd()
    print(f"Monitoring Substrate: {current_dir}")
    for f in ["canal_refiner.py", "refined_inventory.csv"]:
        status = "EXISTS" if os.path.exists(f) else "MISSING"
        print(f"{f}: {status}")
monitor()
