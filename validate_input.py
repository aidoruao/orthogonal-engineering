import pandas as pd
import os
def validate():
    file = "refined_inventory.csv"
    if not os.path.exists(file): 
        print(f"FAILED: {file} not found."); return
    df = pd.read_csv(file)
    print(f"SUCCESS: {file} is valid. Rows: {len(df)}")
validate()
